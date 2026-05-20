/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    crypto.c
  * @brief   Phase 7 encryption — AES-128 in CTR mode.
  *
  *  - AES-128 : compact encrypt-only core (CTR mode only needs encrypt).
  *  - CTR     : AES keystream XOR for the bulk audio, separate TX/RX counters.
  *
  * The 16-byte session key is pre-shared (crypto_keys.h) — identical on both
  * boards — so there is no run-time key exchange and no startup delay.
  ******************************************************************************
  */
/* USER CODE END Header */

#include "crypto.h"
#include "crypto_keys.h"
#include <string.h>

/* ===================================================================== */
/* AES-128 — compact encrypt-only core (CTR mode never needs decrypt).    */
/* ===================================================================== */
static const uint8_t sbox[256] = {
  0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
  0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
  0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
  0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
  0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
  0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
  0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
  0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
  0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
  0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
  0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
  0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
  0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
  0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
  0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
  0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

static uint8_t round_key[176];   /* 11 round keys x 16 bytes */

static void aes_key_expand(const uint8_t key[16])
{
    memcpy(round_key, key, 16);
    uint8_t rcon = 1;
    for (int i = 16; i < 176; i += 4) {
        uint8_t t[4];
        t[0] = round_key[i - 4]; t[1] = round_key[i - 3];
        t[2] = round_key[i - 2]; t[3] = round_key[i - 1];
        if ((i % 16) == 0) {
            uint8_t tmp = t[0];                 /* rotate word */
            t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = tmp;
            t[0] = sbox[t[0]]; t[1] = sbox[t[1]];
            t[2] = sbox[t[2]]; t[3] = sbox[t[3]];
            t[0] ^= rcon;
            rcon = (uint8_t)((rcon << 1) ^ ((rcon >> 7) * 0x1b));
        }
        for (int j = 0; j < 4; j++)
            round_key[i + j] = round_key[i - 16 + j] ^ t[j];
    }
}

static uint8_t xtime(uint8_t x)
{
    return (uint8_t)((x << 1) ^ ((x >> 7) * 0x1b));
}

/* Encrypt one 16-byte block in place (state laid out column-major). */
static void aes_encrypt_block(uint8_t *s)
{
    /* round 0 — AddRoundKey */
    for (int i = 0; i < 16; i++) s[i] ^= round_key[i];

    for (int round = 1; round <= 10; round++) {
        /* SubBytes */
        for (int i = 0; i < 16; i++) s[i] = sbox[s[i]];

        /* ShiftRows */
        uint8_t t;
        t = s[1];  s[1] = s[5];  s[5] = s[9];  s[9] = s[13]; s[13] = t;
        t = s[2];  s[2] = s[10]; s[10] = t;
        t = s[6];  s[6] = s[14]; s[14] = t;
        t = s[15]; s[15] = s[11]; s[11] = s[7]; s[7] = s[3]; s[3] = t;

        /* MixColumns — skipped on the final round */
        if (round != 10) {
            for (int c = 0; c < 16; c += 4) {
                uint8_t a0 = s[c], a1 = s[c + 1], a2 = s[c + 2], a3 = s[c + 3];
                s[c]     = (uint8_t)(xtime(a0) ^ (xtime(a1) ^ a1) ^ a2 ^ a3);
                s[c + 1] = (uint8_t)(a0 ^ xtime(a1) ^ (xtime(a2) ^ a2) ^ a3);
                s[c + 2] = (uint8_t)(a0 ^ a1 ^ xtime(a2) ^ (xtime(a3) ^ a3));
                s[c + 3] = (uint8_t)((xtime(a0) ^ a0) ^ a1 ^ a2 ^ xtime(a3));
            }
        }

        /* AddRoundKey */
        for (int i = 0; i < 16; i++) s[i] ^= round_key[round * 16 + i];
    }
}

/* ===================================================================== */
/* CTR mode + session state                                              */
/* ===================================================================== */
/* The two directions use disjoint counter spaces so they can never reuse a
   keystream block. Which space is TX and which is RX is decided per call
   from the phone numbers (crypto_start_session) — not from a build flag — so
   the two boards can never end up on the same side by mistake. */
static uint32_t tx_counter = 0;
static uint32_t rx_counter = 0;

/* CTR: keystream = AES(counter), then XOR. 'len' must be a multiple of 16. */
static void ctr_crypt(uint8_t *buf, uint32_t len, uint32_t *counter)
{
    for (uint32_t off = 0; off < len; off += 16) {
        uint8_t ks[16];
        memset(ks, 0, sizeof ks);
        uint32_t c = *counter;
        ks[12] = (uint8_t)(c >> 24); ks[13] = (uint8_t)(c >> 16);
        ks[14] = (uint8_t)(c >>  8); ks[15] = (uint8_t)(c);
        aes_encrypt_block(ks);                  /* ks = AES(counter) */
        for (int i = 0; i < 16; i++)
            buf[off + i] ^= ks[i];              /* C = P XOR keystream */
        (*counter)++;
    }
}

void crypto_encrypt_tx(uint8_t *buf, uint32_t len) { ctr_crypt(buf, len, &tx_counter); }
void crypto_decrypt_rx(uint8_t *buf, uint32_t len) { ctr_crypt(buf, len, &rx_counter); }

/* Install the pre-shared key and pick the CTR counter spaces. The board with
   the LOWER phone number (i_am_low = 1) transmits from 0 and receives from
   2^31; the other board is the mirror image. Both ends derive i_am_low from
   the same two phone numbers, so they always agree — no per-board flag. */
void crypto_start_session(int i_am_low)
{
    aes_key_expand(AES_SESSION_KEY);
    if (i_am_low) {
        tx_counter = 0x00000000u;
        rx_counter = 0x80000000u;
    } else {
        tx_counter = 0x80000000u;
        rx_counter = 0x00000000u;
    }
}

void crypto_init(void)
{
    tx_counter = 0;
    rx_counter = 0;
}

/* Fingerprint = first 4 bytes of AES(key, all-zero block). Lets the relay
   confirm both boards were flashed with the SAME pre-shared key. */
uint32_t crypto_key_fingerprint(void)
{
    uint8_t blk[16];
    memset(blk, 0, sizeof blk);
    aes_key_expand(AES_SESSION_KEY);
    aes_encrypt_block(blk);
    return ((uint32_t)blk[0] << 24) | ((uint32_t)blk[1] << 16) |
           ((uint32_t)blk[2] <<  8) |  (uint32_t)blk[3];
}