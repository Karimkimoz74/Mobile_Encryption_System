"""
Tiny relay server for the Secure Voice project.
Forwards bytes between two registered devices identified by phone number.

Protocol (line-based ASCII, terminated with \n, until GO):
  Client  ->  REG <phone>          Register
  Client  ->  CALL <peer_phone>    Initiate call
  Server  ->  INC <caller_phone>   someone is calling you
  Client  ->  ANS                  Pick up
  Server  ->  GO                   Both ends in audio mode
  Client  ->  HUP / socket close   End call

After GO every byte is forwarded transparently to the peer. In Phase 7 those
bytes are AES-128-CTR encrypted audio (pre-shared key, no key exchange).

=== DEBUG BUILD ===
This relay is instrumented to PROVE the audio is encrypted:
  * loads the pre-shared AES key from crypto_keys.h
  * measures the entropy of each direction's stream (~8.0 bits/byte = random)
  * decrypts the stream with the key and writes it to a .wav file you can
    play back -- if it sounds like the conversation, the link was encrypted
  * prints "X silent for Ns" every 5 s if a side stalls
Forwarding behaviour is unchanged; all debug code is observation-only.
"""

import asyncio
import math
import os
import re
import struct
import time


CLIENTS = {}          # phone_number -> Session
AUDIO_WINDOW = 4096    # bytes per entropy report (~0.5 s of 8 kHz audio)
SAMPLE_RATE = 8000     # firmware audio: 8 kHz, 8-bit unsigned PCM

AES_RK = None          # expanded AES round keys, or None if key not loaded


def ts():
    return time.strftime("%H:%M:%S")


# --------------------------------------------------------------------------
# AES-128 (encrypt core) — mirrors crypto.c, used to decrypt the audio stream
# --------------------------------------------------------------------------
SBOX = bytes.fromhex(
 "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
 "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
 "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
 "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
 "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
 "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
 "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
 "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")


def _xtime(x):
    return ((x << 1) ^ ((x >> 7) * 0x1b)) & 0xFF


def aes_key_expand(key):
    rk = list(key)
    rcon = 1
    i = 16
    while i < 176:
        t = rk[i - 4:i]
        if i % 16 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[x] for x in t]
            t[0] ^= rcon
            rcon = ((rcon << 1) ^ ((rcon >> 7) * 0x1b)) & 0xFF
        for j in range(4):
            rk.append(rk[i - 16 + j] ^ t[j])
        i += 4
    return rk


def aes_encrypt_block(s, rk):
    s = list(s)
    for i in range(16):
        s[i] ^= rk[i]
    for rnd in range(1, 11):
        for i in range(16):
            s[i] = SBOX[s[i]]
        s[1], s[5], s[9], s[13] = s[5], s[9], s[13], s[1]
        s[2], s[10] = s[10], s[2]
        s[6], s[14] = s[14], s[6]
        s[3], s[7], s[11], s[15] = s[15], s[3], s[7], s[11]
        if rnd != 10:
            for c in range(0, 16, 4):
                a0, a1, a2, a3 = s[c], s[c + 1], s[c + 2], s[c + 3]
                s[c]     = _xtime(a0) ^ (_xtime(a1) ^ a1) ^ a2 ^ a3
                s[c + 1] = a0 ^ _xtime(a1) ^ (_xtime(a2) ^ a2) ^ a3
                s[c + 2] = a0 ^ a1 ^ _xtime(a2) ^ (_xtime(a3) ^ a3)
                s[c + 3] = (_xtime(a0) ^ a0) ^ a1 ^ a2 ^ _xtime(a3)
        for i in range(16):
            s[i] ^= rk[rnd * 16 + i]
    return bytes(s)


def ctr_crypt(data, counter):
    """AES-CTR over a 16-byte-aligned buffer. Returns plaintext bytes."""
    out = bytearray()
    for off in range(0, len(data), 16):
        ks = bytearray(16)
        ks[12] = (counter >> 24) & 0xFF
        ks[13] = (counter >> 16) & 0xFF
        ks[14] = (counter >> 8) & 0xFF
        ks[15] = counter & 0xFF
        ks = aes_encrypt_block(ks, AES_RK)
        for i in range(16):
            out.append(data[off + i] ^ ks[i])
        counter = (counter + 1) & 0xFFFFFFFF
    return bytes(out)


