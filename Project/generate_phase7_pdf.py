"""
Generates Phase 7 PDF — Encryption Explained (Submission 2).
A from-scratch explanation of encryption/decryption, symmetric vs asymmetric,
RSA, AES, the hybrid scheme, and what crypto_keys.h holds.
Written for readers who have not studied cryptography before.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


OUT = "Phase7_Encryption_Explained.pdf"

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


def P(t, s=body):
    return Paragraph(t, s)


def code(t):
    return Preformatted(t, code_style)


def ascii_block(t):
    return Preformatted(t, ascii_style)


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
                      "Secure Voice Project | Phase 7 — Encryption Explained (Submission 2)")
    canvas.line(2 * cm, A4[1] - 1.3 * cm, A4[0] - 2 * cm, A4[1] - 1.3 * cm)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.1 * cm, "AAST | Embedded Systems")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ============== TITLE PAGE ==============
story.append(Spacer(1, 3 * cm))
story.append(P("Phase 7<br/>Encryption Explained", title_style))
story.append(P("Submission 2: understanding RSA, AES, and the hybrid scheme "
               "before writing a single line of crypto code",
               subtitle_style))
story.append(Spacer(1, 1 * cm))
story.append(P("<b>Purpose:</b> This document explains, from scratch, what encryption and "
               "decryption are, the difference between the two families of ciphers, what "
               "RSA actually does, and what the file <code>crypto_keys.h</code> holds. "
               "It assumes no prior cryptography background.",
               body))
story.append(Spacer(1, 0.5 * cm))
story.append(P("<b>Builds on:</b> Phase 6 (plain unencrypted voice between two devices).<br/>"
               "<b>What's added in Phase 7:</b> a security layer so the voice on the LTE "
               "link is unintelligible to anyone who intercepts it.<br/>"
               "<b>Status:</b> design / understanding stage — no firmware written yet.",
               success_style))
story.append(PageBreak())

# ============== Section 1 ==============
story.append(P("1. What Encryption and Decryption Are", h1))

story.append(P("<b>Encryption</b> is scrambling data so that anyone who intercepts it sees "
               "only meaningless garbage. <b>Decryption</b> is the reverse — turning that "
               "garbage back into the original data.", body))

story.append(P("A <b>key</b> is a secret number that controls the scrambling. The same data "
               "scrambled with two different keys produces two completely different "
               "outputs. Without the correct key, the garbage cannot be turned back into "
               "anything useful.", body))

story.append(P("In this project the \"data\" is the stream of 8-bit audio samples. Today "
               "(Phase 6) those bytes travel the LTE link in the clear — anyone who taps "
               "the relay or the cellular link could record the conversation. After "
               "Phase 7, an interceptor sees only scrambled bytes.", body))

story.append(ascii_block(r"""
   WITHOUT encryption (Phase 6):
       "Hello"  ->  [48 65 6C 6C 6F]  ----LTE---->  [48 65 6C 6C 6F]  ->  "Hello"
                                       (readable by anyone tapping the link)

   WITH encryption (Phase 7):
       "Hello"  ->  ENCRYPT(key)  ->  [9F 2A C1 ...]  ----LTE---->  DECRYPT(key)  ->  "Hello"
                                       (garbage to anyone without the key)
