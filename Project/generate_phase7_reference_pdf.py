"""
Generates Phase 7 TECHNICAL REFERENCE PDF.
Everything in one document: the RSA equations, the AES equations, the full
encrypted-call process, every file and what it does, and the complete
crypto module source code with line-by-line explanation.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase7_Encryption_Reference.pdf"

styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleBig', parent=styles['Title'],
    fontSize=20, leading=26, alignment=TA_CENTER,
    textColor=colors.HexColor('#0B3D91'), spaceAfter=10)

subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'],
    fontSize=13, leading=17, alignment=TA_CENTER,
    textColor=colors.HexColor('#444444'), spaceAfter=20)

h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontSize=16, leading=20, spaceBefore=16, spaceAfter=10,
    textColor=colors.HexColor('#0B3D91'))

h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontSize=12, leading=16, spaceBefore=10, spaceAfter=5,
    textColor=colors.HexColor('#1F4E79'))

h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontSize=11, leading=14, spaceBefore=8, spaceAfter=4,
    textColor=colors.HexColor('#2E75B6'))

body = ParagraphStyle('Body', parent=styles['Normal'],
    fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)

bullet = ParagraphStyle('Bullet', parent=body,
    leftIndent=14, bulletIndent=4, spaceAfter=3)

success_style = ParagraphStyle('Success', parent=body,
    fontSize=10, leading=14,
    textColor=colors.HexColor('#1B7A3F'),
    backColor=colors.HexColor('#E8F5EC'),
    borderColor=colors.HexColor('#1B7A3F'),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=8)

warn_style = ParagraphStyle('Warn', parent=body,
    fontSize=10, leading=14,
    textColor=colors.HexColor('#8A4500'),
    backColor=colors.HexColor('#FFF4E5'),
    borderColor=colors.HexColor('#E08810'),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=8)

note_style = ParagraphStyle('Note', parent=body,
    fontSize=9, leading=12,
    textColor=colors.HexColor('#666666'),
    leftIndent=10, spaceAfter=6)

eq_style = ParagraphStyle('Eq', parent=styles['Normal'],
    fontName='Courier-Bold', fontSize=12, leading=18,
    alignment=TA_CENTER,
    textColor=colors.HexColor('#0B3D91'),
    backColor=colors.HexColor('#EEF2FA'),
    borderColor=colors.HexColor('#9DB4D6'),
    borderWidth=0.5, borderPadding=6,
    spaceBefore=6, spaceAfter=8)

code_style = ParagraphStyle('Code', parent=styles['Code'],
    fontName='Courier', fontSize=7.5, leading=9.5,
    leftIndent=6, rightIndent=4,
    backColor=colors.HexColor('#F4F4F4'),
    borderColor=colors.HexColor('#CCCCCC'),
    borderWidth=0.5, borderPadding=4,
    spaceBefore=4, spaceAfter=8)

ascii_style = ParagraphStyle('Ascii', parent=styles['Code'],
    fontName='Courier', fontSize=8, leading=10,
    leftIndent=4, rightIndent=4,
    spaceBefore=4, spaceAfter=8)

cell_style = ParagraphStyle('CellBody', parent=styles['Normal'],
    fontName='Helvetica', fontSize=8.5, leading=11,
    spaceBefore=0, spaceAfter=0, alignment=0)

cell_header_style = ParagraphStyle('CellHeader', parent=styles['Normal'],
    fontName='Helvetica-Bold', fontSize=9, leading=11,
    textColor=colors.white,
    spaceBefore=0, spaceAfter=0, alignment=0)


def esc(t):
    """Escape XML-special chars so code/diagrams render literally."""
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def P(t, s=body):
    return Paragraph(t, s)


def eq(t):
    """Equation line. Caller may use <super> tags directly."""
    return Paragraph(t, eq_style)


def code(t):
    return Preformatted(esc(t), code_style)


def ascii_block(t):
    return Preformatted(esc(t), ascii_style)


def wrap_cell(value, header_row=False):
    if isinstance(value, Paragraph):
        return value
    if value is None:
        value = ''
    return Paragraph(str(value), cell_header_style if header_row else cell_style)


def make_table(data, col_widths=None, header=True):
    wrapped = []
    for r, row in enumerate(data):
        is_header = (header and r == 0)
        wrapped.append([wrap_cell(c, is_header) for c in row])
    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#888888')),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if header:
        cmds += [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B3D91'))]
    t.setStyle(TableStyle(cmds))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm,
                      "Secure Voice Project | Phase 7 — Encryption Technical Reference")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ==================== TITLE ====================
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 7<br/>Encryption Technical Reference", title_style))
story.append(P("RSA + AES: the equations, the process, the files, and the full code",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>This document contains everything for Phase 7 in one place:</b>", body))
for t in ["The RSA equations — key generation, encryption, decryption — with a worked example.",
          "The AES equations — XOR and CTR-mode keystream.",
          "The complete encrypted-call process, step by step.",
          "Every file in the crypto module and exactly what each one does.",
          "The full source code of the crypto module, explained piece by piece."]:
    story.append(P("&bull; " + t, bullet))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>Builds on:</b> Phase 6 (plain voice between two devices).<br/>"
               "<b>Goal of Phase 7:</b> the voice on the LTE link becomes unintelligible "
               "to anyone who intercepts it.", success_style))
story.append(PageBreak())

# ==================== 1. THE PLAN ====================
story.append(P("1. The Plan in One Picture", h1))

story.append(P("Two ciphers are used together. Each fixes the other's weakness.", body))

plan = [
    ['', 'RSA-512', 'AES-128'],
    ['Type', 'Asymmetric (public + private key)', 'Symmetric (one shared key)'],
    ['Speed', 'Slow', 'Fast'],
    ['Used', 'ONCE, at call setup', 'On EVERY audio packet'],
    ['Job', 'Deliver the AES key safely', 'Scramble the actual voice'],
]
story.append(make_table(plan, col_widths=[2.8 * cm, 6 * cm, 5.7 * cm]))

story.append(ascii_block(r"""
   CALL CONNECTS
        |
        v
   [ RSA - run once ]   caller makes a random AES key,
                        locks it with peer's PUBLIC key, sends it;
                        peer unlocks it with its PRIVATE key.
        |               --> both sides now share the same AES key
        v
   [ AES - run always ] every voice packet is scrambled with that
                        shared AES key, until hangup.
