"""
Tiny relay server for the Secure Voice project.
Forwards bytes between two registered devices identified by phone number.

Protocol (line-based ASCII, terminated with \n, until GO):
  Client  ->  REG <phone>           Register
  Server  <-  OK  or  ERR <reason>

  Client  ->  CALL <peer_phone>     Initiate call
  Server  <-  RING                  ...calling, peer is ringing
  Server  <-  ERR unavail           ...peer not available

  Server  ->  INC <caller_phone>    (unsolicited) someone is calling you
  Client  ->  ANS                   Pick up
  Server  <-  GO                    Both ends in audio mode

  Client  ->  HUP                   End call
  Server  ->  PEER_HUP              Peer ended call
  Server  ->  PEER_GONE             Peer disconnected

After GO, every byte is forwarded transparently to the peer.
"""

import asyncio


CLIENTS = {}   # phone_number -> Session


class Session:
    def __init__(self, r, w):
        self.r = r
        self.w = w
        self.phone = None
        self.peer = None
        self.state = "IDLE"   # IDLE -> REGD -> (CALLING|RINGING) -> TALK
        self.kick = asyncio.Event()

    async def send(self, line):
        self.w.write((line + "\n").encode())
        await self.w.drain()


async def handle_command(s, line):
    if not line.upper().startswith("PING"):
        print(f"  << {s.phone or '?'}: {line!r}")
    parts = line.split(maxsplit=1)
    if not parts:
        return
    verb = parts[0].upper()
    arg = parts[1] if len(parts) > 1 else None

    if verb == "REG" and s.state == "IDLE":
        if not arg:
            return await s.send("ERR no_phone")
        if arg in CLIENTS:
            return await s.send("ERR taken")
        s.phone = arg
        s.state = "REGD"
        CLIENTS[arg] = s
        await s.send("OK")
        print(f"+ registered {arg}")

    elif verb == "CALL" and s.state == "REGD":
        peer = CLIENTS.get(arg)
        if not peer or peer.state != "REGD":
            return await s.send("ERR unavail")
        s.peer = peer
        peer.peer = s
        s.state = "CALLING"
        peer.state = "RINGING"
        await s.send("RING")
        await peer.send(f"INC {s.phone}")
        peer.kick.set()
        print(f"  ring: {s.phone} -> {peer.phone}")

    elif verb == "ANS" and s.state == "RINGING":
        s.state = "TALK"
        s.peer.state = "TALK"
        await s.send("GO")
        await s.peer.send("GO")
        s.peer.kick.set()
        print(f"  TALK: {s.phone} <-> {s.peer.phone}")

    elif verb == "HUP":
        if s.peer:
            await s.peer.send("PEER_HUP")
            s.peer.peer = None
            s.peer.state = "REGD"
            s.peer.kick.set()
        s.peer = None
        s.state = "REGD"
        await s.send("OK")
        print(f"  hup: {s.phone}")

    elif verb in ("DBG", "PING"):
        # debug/heartbeat lines — silently accept, no reply
        # (replying with ERR would put 'ERR ' in the device's RX buffer and
        # falsely trigger its state machine)
        pass

    else:
        await s.send(f"ERR {verb}_in_{s.state}")


async def setup_phase(s):
    # Stay in line-parsing mode while not in TALK. Once TALK, exit so we
    # can switch to byte-forwarding for audio.
    while s.state not in ("TALK", "GONE"):
        rt = asyncio.create_task(s.r.readline())
        kt = asyncio.create_task(s.kick.wait())
        done, pending = await asyncio.wait(
            [rt, kt], return_when=asyncio.FIRST_COMPLETED)
        for p in pending:
            p.cancel()
            try:
                await p
            except (asyncio.CancelledError, Exception):
                pass

        if kt in done:
            s.kick.clear()
            continue

        line = rt.result()
        if not line:
            s.state = "GONE"
            return
        await handle_command(s, line.decode(errors="replace").strip())


async def talk_phase(s):
    while s.state == "TALK" and s.peer and s.peer.state == "TALK":
        try:
            data = await s.r.read(256)
        except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
            break
        if not data:
            break
        peer = s.peer            # snapshot in case peer disappears mid-write
        if peer is None or peer.state != "TALK":
            break
        try:
            peer.w.write(data)
            await peer.w.drain()
        except (ConnectionResetError, BrokenPipeError, AttributeError):
            break


async def handle(r, w):
    s = Session(r, w)
    addr = w.get_extra_info("peername")
    print(f"+ conn {addr}")
    try:
        await setup_phase(s)
        if s.state == "TALK":
            # Phase 6.2: byte-forward audio peer-to-peer transparently.
            # Hangup during the call = device closes its TCP socket; the EOF
            # exits talk_phase and the finally block notifies the peer.
            await talk_phase(s)
    finally:
        print(f"- disc {s.phone or addr}")
        if s.phone in CLIENTS:
            del CLIENTS[s.phone]
        if s.peer:
            try:
                s.peer.w.write(b"PEER_GONE\n")
                await s.peer.w.drain()
            except Exception:
                pass
            s.peer.peer = None
            s.peer.state = "REGD"
            s.peer.kick.set()
        try:
            w.close()
            await w.wait_closed()
        except Exception:
            pass


async def main():
    srv = await asyncio.start_server(handle, "0.0.0.0", 5555)
    addr = srv.sockets[0].getsockname()
    print(f"relay listening on {addr}")
    print("Ctrl+C to quit.\n")
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nbye")