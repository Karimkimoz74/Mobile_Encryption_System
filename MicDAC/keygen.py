#!/usr/bin/env python3
"""
Secure Voice - AES-128 session-key generator (Phase 7).  Pure standard library.

Run ONCE on your PC:
    python keygen.py

It writes  Core/Inc/crypto_keys.h  with a random 16-byte AES key.
That file is IDENTICAL on both boards (only device_config.h differs between
them).  Do NOT re-run this between builds unless you re-flash BOTH boards -
otherwise the two devices hold different keys and cannot decrypt each other.
"""
import os
import secrets

key = secrets.token_bytes(16)

here = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(here, "Core", "Inc", "crypto_keys.h")

if os.path.exists(out_path):
    print("crypto_keys.h ALREADY EXISTS - refusing to overwrite it.")
    print("Both boards MUST be built from ONE identical key. Regenerating it")
    print("here would desync any board (including a teammate's) not re-flashed")
    print("afterwards. To deploy: COPY this exact crypto_keys.h to the other")
    print("build machine - do NOT run keygen there.")
    print("Only to deliberately mint a NEW key: delete crypto_keys.h first,")
    print("then re-flash BOTH boards from the new file.")
    raise SystemExit(1)

row = "  " + ", ".join(f"0x{b:02X}" for b in key)

with open(out_path, "w") as f:
    f.write("#ifndef CRYPTO_KEYS_H\n#define CRYPTO_KEYS_H\n")
    f.write("#include <stdint.h>\n")
    f.write('#include "device_config.h"   /* IS_DEVICE_A - per-board switch */\n\n')
    f.write("/* Pre-shared AES-128 session key, generated offline by keygen.py.\n")
    f.write("   IDENTICAL on both boards. If you regenerate it, re-flash BOTH. */\n")
    f.write(f"static const uint8_t AES_SESSION_KEY[16] = {{\n{row}\n}};\n\n")
    f.write("#endif /* CRYPTO_KEYS_H */\n")

print("wrote", out_path)
print("AES-128 key =", key.hex())