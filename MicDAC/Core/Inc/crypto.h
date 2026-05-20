/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    crypto.h
  * @brief   Phase 7 encryption — AES-128 in CTR mode, pre-shared session key.
  *
  * Both boards are flashed with the SAME 16-byte key (crypto_keys.h), so there
  * is no run-time key exchange: crypto_start_session() just installs the key
  * and resets the CTR counters. AES-128-CTR then encrypts every audio packet.
  *
  * main.c only ever calls the functions declared here; the AES maths is
  * hidden inside crypto.c.
  ******************************************************************************
  */
/* USER CODE END Header */
#ifndef CRYPTO_H
#define CRYPTO_H

#include <stdint.h>

/* One-time init at startup. */
void crypto_init(void);

/* Call once per call, on BOTH devices, the moment the call connects (GO).
   Installs the pre-shared AES key and picks the TX/RX counter spaces.
   'i_am_low' must be 1 on the board with the LOWER phone number and 0 on the
   other — main.c passes strcmp(PHONE_NUMBER, PEER_PHONE) < 0 — so the two
   ends always agree on the keystream split without any build-time flag. */
void crypto_start_session(int i_am_low);

/* Bulk audio — encrypt/decrypt happen in place. 'len' must be a multiple
   of 16. CTR mode is symmetric, but TX and RX use separate counter spaces
   so the two directions never reuse a keystream. */
void crypto_encrypt_tx(uint8_t *buf, uint32_t len);
void crypto_decrypt_rx(uint8_t *buf, uint32_t len);

/* 32-bit fingerprint of the pre-shared key (AES of an all-zero block).
   Both boards MUST report the same value or they cannot decrypt each other.
   main.c sends it to the relay at registration as "DBG KEYFP=........". */
uint32_t crypto_key_fingerprint(void);

#endif /* CRYPTO_H */