def load_aes_key():
    """Parse AES_SESSION_KEY[16] from crypto_keys.h so the relay can decrypt."""
    global AES_RK
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(
        os.path.join(here, "..", "MicDAC", "Core", "Inc", "crypto_keys.h"))
    try:
        text = open(path).read()
    except OSError:
        print(f"[debug] crypto_keys.h not found ({path})")
        print("[debug] audio decryption disabled; entropy still measured.")
        return
    m = re.search(r"AES_SESSION_KEY\[16\]\s*=\s*\{(.*?)\}", text, re.S)
    if not m:
        print("[debug] AES_SESSION_KEY not found in crypto_keys.h")
        return
    key = bytes(int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", m.group(1)))
    if len(key) != 16:
        print(f"[debug] AES key has {len(key)} bytes, expected 16")
        return
    AES_RK = aes_key_expand(key)
    print(f"[debug] AES-128 key loaded from {path}")
    print(f"[debug] key = {key.hex()}")
    print(f"[debug] key fingerprint = {key_fingerprint()}  "
          f"(both boards must report this)")
    print("[debug] audio streams will be decrypted to .wav for verification.")


def key_fingerprint():
    """8-hex fingerprint of the loaded key: first 4 bytes of AES(key, zero
    block). Mirrors crypto.c's crypto_key_fingerprint()."""
    if AES_RK is None:
        return None
    return aes_encrypt_block(bytes(16), AES_RK)[:4].hex().upper()


def shannon_entropy(data):
    """Bits-per-byte. ~8.0 = uniformly random (encrypted); low = plaintext."""
    if not data:
        return 0.0
    freq = [0] * 256
    for x in data:
        freq[x] += 1
    n = len(data)
    h = 0.0
    for f in freq:
        if f:
            p = f / n
            h -= p * math.log2(p)
    return h


def wav_header(data_len):
    return (b"RIFF" + struct.pack("<I", 36 + data_len) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1,
                                    SAMPLE_RATE, SAMPLE_RATE, 1, 8)
            + b"data" + struct.pack("<I", data_len))