""".strip()))

# ============== Section 2 ==============
story.append(P("2. Two Families of Encryption", h1))

story.append(P("There are two fundamentally different kinds of cipher. This project uses "
               "<b>one of each</b>, because each solves a problem the other cannot.", body))

fam = [
    ['Property', 'Symmetric', 'Asymmetric'],
    ['Number of keys', 'ONE shared secret key', 'TWO keys: public + private'],
    ['Same key both ways?', 'Yes — same key encrypts and decrypts',
     'No — public key encrypts, private key decrypts'],
    ['Speed', 'Very fast', 'Slow'],
    ['Good for', 'Large amounts of data (the audio stream)',
     'Small amounts safely (delivering a key)'],
    ['Example used here', 'AES-128', 'RSA-512'],
]
story.append(make_table(fam, col_widths=[3.5 * cm, 5.5 * cm, 5.5 * cm]))

story.append(P("2.1 — Symmetric (AES): fast, but has a key-delivery problem", h2))
story.append(P("Symmetric encryption is fast enough to scramble thousands of audio bytes "
               "per second. Its weakness: both devices must hold the <b>same secret key</b>, "
               "and that key cannot simply be sent over the LTE link in plain text — an "
               "attacker watching the link would grab it and then decrypt everything.",
               body))

story.append(P("2.2 — Asymmetric (RSA): solves the key-delivery problem", h2))
story.append(P("Asymmetric encryption is built exactly to move a secret safely across an "
               "untrusted link. It is too slow to encrypt the whole audio stream, but it "
               "is perfect for sending one small secret — the AES key — securely.",
               body))

story.append(PageBreak())

# ============== Section 3 ==============
story.append(P("3. What RSA Is", h1))

story.append(P("RSA gives each device <b>two matching keys</b>:", body))

keys = [
    ['Key', 'Secret?', 'Role'],
    ['Public key', 'NO — can be shared with anyone, even publicly',
     'Used to ENCRYPT a message for the owner'],
    ['Private key', 'YES — never leaves the device',
     'The ONLY key that can DECRYPT what the public key encrypted'],
]
story.append(make_table(keys, col_widths=[3 * cm, 6 * cm, 5.5 * cm]))

story.append(P("The defining property of RSA:", body))
story.append(P("<b>Anything encrypted with the public key can only be decrypted with the "
               "matching private key — and nothing else, not even the public key that "
               "locked it.</b>", success_style))

story.append(P("3.1 — The padlock analogy", h2))
story.append(P("Think of the public key as an <b>open padlock</b>. You make many copies of "
               "your open padlock and hand them out to anyone who wants one — you do not "
               "care who has them. Someone puts a message in a box, snaps your padlock "
               "shut, and sends the box to you. Once the padlock clicks shut, <b>only the "
               "single physical key you keep</b> can open it again. Even the person who "
               "locked the box cannot reopen it.", body))

story.append(ascii_block(r"""
   Device A wants to send a secret to Device B:

      Device B's public key  =  an open padlock B handed out
      Device B's private key =  the one key B keeps to itself

      A:  put secret in box  ->  lock with B's padlock  ->  send box over LTE
      Interceptor: sees a locked box, has no key  ->  cannot open it
      B:  receives box  ->  opens with its private key  ->  reads the secret
""".strip()))

story.append(P("3.2 — Why it is secure (the math, briefly)", h2))
story.append(P("RSA's security rests on a simple fact about numbers: multiplying two large "
               "prime numbers together is easy, but taking the result and finding which "
               "two primes produced it (\"factoring\") is practically impossible for large "
               "enough numbers. The public key is built from the product; the private key "
               "depends on knowing the original primes. \"RSA-512\" means the numbers "
               "involved are 512 bits long — roughly 155 decimal digits.", body))

story.append(P("The actual operations are: <code>encrypted = message ^ E mod N</code> and "
               "<code>message = encrypted ^ D mod N</code>, where (N, E) is the public key "
               "and (N, D) is the private key. The STM32 only has to compute these two "
               "formulas — it never has to generate the keys.", note_style))

story.append(P("RSA-512 is considered weak by modern standards and would not be used to "
               "protect real systems. It is chosen here because it is light enough to run "
               "on the STM32F401 and is fully adequate to demonstrate the concept for an "
               "academic project.", warn_style))

story.append(PageBreak())

# ============== Section 4 ==============
story.append(P("4. The Hybrid Scheme — Using Both Together", h1))

story.append(P("RSA is too slow to encrypt every audio packet; AES needs a shared key it "
               "cannot safely deliver on its own. The solution, used by HTTPS, WhatsApp, "
               "and essentially all secure systems, is to <b>combine them</b>: RSA delivers "
               "the AES key, then AES does the bulk work.", body))

story.append(ascii_block(r"""
   STEP 1  Caller generates a fresh random 16-byte AES key (the "session key").

   STEP 2  Caller RSA-encrypts that small key with the PEER's PUBLIC key.   <-- RSA, once
              random AES key  ->  rsa_encrypt(peer_public)  ->  64-byte blob

   STEP 3  Caller sends the 64-byte blob over LTE.
              Safe: only the peer's private key can unwrap it.

   STEP 4  Peer RSA-decrypts the blob with its OWN PRIVATE key.
              -> recovers the exact same 16-byte AES key.

   STEP 5  Both devices now hold the SAME AES key.
           Every audio packet from now on:  aes_ctr_crypt()  before send / after receive.
                                                                          <-- AES, every packet