""".strip()))

# ==================== 2. RSA EQUATIONS ====================
story.append(P("2. RSA — The Equations", h1))

story.append(P("2.1 Key generation (done once on the PC by keygen.py)", h2))
story.append(P("Two large random prime numbers <b>p</b> and <b>q</b> are chosen. From them:",
               body))

story.append(eq("N  =  p &times; q"))
story.append(P("<b>N</b> is the <i>modulus</i>. For RSA-512 it is a 512-bit number "
               "(64 bytes). N is part of both the public and the private key.", body))

story.append(eq("phi(N)  =  (p &minus; 1) &times; (q &minus; 1)"))
story.append(P("<b>phi(N)</b> (Euler's totient) is a helper number used only during key "
               "generation. It is secret and discarded afterwards.", body))

story.append(eq("choose E  such that  1 &lt; E &lt; phi(N)  and  gcd(E, phi(N)) = 1"))
story.append(P("<b>E</b> is the <i>public exponent</i>. In practice E = 65537 is used for "
               "every key. It must share no common factor with phi(N).", body))

story.append(eq("D  =  E<super>&minus;1</super>  mod  phi(N)"))
story.append(P("<b>D</b> is the <i>private exponent</i>. It is the modular inverse of E: "
               "the number for which (E &times; D) divided by phi(N) leaves remainder 1. "
               "D is the secret that makes decryption possible.", body))

story.append(P("Result — the two keys:", body))
keytab = [
    ['Key', 'Made of', 'Secret?'],
    ['Public key', '(N, E)', 'No — shared with anyone'],
    ['Private key', '(N, D)', 'Yes — never leaves the device'],
]
story.append(make_table(keytab, col_widths=[3.5 * cm, 4 * cm, 7 * cm]))

story.append(P("2.2 Encryption and decryption", h2))
story.append(P("The message <b>m</b> must be a number smaller than N. To encrypt it into "
               "the ciphertext <b>c</b>:", body))
story.append(eq("c  =  m<super>E</super>  mod  N"))
story.append(P("To decrypt the ciphertext back to the message:", body))
story.append(eq("m  =  c<super>D</super>  mod  N"))
story.append(P("\"mod N\" means: divide by N and keep only the remainder. Encryption uses "
               "the public pair (N, E); decryption uses the private pair (N, D). Locking "
               "with E can only be undone by D, and D cannot be found without the original "
               "primes p and q.", body))

story.append(P("2.3 Worked mini-example (tiny numbers, to see it actually work)", h2))
mini = [
    ['Step', 'Equation', 'Result'],
    ['Pick primes', 'p, q', 'p = 11, q = 13'],
    ['Modulus', 'N = p x q', 'N = 143'],
    ['Totient', 'phi = (p-1)(q-1)', 'phi = 10 x 12 = 120'],
    ['Public exponent', 'choose E', 'E = 7'],
    ['Private exponent', 'D = E^-1 mod phi', 'D = 103   (7 x 103 = 721 = 6x120 + 1)'],
    ['Encrypt m = 9', 'c = m^E mod N', 'c = 9^7 mod 143 = 48'],
    ['Decrypt c = 48', 'm = c^D mod N', 'm = 48^103 mod 143 = 9   (original back)'],
]
story.append(make_table(mini, col_widths=[3 * cm, 4.5 * cm, 7 * cm]))
story.append(P("Public key here = (143, 7); private key = (143, 103). The number 48 is "
               "what travels the network — useless without D = 103.", note_style))

story.append(P("2.4 The 64-byte block and padding", h2))
story.append(P("RSA-512 always works on a fixed 64-byte block. The AES key is only 16 "
               "bytes, so the other 48 bytes are filled with random padding before "
               "encryption. Padding does two jobs: it makes the message m large (close to "
               "N, as RSA needs) and it makes every encryption different even if the same "
               "key is sent twice. The receiver strips the padding after decrypting.",
               body))

story.append(P("2.5 Why RSA is secure", h2))
story.append(P("An attacker sees N, E and the ciphertext c. To recover m they need D. "
               "D can only be computed from phi(N), and phi(N) can only be computed from "
               "the primes p and q. The attacker only has N = p x q. Splitting a large N "
               "back into p and q (\"factoring\") has no fast method known — for a 512-bit "
               "N it is computationally enormous. That gap is the entire security of RSA.",
               body))
story.append(P("RSA-512 is weak by modern standards and would never protect a real system. "
               "It is used here only because it is light enough for the STM32F401 and is "
               "perfectly adequate to demonstrate the principle for an academic project.",
               warn_style))

story.append(PageBreak())

# ==================== 3. AES EQUATIONS ====================
story.append(P("3. AES — The Equations", h1))

story.append(P("3.1 XOR — the reversible operation", h2))
story.append(P("AES encryption is built on XOR. XOR compares two bits: equal bits give 0, "
               "different bits give 1.", body))
story.append(eq("0&oplus;0=0   &nbsp; 0&oplus;1=1   &nbsp; 1&oplus;0=1   &nbsp; 1&oplus;1=0"))
story.append(P("Its key property — applying the same value twice cancels out:", body))
story.append(eq("( P &oplus; K ) &oplus; K  =  P"))
story.append(P("So if you XOR the audio with a secret value to scramble it, XOR-ing the "
               "result with the <i>same</i> secret value brings the audio back.", body))

story.append(P("3.2 CTR mode — turning AES into a keystream", h2))
story.append(P("AES itself encrypts one fixed 16-byte block. CTR (Counter) mode uses AES "
               "to generate an endless stream of random-looking bytes — the "
               "<i>keystream</i> — by encrypting a simple counter:", body))
story.append(eq("S<sub>i</sub>  =  AES( K , counter<sub>i</sub> )"))
story.append(P("K is the 16-byte session key; counter<sub>i</sub> is the block number "
               "(0, 1, 2, ...). Each S<sub>i</sub> is one 16-byte block of keystream. "
               "The audio is then encrypted and decrypted by XOR:", body))
story.append(eq("C  =  P &oplus; S<sub>i</sub>      (encrypt)"))
story.append(eq("P  =  C &oplus; S<sub>i</sub>      (decrypt)"))
story.append(P("P = plaintext audio, C = ciphertext (scrambled) audio. Because both "
               "devices hold the same key K and use the same counter, both generate the "
               "same keystream S<sub>i</sub>, so the receiver's XOR exactly undoes the "
               "sender's XOR.", body))

story.append(P("3.3 The counter", h2))
story.append(P("The counter must advance by one for every 16-byte block and must never "
               "repeat for a given key — reusing a counter value would leak information. "
               "Both sides start at 0 when the call begins and count up together. Encrypt "
               "and decrypt are the same operation, which is why a single function "
               "<code>aes_ctr_crypt()</code> serves both directions.", body))

story.append(PageBreak())

# ==================== 4. THE PROCESS ====================
story.append(P("4. The Encrypted Call — Full Process", h1))

story.append(P("Steps 1-7 are the Phase 6 call. Phase 7 inserts one new step, 5.5, between "
               "the call connecting and the audio starting.", body))

story.append(ascii_block(r"""
   Device A            relay            Device B
   --------            -----            --------
   REG 001  ------------->
                    REG 002  <-------------
   [A presses CALL]
   CALL 002 ------------->  INC 001 ------->
                                       [B presses ANSWER]
                            <------- ANS
            <----- GO        GO ------->
   ========================= STEP 5.5: KEY EXCHANGE (RSA) =========================
   A: make random 16-byte AES key  ->  pad to 64 bytes
   A: blob = rsa_encrypt(padded)   (locked with B's PUBLIC key)
   A: send blob  ------------------------------------------>
                                       B: rsa_decrypt(blob) with B's PRIVATE key
                                       B: strip padding -> recovers the AES key
   --> both devices now hold the SAME 16-byte AES key
   ============================ STEP 6: ENCRYPTED AUDIO ==========================
   A: audio -> aes_ctr_crypt() -> scrambled -> LTE ------->  B: aes_ctr_crypt() -> audio
   B: audio -> aes_ctr_crypt() -> scrambled -> LTE ------->  A: aes_ctr_crypt() -> audio
   ...continues until...
   [HANGUP]  -> AES key is erased; next call generates a fresh one
""".strip()))

proc = [
    ['Step', 'What happens', 'Crypto function'],
    ['1-5', 'Register, CALL, INC, ANS, GO (Phase 6 call setup)', 'none'],
    ['5.5a', 'Caller generates a random 16-byte AES key', 'crypto_init / RNG'],
    ['5.5b', 'Caller pads it to 64 bytes and RSA-locks it with peer public key',
     'rsa_encrypt()'],
    ['5.5c', 'The 64-byte blob is sent as one control message over LTE', 'tcp_send_line'],
    ['5.5d', 'Peer RSA-unlocks the blob with its own private key, strips padding',
     'rsa_decrypt()'],
    ['5.5e', 'Both sides load the recovered key into AES', 'aes_ctr_set_key()'],
    ['6', 'Every audio packet is scrambled before send, unscrambled after receive',
     'aes_ctr_crypt()'],
    ['7', 'Hangup — the AES key is erased from RAM', 'none'],
]
story.append(make_table(proc, col_widths=[1.6 * cm, 9 * cm, 3.9 * cm]))

story.append(PageBreak())

# ==================== 5. THE FILES ====================
story.append(P("5. The Files — What Each One Does", h1))

story.append(P("5.1 New files added for Phase 7", h2))
files = [
    ['File', 'Where', 'What it does'],
    ['keygen.py', 'MicDAC/ (runs on PC)',
     'Generates the RSA keypairs once. Writes crypto_keys.h. Never runs on the STM32.'],
    ['crypto_keys.h', 'MicDAC/Core/Inc/',
     'Pure data: the RSA key numbers as byte arrays. No logic. Produced by keygen.py.'],
    ['crypto.h', 'MicDAC/Core/Inc/',
     'The header: declares the crypto functions so main.c can call them.'],
    ['crypto.c', 'MicDAC/Core/Src/',
     'The encryption logic: RSA bignum math + AES-CTR. The "encryption tool".'],
    ['aes.c / aes.h', 'MicDAC/Core/Src/ + Inc/',
     'The AES block cipher core (tiny-AES-c, a small public-domain library).'],
]
story.append(make_table(files, col_widths=[2.6 * cm, 3.6 * cm, 8.3 * cm]))

story.append(P("5.2 Existing files and their roles", h2))
exist = [
    ['File', 'Role'],
    ['Core/Src/main.c', 'The program: call state machine, buttons, LTE, audio. Calls into crypto.c.'],
    ['Core/Src/adc.c, tim.c, i2c.c, usart.c, dma.c, gpio.c',
     'CubeMX hardware setup (ADC, timers, I2C DAC, modem UART, DMA, pins).'],
    ['CMakeLists.txt', 'Build recipe. Must be edited to add crypto.c and aes.c.'],
    ['Server/relay.py', 'Runs on the laptop. Passes messages and audio between the two devices.'],
]
story.append(make_table(exist, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("5.3 How the files depend on each other", h2))
story.append(ascii_block(r"""
   keygen.py  --(run once on PC)-->  crypto_keys.h
                                          |
                                          |  #include
                                          v
   main.c  --calls-->  crypto.h  <--declares--  crypto.c  --uses-->  aes.c
      |                                            |
      |  (the call logic)                          |  (RSA bignum + AES-CTR)
      v                                            v
   adc/tim/i2c/usart/dma/gpio.c                crypto_keys.h (the keys)

   CMakeLists.txt  --tells the compiler-->  build main.c + crypto.c + aes.c + ...
""".strip()))

story.append(PageBreak())

# ==================== 6. THE CODE ====================
story.append(P("6. The Code", h1))

story.append(P("6.1 crypto.h — the interface main.c sees", h2))
story.append(code('''#ifndef CRYPTO_H
#define CRYPTO_H
#include <stdint.h>

/* One-time setup at startup. */
void crypto_init(void);

/* ---- RSA-512: works on fixed 64-byte blocks ---- */
/* Lock a 64-byte block with the PEER's public key.  */
void rsa_encrypt(const uint8_t in[64], uint8_t out[64]);
/* Unlock a 64-byte block with MY private key.       */
void rsa_decrypt(const uint8_t in[64], uint8_t out[64]);

/* ---- AES-128 in CTR mode ---- */
/* Load the 16-byte session key for this call.       */
void aes_ctr_set_key(const uint8_t key[16]);
/* Encrypt OR decrypt len bytes in place. block0 is the
   starting counter for this buffer.                 */
void aes_ctr_crypt(uint8_t *buf, uint32_t len, uint32_t block0);

#endif /* CRYPTO_H */'''))
story.append(P("Just five function declarations. main.c includes this header and calls "
               "these names — it does not need to know the math inside.", note_style))

story.append(P("6.2 crypto_keys.h — the keys (made by keygen.py)", h2))
story.append(code('''#ifndef CRYPTO_KEYS_H
#define CRYPTO_KEYS_H
#include <stdint.h>

#define IS_DEVICE_A 1          /* 1 on device ...001, 0 on device ...002 */

static const uint8_t RSA_A_N[64] = { 0x.., 0x.., ... };  /* device A modulus  */
static const uint8_t RSA_A_D[64] = { 0x.., 0x.., ... };  /* device A private  */
static const uint8_t RSA_B_N[64] = { 0x.., 0x.., ... };  /* device B modulus  */
static const uint8_t RSA_B_D[64] = { 0x.., 0x.., ... };  /* device B private  */
static const uint32_t RSA_E = 65537u;                    /* shared public exp */

#if IS_DEVICE_A
  #define MY_N    RSA_A_N
  #define MY_D    RSA_A_D
  #define PEER_N  RSA_B_N
#else
  #define MY_N    RSA_B_N
  #define MY_D    RSA_B_D
  #define PEER_N  RSA_A_N
#endif
#endif'''))
story.append(P("This file is only data. The 0x.. bytes are filled in by keygen.py. Both "
               "devices use the same file; only IS_DEVICE_A differs.", note_style))

story.append(P("6.3 crypto.c — RSA: representing 512-bit numbers", h2))
story.append(P("The STM32 has no 512-bit integer type. A big number is stored as an array "
               "of 16 small 32-bit pieces (\"limbs\"): 16 x 32 = 512 bits. limb[0] is the "
               "least significant.", body))
story.append(code('''#include "crypto.h"
#include "crypto_keys.h"
#include "aes.h"
#include <string.h>

#define LIMBS 16                  /* 16 x 32-bit = 512-bit numbers */
typedef uint32_t bn_t[LIMBS];     /* a big number; bn[0] = least significant */

/* The RSA keys are stored big-endian (64 bytes). Convert to a limb array. */
static void bytes_to_bn(const uint8_t b[64], bn_t out) {
    for (int i = 0; i < LIMBS; i++) {
        int j = (LIMBS - 1 - i) * 4;
        out[i] = ((uint32_t)b[j]   << 24) | ((uint32_t)b[j+1] << 16) |
                 ((uint32_t)b[j+2] <<  8) | ((uint32_t)b[j+3]);
    }
}
static void bn_to_bytes(const bn_t in, uint8_t b[64]) {
    for (int i = 0; i < LIMBS; i++) {
        int j = (LIMBS - 1 - i) * 4;
        b[j]   = (uint8_t)(in[i] >> 24); b[j+1] = (uint8_t)(in[i] >> 16);
        b[j+2] = (uint8_t)(in[i] >>  8); b[j+3] = (uint8_t)(in[i]);
    }
}'''))

story.append(P("6.4 crypto.c — RSA: add, subtract, compare", h2))
story.append(code('''/* Compare: returns -1 if a<b, 0 if equal, +1 if a>b. */
static int bn_cmp(const bn_t a, const bn_t b) {
    for (int i = LIMBS - 1; i >= 0; i--) {
        if (a[i] < b[i]) return -1;
        if (a[i] > b[i]) return  1;
    }
    return 0;
}
/* r = a + b, returns the carry out of the top limb. */
static uint32_t bn_add(bn_t r, const bn_t a, const bn_t b) {
    uint64_t carry = 0;
    for (int i = 0; i < LIMBS; i++) {
        uint64_t s = (uint64_t)a[i] + b[i] + carry;
        r[i] = (uint32_t)s;
        carry = s >> 32;
    }
    return (uint32_t)carry;
}
/* r = a - b  (assumes a >= b). */
static void bn_sub(bn_t r, const bn_t a, const bn_t b) {
    uint64_t borrow = 0;
    for (int i = 0; i < LIMBS; i++) {
        uint64_t d = (uint64_t)a[i] - b[i] - borrow;
        r[i] = (uint32_t)d;
        borrow = (d >> 32) & 1;
    }
}'''))

story.append(P("6.5 crypto.c — RSA: modular multiply and modular power", h2))
story.append(P("These two functions ARE the RSA equations c = m^E mod N translated into "
               "code that works on 512-bit numbers.", body))
story.append(code('''/* r = (r + add) mod m, given r < m and add < m. One subtraction is enough
   because the sum is always less than 2m. */
static void bn_addmod(bn_t r, const bn_t add, const bn_t m) {
    uint32_t carry = bn_add(r, r, add);
    if (carry || bn_cmp(r, m) >= 0) bn_sub(r, r, m);
}

/* r = (a * b) mod m  --  double-and-add, bit by bit through b.
   No 1024-bit product is ever formed; only 512-bit add/sub are used. */
static void bn_modmul(bn_t r, const bn_t a, const bn_t b, const bn_t m) {
    bn_t acc; memset(acc, 0, sizeof acc);          /* acc = 0 */
    for (int i = LIMBS - 1; i >= 0; i--) {
        for (int bit = 31; bit >= 0; bit--) {
            bn_addmod(acc, acc, m);                /* acc = 2*acc mod m */
            if ((b[i] >> bit) & 1u)
                bn_addmod(acc, a, m);              /* acc = acc + a mod m */
        }
    }
    memcpy(r, acc, sizeof acc);
}

/* r = (base ^ exp) mod m  --  square-and-multiply, bit by bit through exp.
   This is the RSA core: c = m^E mod N  and  m = c^D mod N. */
static void bn_modexp(bn_t r, const bn_t base, const bn_t exp, const bn_t m) {
    bn_t acc; memset(acc, 0, sizeof acc); acc[0] = 1;   /* acc = 1 */
    for (int i = LIMBS - 1; i >= 0; i--) {
        for (int bit = 31; bit >= 0; bit--) {
            bn_modmul(acc, acc, acc, m);                /* square      */
            if ((exp[i] >> bit) & 1u)
                bn_modmul(acc, acc, base, m);           /* multiply    */
        }
    }
    memcpy(r, acc, sizeof acc);
}'''))
story.append(P("<b>Square-and-multiply</b>: to compute base^exp, walk the bits of the "
               "exponent from top to bottom. At each bit, square the running value; if the "
               "bit is 1, also multiply by base. This computes a 512-bit power in only "
               "~512 steps instead of an impossible number of multiplications.", body))

story.append(P("6.6 crypto.c — RSA: the public encrypt / decrypt functions", h2))
story.append(code('''/* Lock a 64-byte block with the PEER's public key:  out = in ^ E mod PEER_N */
void rsa_encrypt(const uint8_t in[64], uint8_t out[64]) {
    bn_t m, n, e, c;
    bytes_to_bn(in, m);
    bytes_to_bn(PEER_N, n);
    memset(e, 0, sizeof e); e[0] = RSA_E;     /* small public exponent -> bignum */
    bn_modexp(c, m, e, n);                    /* c = m ^ E mod N */
    bn_to_bytes(c, out);
}

/* Unlock a 64-byte block with MY private key:  out = in ^ D mod MY_N */
void rsa_decrypt(const uint8_t in[64], uint8_t out[64]) {
    bn_t c, n, d, m;
    bytes_to_bn(in, c);
    bytes_to_bn(MY_N, n);
    bytes_to_bn(MY_D, d);
    bn_modexp(m, c, d, n);                    /* m = c ^ D mod N */
    bn_to_bytes(m, out);
}'''))
story.append(P("Notice how short these are: all the work is in bn_modexp. rsa_encrypt is "
               "literally the equation c = m^E mod N; rsa_decrypt is m = c^D mod N.",
               note_style))

story.append(P("6.7 crypto.c — AES-CTR", h2))
story.append(P("The AES block cipher itself comes from tiny-AES-c (aes.c / aes.h). This "
               "code wraps it in CTR mode: encrypt a counter to get keystream, then XOR.",
               body))
story.append(code('''static uint8_t aes_key[16];

void aes_ctr_set_key(const uint8_t key[16]) {
    memcpy(aes_key, key, 16);              /* store the session key */
}

/* Encrypt OR decrypt buf[] in place (CTR mode is symmetric: same operation). */
void aes_ctr_crypt(uint8_t *buf, uint32_t len, uint32_t block0) {
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, aes_key);
    for (uint32_t off = 0; off < len; off += 16) {
        uint8_t ks[16] = {0};
        uint32_t ctr = block0 + off / 16;          /* this block's counter   */
        ks[12] = (uint8_t)(ctr >> 24); ks[13] = (uint8_t)(ctr >> 16);
        ks[14] = (uint8_t)(ctr >>  8); ks[15] = (uint8_t)(ctr);
        AES_ECB_encrypt(&ctx, ks);                 /* ks = AES(counter) = Si  */
        uint32_t n = (len - off < 16) ? (len - off) : 16;
        for (uint32_t i = 0; i < n; i++)
            buf[off + i] ^= ks[i];                 /* C = P XOR Si            */
    }
}

void crypto_init(void) {
    /* nothing needed yet; placeholder for RNG seeding if required */
}'''))
story.append(P("This single function is used by the sender (audio in -> scrambled out) and "
               "by the receiver (scrambled in -> audio out). XOR with the keystream is its "
               "own inverse, so no separate decrypt function is needed.", note_style))

story.append(P("6.8 Hooking the crypto into main.c", h2))
story.append(P("main.c includes crypto.h and calls the functions at two points: once at "
               "call setup, and around every audio packet.", body))
story.append(code('''#include "crypto.h"

/* --- at call setup, once the call connects (after GO) --- */
uint8_t aes_key[16];
uint8_t blob[64];
/* caller side: */
make_random_bytes(aes_key, 16);            /* fresh session key  */
build_padded_block(plain64, aes_key);      /* 16-byte key -> 64-byte padded */
rsa_encrypt(plain64, blob);                /* lock with peer public key */
/* ...send blob over LTE as one message... */
aes_ctr_set_key(aes_key);

/* peer side: */
/* ...receive blob over LTE... */
rsa_decrypt(blob, plain64);                /* unlock with my private key */
extract_key(aes_key, plain64);             /* strip padding */
aes_ctr_set_key(aes_key);

/* --- around audio (in the ST_IN_CALL block) --- */
/* outgoing, just before tcp_send_audio(out, HALF_SIZE): */
aes_ctr_crypt(out, HALF_SIZE, tx_counter);
tx_counter += HALF_SIZE / 16;

/* incoming, before writing the bytes into play_buf: */
aes_ctr_crypt(in, n, rx_counter);
rx_counter += n / 16;'''))

story.append(P("6.9 CMakeLists.txt — build the new files", h2))
story.append(P("The compiler must be told about the new source files. Add crypto.c and "
               "aes.c to the source list in CMakeLists.txt:", body))
story.append(code('''# in the add_executable(...) / target_sources(...) source list:
    Core/Src/crypto.c
    Core/Src/aes.c'''))

story.append(PageBreak())

# ==================== 7. SUMMARY ====================
story.append(P("7. Summary", h1))

summ = [
    ['Item', 'In one line'],
    ['N = p x q', 'The RSA modulus, built from two secret primes.'],
    ['phi = (p-1)(q-1)', 'Helper number for key generation; secret, then discarded.'],
    ['E', 'Public exponent (65537). Part of the public key.'],
    ['D = E^-1 mod phi', 'Private exponent. The secret that allows decryption.'],
    ['c = m^E mod N', 'RSA encryption — lock with the public key.'],
    ['m = c^D mod N', 'RSA decryption — unlock with the private key.'],
    ['Si = AES(K, counter)', 'AES-CTR keystream block.'],
    ['C = P XOR Si', 'AES encrypt and decrypt (same operation).'],
    ['keygen.py', 'PC tool: generates the RSA keys, writes crypto_keys.h.'],
    ['crypto_keys.h', 'Holds the RSA key numbers. Data only.'],
    ['crypto.h', 'Declares the 5 crypto functions for main.c.'],
    ['crypto.c', 'The encryption tool: RSA bignum math + AES-CTR.'],
    ['aes.c / aes.h', 'The AES block cipher core (tiny-AES-c library).'],
    ['rsa_encrypt / rsa_decrypt', 'Lock / unlock a 64-byte block. Used once per call.'],
    ['aes_ctr_crypt', 'Scramble / unscramble an audio packet. Used every packet.'],
]
story.append(make_table(summ, col_widths=[4.5 * cm, 10 * cm]))

story.append(Spacer(1, 0.4 * cm))
story.append(P("<b>The whole idea, one paragraph:</b> RSA solves \"how do two devices agree "
               "on a secret over an open line\" — the caller locks a fresh AES key with the "
               "peer's public key, only the peer's private key can open it. That happens "
               "once. Then AES, using that shared key, scrambles every voice packet fast "
               "enough for real-time audio, until the call ends.", success_style))

story.append(Spacer(1, 0.4 * cm))
story.append(P("End of Phase 7 — Encryption Technical Reference.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 7 — Encryption Technical Reference",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")