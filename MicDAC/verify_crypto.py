#!/usr/bin/env python3
"""Faithful Python port of crypto.c's bignum + AES, to verify correctness.
Mirrors the C arithmetic exactly (32-bit limbs, 64-bit intermediates)."""
import re

M32 = 0xFFFFFFFF
M64 = 0xFFFFFFFFFFFFFFFF
LIMBS = 16

# ---- load the real keys from crypto_keys.h ----
t = open("Core/Inc/crypto_keys.h").read()
def keyint(name):
    m = re.search(name + r"\[64\] = \{(.*?)\}", t, re.S)
    b = [int(x, 16) for x in re.findall(r"0x[0-9A-Fa-f]+", m.group(1))]
    return int.from_bytes(bytes(b), "big")

# ---- bignum, mirroring crypto.c ----
def bytes_to_bn(b):           # b: 64 bytes big-endian -> 16 limbs little-endian
    return [int.from_bytes(b[(LIMBS-1-i)*4:(LIMBS-1-i)*4+4], "big") for i in range(LIMBS)]

def bn_to_int(bn):
    return sum(bn[i] << (32*i) for i in range(LIMBS))

def bn_cmp(a, b):
    for i in range(LIMBS-1, -1, -1):
        if a[i] < b[i]: return -1
        if a[i] > b[i]: return 1
    return 0

def bn_add(a, b):
    r = [0]*LIMBS; carry = 0
    for i in range(LIMBS):
        s = a[i] + b[i] + carry
        r[i] = s & M32; carry = s >> 32
    return r, carry

def bn_sub(a, b):
    r = [0]*LIMBS; borrow = 0
    for i in range(LIMBS):
        d = (a[i] - b[i] - borrow) & M64
        r[i] = d & M32; borrow = (d >> 32) & 1
    return r

def bn_addmod(r, add, m):
    r2, carry = bn_add(r, add)
    if carry or bn_cmp(r2, m) >= 0:
        r2 = bn_sub(r2, m)
    return r2

def bn_modmul(a, b, m):
    acc = [0]*LIMBS
    for i in range(LIMBS-1, -1, -1):
        for bit in range(31, -1, -1):
            acc = bn_addmod(acc, acc, m)
            if (b[i] >> bit) & 1:
                acc = bn_addmod(acc, a, m)
    return acc

def bn_modexp(base, exp, m):
    acc = [0]*LIMBS; acc[0] = 1
    for i in range(LIMBS-1, -1, -1):
        for bit in range(31, -1, -1):
            acc = bn_modmul(acc, acc, m)
            if (exp[i] >> bit) & 1:
                acc = bn_modmul(acc, base, m)
    return acc

fails = 0
def check(cond, msg):
    global fails
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond: fails += 1

print("== RSA bignum vs Python pow() ==")
for name, (N, D) in [("A", ("RSA_A_N", "RSA_A_D")), ("B", ("RSA_B_N", "RSA_B_D"))]:
    n = keyint(N); d = keyint(D); e = 65537
    msg = bytes([(i*7+3) & 0xFF for i in range(64)]); msg = bytes([0]) + msg[1:]
    m = int.from_bytes(msg, "big")
    c_ref = pow(m, e, n); m_ref = pow(c_ref, d, n)
    ebn = [0]*LIMBS; ebn[0] = e
    c = bn_to_int(bn_modexp(bytes_to_bn(msg), ebn, bytes_to_bn(n.to_bytes(64,"big"))))
    m2 = bn_to_int(bn_modexp(bytes_to_bn(c.to_bytes(64,"big")), bytes_to_bn(d.to_bytes(64,"big")),
                             bytes_to_bn(n.to_bytes(64,"big"))))
    check(c == c_ref, f"device {name}: bn_modexp encrypt matches pow()")
    check(m2 == m == m_ref, f"device {name}: bn_modexp decrypt recovers message")

# ---- AES, mirroring crypto.c ----
SBOX = bytes.fromhex(
 "637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0"
 "b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b275"
 "09832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cf"
 "d0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2"
 "cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb"
 "e0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08"
 "ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"
 "e1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16")

def xtime(x): return ((x << 1) ^ ((x >> 7) * 0x1b)) & 0xFF

def key_expand(key):
    rk = list(key); rcon = 1
    i = 16
    while i < 176:
        tt = rk[i-4:i]
        if i % 16 == 0:
            tt = tt[1:] + tt[:1]
            tt = [SBOX[x] for x in tt]
            tt[0] ^= rcon
            rcon = ((rcon << 1) ^ ((rcon >> 7) * 0x1b)) & 0xFF
        for j in range(4):
            rk.append(rk[i-16+j] ^ tt[j])
        i += 4
    return rk

def encrypt_block(s, rk):
    s = list(s)
    for i in range(16): s[i] ^= rk[i]
    for rnd in range(1, 11):
        for i in range(16): s[i] = SBOX[s[i]]
        s[1],s[5],s[9],s[13] = s[5],s[9],s[13],s[1]
        s[2],s[10] = s[10],s[2]; s[6],s[14] = s[14],s[6]
        s[3],s[7],s[11],s[15] = s[15],s[3],s[7],s[11]
        if rnd != 10:
            for c in range(0,16,4):
                a0,a1,a2,a3 = s[c],s[c+1],s[c+2],s[c+3]
                s[c]   = xtime(a0)^(xtime(a1)^a1)^a2^a3
                s[c+1] = a0^xtime(a1)^(xtime(a2)^a2)^a3
                s[c+2] = a0^a1^xtime(a2)^(xtime(a3)^a3)
                s[c+3] = (xtime(a0)^a0)^a1^a2^xtime(a3)
        for i in range(16): s[i] ^= rk[rnd*16+i]
    return bytes(s)

print("== AES ==")
rk = key_expand(bytes(range(16)))
ct = encrypt_block(bytes.fromhex("00112233445566778899aabbccddeeff"), rk)
check(ct.hex() == "69c4e0d86a7b0430d8cdb78070b4c55a", "AES-128 FIPS-197 known-answer test")

print("\n" + ("*** FAILURES ***" if fails else "ALL CHECKS PASSED"))
exit(fails)