""".strip()))

story.append(P("RSA runs <b>once per call</b>, where its slowness does not matter. AES runs "
               "on <b>every audio packet</b>, where its speed is exactly what is needed. "
               "A new random AES key each call means that even if one call's key were "
               "exposed, earlier and later calls stay protected.", body))

roles = [
    ['', 'RSA-512', 'AES-128'],
    ['When it runs', 'Once, at call setup', 'On every audio packet'],
    ['What it protects', 'The 16-byte AES session key', 'The actual voice audio'],
    ['Key used', 'Peer public key (encrypt), own private key (decrypt)',
     'The shared 16-byte session key'],
    ['Speed needed', 'Not critical', 'Critical — must keep up with 8 kHz audio'],
]
story.append(make_table(roles, col_widths=[3.5 * cm, 5.5 * cm, 5.5 * cm]))

# ============== Section 5 ==============
story.append(P("5. What crypto_keys.h Is", h1))

story.append(P("<code>crypto_keys.h</code> is a C header file that holds the RSA keys as "
               "arrays of numbers, compiled directly into the firmware. The STM32 cannot "
               "generate RSA keys itself — prime-number searching is far too slow on the "
               "microcontroller — so the keys are generated once on a PC by "
               "<code>keygen.py</code> and written into this file.", body))

story.append(P("5.1 — What it contains", h2))
contents = [
    ['Symbol', 'Meaning'],
    ['RSA_A_N', "Device A's modulus N (64 bytes) — part of both its keys"],
    ['RSA_A_D', "Device A's private exponent D (64 bytes) — secret"],
    ['RSA_B_N', "Device B's modulus N (64 bytes)"],
    ['RSA_B_D', "Device B's private exponent D (64 bytes) — secret"],
    ['RSA_E', "The public exponent E, shared by both (typically 65537)"],
    ['IS_DEVICE_A', "A flag: 1 on device ...001, 0 on device ...002"],
]
story.append(make_table(contents, col_widths=[3.5 * cm, 11 * cm]))

story.append(P("A <b>public key</b> is the pair (N, E). A <b>private key</b> is the pair "
               "(N, D). The <code>IS_DEVICE_A</code> flag tells each device which set of "
               "numbers is \"mine\" and which belongs to \"the peer\" — the same idea as "
               "swapping <code>PHONE_NUMBER</code> per board.", body))

story.append(P("5.2 — Both devices share one file", h2))
story.append(P("<code>keygen.py</code> is run <b>once</b>. The resulting "
               "<code>crypto_keys.h</code> is copied to BOTH devices unchanged — only the "
               "<code>IS_DEVICE_A</code> flag differs. If the file were regenerated "
               "separately for each device, the two would hold different keys and could "
               "never decrypt each other.", warn_style))

story.append(P("5.3 — How the device picks its keys", h2))
story.append(code('''#if IS_DEVICE_A
  #define MY_N    RSA_A_N   /* my modulus  */
  #define MY_D    RSA_A_D   /* my private exponent (secret) */
  #define PEER_N  RSA_B_N   /* peer's modulus */
#else
  #define MY_N    RSA_B_N
  #define MY_D    RSA_B_D
  #define PEER_N  RSA_A_N
#endif

/* Encrypt for the peer:  uses (PEER_N, RSA_E)  -> peer public key
   Decrypt what I receive: uses (MY_N,   MY_D)  -> my private key   */'''))

story.append(PageBreak())

# ============== Section 6 ==============
story.append(P("6. How It Fits the Voice Project", h1))

story.append(P("The encryption is added as a self-contained module — two new files, "
               "<code>crypto.c</code> and <code>crypto.h</code> — so the rest of the "
               "firmware barely changes. <code>main.c</code> simply calls into it.", body))

story.append(P("6.1 — The crypto module functions", h2))
funcs = [
    ['Function', 'Job'],
    ['crypto_init()', 'One-time setup at startup'],
    ['rsa_encrypt() / rsa_decrypt()', 'Wrap / unwrap the AES session key (once per call)'],
    ['aes_ctr_set_key()', 'Load the shared 16-byte AES key'],
    ['aes_ctr_crypt()', 'Encrypt or decrypt one audio packet (every packet)'],
]
story.append(make_table(funcs, col_widths=[5 * cm, 9.5 * cm]))

story.append(P("6.2 — Where it plugs into the call", h2))
story.append(ascii_block(r"""
   Caller presses CALL
        generate random 16-byte AES key
        rsa_encrypt(key with peer public key)  ->  64-byte blob
        send blob as one control message
   Peer answers
        rsa_decrypt(blob with own private key) ->  same 16-byte AES key
   Both sides now share the AES key
        outgoing audio: aes_ctr_crypt() just before tcp_send_audio()
        incoming audio: aes_ctr_crypt() just before writing play_buf
