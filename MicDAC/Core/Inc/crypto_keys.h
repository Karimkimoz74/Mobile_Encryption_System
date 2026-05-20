#ifndef CRYPTO_KEYS_H
#define CRYPTO_KEYS_H
#include <stdint.h>
#include "device_config.h"   /* IS_DEVICE_A - per-board switch */

/* Pre-shared AES-128 session key, generated offline by keygen.py.
   IDENTICAL on both boards. If you regenerate it, re-flash BOTH. */
static const uint8_t AES_SESSION_KEY[16] = {
  0x0E, 0xEC, 0x4D, 0xDC, 0x8F, 0x43, 0xC7, 0x09, 0x7B, 0x0A, 0xEE, 0x54, 0xB8, 0x50, 0x1B, 0xEA
};

#endif /* CRYPTO_KEYS_H */