class CallSniffer:
    """Observes one device's outbound (encrypted) audio stream: measures its
    entropy, decrypts it with the shared key, and saves the result to a .wav."""

    def __init__(self, who):
        self.who = who
        # device A's phone ends in 1 (CTR base 0); device B ends in 2 (2^31).
        self.counter0 = 0x00000000 if who.strip().endswith("1") else 0x80000000
        self.cipher = bytearray()       # whole call captured; processed at end
        self.next_report = 32768        # next cipher length at which to log

    def feed(self, data):
        # HOT PATH — keep light so byte-forwarding is never delayed.
        if len(self.cipher) < 6_000_000:        # ~12 min cap, protects RAM
            self.cipher += data
        # Every ~32 KB (~4 s of audio) print a live encryption/decryption line.
        if len(self.cipher) >= self.next_report:
            self.next_report += 32768
            self._live_report()

    def _live_report(self):
        """Show, live during the call, that the stream is encrypted (random)
        and that it decrypts back to real audio with the shared key."""
        try:
            n = len(self.cipher)
            start = (n - 4096) & ~15            # 16-byte-aligned window start
            win = bytes(self.cipher[start:start + 4096])
            ch = shannon_entropy(win)
            msg = (f"{ts()}  [AUD] {self.who}: {n // 1024} KB | encrypted "
                   f"entropy {ch:.2f}/8.00 (random)")
            if AES_RK is not None:
                ctr = (self.counter0 + start // 16) & 0xFFFFFFFF
                ph = shannon_entropy(ctr_crypt(win, ctr))
                ok = ph < ch - 0.4
                msg += (f"  ->  decrypts to {ph:.2f} "
                        f"({'AUDIO ok' if ok else 'KEY MISMATCH'})")
            print(msg)
        except Exception as e:
            print(f"  [debug] live report error: {e}")

    def summary(self):
        """Call ended — do the heavy work now, OFF the forwarding path: save the
        on-the-wire ciphertext and the AES-decrypted audio, each as a .wav."""
        n = len(self.cipher)
        print(f"{ts()}  [SUM] {self.who}: {n} bytes forwarded")
        if n < 16:
            return
        cipher = bytes(self.cipher)
        stamp = time.strftime("%H%M%S")

        # control lines that leaked into the audio stream (diagnostic only)
        for m in re.finditer(rb"DBG [A-Z][\x20-\x7e]{0,27}", cipher):
            print(f"{ts()}  [CTL] {self.who}: "
                  f"{m.group().decode('ascii', 'replace')!r}")

        # 1) raw on-the-wire ciphertext  ->  plays as noise
        ch = shannon_entropy(cipher[:AUDIO_WINDOW])
        enc_name = f"encrypted_{self.who}_{stamp}.wav"
        try:
            with open(enc_name, "wb") as f:
                f.write(wav_header(n))
                f.write(cipher)
            print(f"{ts()}  [REC] {self.who}: ENCRYPTED {n} B -> {enc_name}  "
                  f"(entropy {ch:.2f}/8.00 — plays as noise)")
        except Exception as e:
            print(f"  [debug] encrypted wav error: {e}")

        # 2) AES-decrypted audio  ->  plays as voice
        if AES_RK is None:
            print(f"  [debug] no key loaded — cannot decrypt")
            return
        try:
            m2 = n - (n % 16)
            plain = ctr_crypt(cipher[:m2], self.counter0)
            ph = shannon_entropy(plain[:AUDIO_WINDOW])
            dec_name = f"decrypted_{self.who}_{stamp}.wav"
            with open(dec_name, "wb") as f:
                f.write(wav_header(len(plain)))
                f.write(plain)
            ok = ph < ch - 0.4
            print(f"{ts()}  [REC] {self.who}: DECRYPTED -> {dec_name}  "
                  f"(entropy {ph:.2f} — "
                  f"{'decrypts to real audio' if ok else 'decrypt FAILED (key/desync)'})")
        except Exception as e:
            print(f"  [debug] decrypted wav error: {e}")


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
    parts = line.split(maxsplit=1)
    if not parts:
        return
    verb = parts[0].upper()
    arg = parts[1] if len(parts) > 1 else None
    # The relay's public port attracts a lot of internet-scanner junk. Only
    # log lines from an already-registered device, or a REG itself — this
    # keeps the call log readable instead of drowning in probe garbage.
    if verb != "PING" and (s.phone or verb == "REG"):
        print(f"{ts()}  << {s.phone or '?'}: {line!r}")

    if verb == "REG" and s.state == "IDLE":
        if not arg:
            return await s.send("ERR no_phone")
        if arg in CLIENTS:
            return await s.send("ERR taken")
        s.phone = arg
        s.state = "REGD"
        CLIENTS[arg] = s
        await s.send("OK")
        print(f"{ts()}  + registered {arg}")

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
        print(f"{ts()}  ring: {s.phone} -> {peer.phone}")

    elif verb == "ANS" and s.state == "RINGING":
        s.state = "TALK"
        s.peer.state = "TALK"
        await s.send("GO")
        await s.peer.send("GO")
        s.peer.kick.set()
        print(f"{ts()}  TALK: {s.phone} <-> {s.peer.phone}")

    elif verb == "HUP":
        if s.peer:
            await s.peer.send("PEER_HUP")
            s.peer.peer = None
            s.peer.state = "REGD"
            s.peer.kick.set()
        s.peer = None
        s.state = "REGD"
        await s.send("OK")
        print(f"{ts()}  hup: {s.phone}")

    elif verb == "DBG":
        # A board announces its AES key fingerprint just after registering.
        if arg and arg.startswith("KEYFP="):
            got = arg[6:].strip().upper()
            want = key_fingerprint()
            if want is None:
                print(f"  [KEY] {s.phone}: fingerprint {got} "
                      f"(relay has no key file to compare against)")
            elif got == want:
                print(f"  [KEY] {s.phone}: key {got} -- MATCHES the shared key")
            else:
                print(f"  [KEY] {s.phone}: key {got} != expected {want}")
                print(f"        *** WRONG KEY ON THIS BOARD - RE-FLASH IT ***")
        # other DBG lines: silently accept, no reply

    elif verb == "PING":
        # heartbeat — silently accept, no reply
        pass

    else:
        await s.send(f"ERR {verb}_in_{s.state}")


async def setup_phase(s):
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
    sniff = CallSniffer(s.phone)
    peerphone = s.peer.phone if s.peer else "?"
    print(f"{ts()}  --- audio path open: {s.phone} -> {peerphone} ---")
    idle = 0
    while s.state == "TALK" and s.peer and s.peer.state == "TALK":
        try:
            data = await asyncio.wait_for(s.r.read(256), timeout=5.0)
        except asyncio.TimeoutError:
            idle += 5
            print(f"{ts()}  [...] {s.phone} silent for {idle}s")
            continue
        except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
            break
        if not data:
            print(f"{ts()}  [END] {s.phone} closed its socket — call ended "
                  f"(hangup / lost link)")
            break
        peer = s.peer
        if peer is None or peer.state != "TALK":
            break
        try:
            peer.w.write(data)
            await peer.w.drain()
        except (ConnectionResetError, BrokenPipeError, AttributeError):
            break
        idle = 0
        sniff.feed(data)         # observation only — never affects forwarding
    sniff.summary()


async def handle(r, w):
    s = Session(r, w)
    try:
        await setup_phase(s)
        if s.state == "TALK":
            await talk_phase(s)
    finally:
        if s.phone:
            print(f"{ts()}  - disc {s.phone}")
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
    load_aes_key()
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