""".strip()))

story.append(P("6.3 — Encryption is symmetric in code", h2))
story.append(P("AES-CTR mode has a convenient property: the <b>same function</b> both "
               "encrypts and decrypts. The sender calls <code>aes_ctr_crypt()</code> on "
               "plain audio to scramble it; the receiver calls the identical function on "
               "the scrambled bytes to recover the audio. No separate decrypt routine is "
               "needed for the audio stream.", body))

# ============== Section 7 ==============
story.append(P("7. Summary", h1))

summ = [
    ['Term', 'One-line meaning'],
    ['Encryption', 'Scrambling data so interceptors see only garbage'],
    ['Key', 'The secret number that controls the scrambling'],
    ['Symmetric (AES)', 'One shared key, very fast — used for the audio stream'],
    ['Asymmetric (RSA)', 'Public + private key pair, slow — used to deliver the AES key'],
    ['Public key', 'Not secret; encrypts a message for its owner'],
    ['Private key', 'Secret; the only key that can decrypt what the public key locked'],
    ['Hybrid scheme', 'RSA delivers the AES key once; AES then encrypts all the audio'],
    ['crypto_keys.h', 'C header with the RSA key numbers, generated on PC by keygen.py'],
]
story.append(make_table(summ, col_widths=[3.8 * cm, 10.7 * cm]))

story.append(Spacer(1, 0.4 * cm))
story.append(P("<b>Next step:</b> run <code>keygen.py</code> on the PC to produce "
               "<code>crypto_keys.h</code>, then build the <code>crypto.c</code> / "
               "<code>crypto.h</code> module and self-test the RSA round-trip before "
               "wiring encryption into the live call.",
               success_style))

story.append(Spacer(1, 0.5 * cm))
story.append(P("End of Phase 7 — Encryption Explained.", note_style))


# ---------------- BUILD ----------------
doc = SimpleDocTemplate(OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=2 * cm, bottomMargin=2 * cm,
    title="Phase 7 — Encryption Explained",
    author="AAST Embedded Systems Team")

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {OUT}")