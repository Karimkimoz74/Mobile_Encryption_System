# Secure Real-Time Voice Communication System (STM32 + LTE)

Graduation project — AAST Computer Engineering, Embedded Systems (ECE5206).

Two identical STM32-based devices exchange real-time voice over 4G LTE, identifying
each other by phone number through a relay server. Designed to later carry
RSA + AES encrypted audio.

## Architecture

```
mic -> MAX9814 -> STM32 ADC (8 kHz, 12-bit) -> 8-bit PCM
    -> A7608 4G modem (AT+CIPSEND over TCP)
    -> ngrok tunnel -> Python relay -> ngrok
    -> peer A7608 modem -> peer STM32 (+IPD parse)
    -> MCP4725 DAC -> LM386 -> headphones
```

- **Identification:** phone numbers as labels on the relay (`REG` / `CALL` / `ANS` / `HUP`).
- **Call mode:** AUTO-VOX half-duplex (voice-activated transmit).
- **Encryption:** RSA-512 wraps an AES-128 session key, AES-CTR for bulk audio (planned — Submission 2).

## Repository layout

| Path | Description |
|------|-------------|
| `MicDAC/` | STM32F401 firmware (CubeMX + CMake). Main logic in `Core/Src/main.c`. |
| `Server/` | `relay.py` — Python asyncio TCP relay (REG/CALL/INC/ANS/GO/HUP protocol). |
| `Project/` | Phase documentation PDFs and the reportlab generator scripts. |

## Hardware (×2 — two identical nodes)

- STM32F401 Black Pill (84 MHz)
- LilyGO A7608 4G LTE module (ESP32 + SIMCom A7608)
- MAX9814 microphone preamplifier
- MCP4725 12-bit I²C DAC
- LM386 audio amplifier

## Status

- ✅ Phase 1–5: toolchain, analog audio, digital loopback, LTE bring-up, relay registration
- ✅ Phase 6: two-device voice call over LTE (call control + live audio)
- ⬜ Phase 7: RSA + AES encryption
- ⬜ Phase 8: demo polish

## Build (firmware)

Open `MicDAC/` in VS Code with the STM32 extension, or build with CMake +
arm-none-eabi-gcc. Flash with ST-Link.

## Run (relay)

```
cd Server
python relay.py          # listens on TCP 5555
ngrok tcp 5555           # expose publicly; update NGROK_HOST/PORT in main.c
```