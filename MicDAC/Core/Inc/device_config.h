/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    device_config.h
  * @brief   THE ONE PER-BOARD SWITCH for the Secure Voice project.
  *
  *   IS_DEVICE_A = 1  -> the board whose phone number ends in ...001
  *   IS_DEVICE_A = 0  -> the board whose phone number ends in ...002
  *
  * This single macro is the ONLY thing that differs between the two boards.
  * Everything else is derived from it:
  *   - main.c   picks PHONE_NUMBER / PEER_PHONE
  *   - crypto.c picks the RSA key pair and the AES-CTR counter base
  * so the two boards can never be configured inconsistently.
  *
  * Flashing procedure:
  *   1. set IS_DEVICE_A 1 -> build -> flash board ...001
  *   2. set IS_DEVICE_A 0 -> build -> flash board ...002
  ******************************************************************************
  */
/* USER CODE END Header */
#ifndef DEVICE_CONFIG_H
#define DEVICE_CONFIG_H

#define IS_DEVICE_A 1   /* 1 = board ...001 (A), 0 = board ...002 (B) */

#endif /* DEVICE_CONFIG_H */