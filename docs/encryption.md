# Encryption Implementation Detail / Detalhes da Implementação de Cifra

## English

### 1. Alphabet Normalization & Character Mapping
The core engine (`core/vigenere.py`) operates strictly on a 26-character Latin alphabet (A-Z). To ensure high reliability, the system performs rigorous normalization via the `normalize_text` and `remove_accents` functions.

- **Accent Removal**: A static mapping (`accent_map`) is used to convert characters like `á`, `ã`, `â` to `a`, and `ç` to `c`. This prevents the cipher from breaking due to non-standard indices.
- **Regex Filtering**: After accent removal, the system applies `re.sub(r'[^A-Za-z]', '', text)` to extract a clean string for pure mathematical operations.

```python
# From core/vigenere.py
def normalize_text(text: str) -> str:
    # Mapping accented to non-accented
    accent_map = {'á': 'a', 'à': 'a', 'ã': 'a', ...}
    normalized = text
    for accented, plain in accent_map.items():
        normalized = normalized.replace(accented, plain)
    
    # regex to keep only A-Z
    normalized = re.sub(r'[^A-Za-z]', '', normalized)
    return normalized.upper()
```

### 2. Format-Preserving Vigenère Logic
Unlike standard academic implementations, the `encrypt_preserve_format` function maintains the visual integrity of the user's input (casing, spaces, numbers, and punctuation).

**The Algorithm Workflow:**
1. **Key Validation**: The key is normalized to A-Z. If empty, a `ValueError` is raised.
2. **Key Expansion**: The key is repeated modularly using `(normalized_key * ((len(text) // len(normalized_key)) + 1))`.
3. **Iterative Shift**: 
   - A `key_index` tracks progress through the key ONLY when an alphabetic character is encountered.
   - For each character $P_i$ in the plaintext:
     - If $P_i$ is alphabetic:
       - Determine base (ASCII 65 for 'A', 97 for 'a') using `char.isupper()`.
       - Calculate shift: $E_i = (P_i - \text{base} + K_{j \pmod m}) \pmod{26}$.
       - Update `key_index`.
     - Else:
       - Append $P_i$ to result without modification and without advancing `key_index`.

```python
# Core logic snippet
for char in text:
    if char.isalpha():
        is_upper = char.isupper()
        base = ord('A') if is_upper else ord('a')
        text_num = ord(char) - base
        key_num = ord(key_expanded[key_index]) - ord('A')
        
        # Vigenère Formula Core
        encrypted_num = (text_num + key_num) % 26
        ciphertext.append(chr(encrypted_num + base))
        key_index += 1
    else:
        ciphertext.append(char)
```

### 3. AES-128 Implementation from Scratch

The `core/aes.py` module implements the Advanced Encryption Standard (FIPS-197) entirely in pure Python, without relying on external cryptographic libraries. It supports configurable rounds (`1` to `14`), enabling educational experiments with reduced-round variants.

#### 3.1 State Representation & Transformations

AES operates on a 4×4 matrix of bytes called the **state**. Each transformation is applied in-place:

1. **SubBytes**: Non-linear byte substitution using a 256-byte S-box.
2. **ShiftRows**: Cyclic left shift of rows (row 0 by 0, row 1 by 1, row 2 by 2, row 3 by 3).
3. **MixColumns**: Matrix multiplication in the finite field GF(2⁸) with irreducible polynomial `x⁸ + x⁴ + x³ + x + 1` (`0x11B`). Each column is multiplied by a fixed polynomial matrix:
   ```
   [02 03 01 01]
   [01 02 03 01]
   [01 01 02 03]
   [03 01 01 02]
   ```
4. **AddRoundKey**: XOR the state with a 16-byte round key.

Multiplication in GF(2⁸) is implemented via bitwise shift-and-reduce:

```python
# From core/aes.py
def _gmul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a <<= 1
        if hi:
            a ^= 0x1B  # 0x11B without x^8 term
        b >>= 1
    return p & 0xFF
```

Pre-computed lookup tables (`_MUL2`, `_MUL3`, `_MUL9`, `_MUL11`, `_MUL13`, `_MUL14`) optimize `MixColumns` and `InvMixColumns`.

#### 3.2 Key Expansion (Generalized)

The `key_expansion` function generates `(num_rounds + 1)` 128-bit round keys from a 16-byte cipher key. It follows the standard AES Key Schedule but is generalized to support any `num_rounds` between 1 and 14:

```python
# Simplified excerpt from core/aes.py
def key_expansion(key: bytes, num_rounds: int) -> List[bytes]:
    w = [key[i:i+4] for i in range(0, 16, 4)]
    for i in range(4, 4 * (num_rounds + 1)):
        temp = w[i - 1]
        if i % 4 == 0:
            temp = _sub_word(_rot_word(temp))
            temp = bytes(a ^ b for a, b in zip(temp, _rcon(i // 4)))
        w.append(bytes(a ^ b for a, b in zip(w[i - 4], temp)))
    # Pack words into 16-byte round keys
    return [b''.join(w[i:i+4]) for i in range(0, len(w), 4)]
```

#### 3.3 Block Encryption

The `encrypt_block` function applies the round transformations sequentially:

```python
# Excerpt from core/aes.py
def encrypt_block(block: bytes, round_keys: List[bytes], num_rounds: int) -> bytes:
    state = _bytes_to_state(block)
    _add_round_key(state, round_keys[0])
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[r])
    # Final round (no MixColumns)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])
    return _state_to_bytes(state)
```

#### 3.4 Modes of Operation

**ECB (Electronic Codebook)** encrypts each 16-byte block independently. Identical plaintext blocks yield identical ciphertext blocks, making patterns visible in images. Padding uses PKCS#7.

**CTR (Counter Mode)** turns AES into a stream cipher. A 16-byte nonce is encrypted to produce a keystream, which is XORed with the plaintext. No padding is required, and the visual result is uniformly noisy because every block is XORed with a unique keystream block.

```python
# From core/modes.py
def aes_ctr_encrypt(data: bytes, key: bytes, num_rounds: int = 10, iv=None):
    round_keys = key_expansion(key, num_rounds)
    nonce = iv or os.urandom(16)
    output = bytearray()
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        keystream = encrypt_block(nonce, round_keys, num_rounds)
        output.extend(b ^ k for b, k in zip(block, keystream))
        nonce = _inc_nonce(nonce)
    return bytes(output), iv
```

### 4. The Didactic Visual Cipher (Innovation)

A standard AES with only 3 rounds already produces ciphertext that is statistically indistinguishable from random noise. While cryptographically desirable, this makes it impossible to *visually* demonstrate how each transformation contributes to the final scrambled image.

To solve this, the project introduces **`encrypt_block_visual`**, a pedagogical variant that **omits `MixColumns` in intermediate rounds below a threshold** (`mixcol_after`, default 3). This creates a progressive visual effect:

| Rounds | MixColumns Active From | Visual Effect |
|--------|------------------------|---------------|
| 3 | Never | Only SubBytes + ShiftRows + AddRoundKey. Colours are permuted and rows shifted, but local structure (blocks, edges) remains visible. |
| 5 | Round 3 onward | Colours begin to blend across columns. Shapes blur but large features survive. |
| 9 | Round 3 onward | Strong diffusion; most structure lost; approaching noise. |
| 13 | Round 3 onward | Full diffusion; visually indistinguishable from standard AES. |

```python
# From core/aes.py — the didactic visual variant
def encrypt_block_visual(block: bytes, round_keys: List[bytes],
                         num_rounds: int, mixcol_after: int = 3) -> bytes:
    state = _bytes_to_state(block)
    _add_round_key(state, round_keys[0])
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        if r >= mixcol_after:
            _mix_columns(state)
        _add_round_key(state, round_keys[r])
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])
    return _state_to_bytes(state)
```

This approach preserves the **exact same key schedule and round structure** as real AES; the only difference is the conditional omission of `MixColumns` in early rounds. When the threshold is reached, the cipher converges to standard AES behaviour, ensuring that the 13-round output is genuinely secure.

### 5. Image Visualization Pipeline

For the selfie demonstration:

1. **BMP Conversion**: Any input image is scaled to 512×512 and converted to a 24-bit uncompressed BMP.
2. **Header Extraction**: The 54-byte BMP header is preserved. Only the raw pixel bytes are encrypted.
3. **Encryption**: Pixel bytes are fed through `aes_ecb_encrypt_visual` or `aes_ctr_encrypt_visual`.
4. **Reconstruction**: The original header is prepended to the encrypted pixels, producing a valid BMP that Qt renders.
5. **Export**: The rendered preview is saved as a PNG file.

---

### 6. RSA-OAEP Implementation

The `core/rsa/` sub-package implements RSA-2048 with OAEP padding entirely in pure Python, without any external cryptographic library.

#### 6.1 Prime Generation — Miller-Rabin

Generating large prime numbers is the computational foundation of RSA. The implementation uses the **Miller-Rabin probabilistic primality test** with `k=64` rounds, reducing the false-positive probability to below $4^{-64} \approx 2.9 \times 10^{-39}$.

Given a candidate $n$, write $n - 1 = 2^r \cdot d$ with $d$ odd. For each random witness $a \in [2, n-2]$:

```python
# From core/rsa/keys.py
x = pow(a, d, n)
if x == 1 or x == n - 1:
    continue  # probably prime for this witness
for _ in range(r - 1):
    x = pow(x, 2, n)
    if x == n - 1:
        break
else:
    return False  # definitely composite
```

All random choices use `secrets.randbelow`, ensuring cryptographically strong entropy.

#### 6.2 Key Pair Generation

```
p, q ← generate_prime(1024)   # two distinct 1024-bit primes
n = p × q                      # 2048-bit modulus
φ(n) = (p−1)(q−1)
e = 65537                      # public exponent (Fermat prime F₄)
d ≡ e⁻¹ (mod φ(n))            # private exponent via pow(e, -1, phi)
Public key:  (n, e)
Private key: (n, d)
```

#### 6.3 OAEP Padding (RFC 8017)

The Optimal Asymmetric Encryption Padding ensures semantic security (IND-CCA2) by introducing randomness into each encryption. Using SHA3-256 (`hLen = 32`) and MGF1:

| Symbol | Value | Description |
|--------|-------|-------------|
| `k` | 256 bytes | Modulus byte length for RSA-2048 |
| `hLen` | 32 bytes | SHA3-256 digest size |
| `mLen_max` | 190 bytes | `k − 2·hLen − 2` |

**Encoding steps:**

```
lHash  = SHA3-256(label)                          # label default = b""
PS     = b"\x00" × (k − mLen − 2·hLen − 2)       # zero-padding
DB     = lHash ‖ PS ‖ 0x01 ‖ M                    # data block
seed   = secrets.token_bytes(hLen)                # 32 random bytes
maskedDB   = DB   ⊕ MGF1(seed, k − hLen − 1)
maskedSeed = seed ⊕ MGF1(maskedDB, hLen)
EM     = 0x00 ‖ maskedSeed ‖ maskedDB             # encoded message
```

Decoding reverses these steps and verifies `lHash` and the `0x01` separator, raising `ValueError` on any mismatch.

#### 6.4 Encryption and Decryption

Encryption converts the OAEP-encoded message to an integer and applies modular exponentiation:

```python
# From core/rsa/cipher.py
c = pow(int.from_bytes(oaep_encode(M, n), "big"), e, n)
```

Decryption is the inverse:

```python
m_int = pow(c, d, n)
M = oaep_decode(m_int.to_bytes(k, "big"), n)
```

Python's built-in `pow(base, exp, mod)` implements the square-and-multiply algorithm in C, making it efficient even for 2048-bit exponents.

#### 6.5 Digital Signature

The signature scheme signs the **hash** of the message, not the message directly:

```
Sign:   σ = pow(OAEP_encode(SHA3-256(M), n), d, n)
Verify: H' = OAEP_decode(pow(σ, e, n), n)
        valid iff H' == SHA3-256(M)
```

This provides:
- **Integrity**: Any modification to `M` changes `SHA3-256(M)`, invalidating the signature.
- **Authentication**: Only the holder of `d` (private key) can produce a valid `σ`.
- **Non-repudiation**: The signer cannot deny having signed `M`.

For a full technical walkthrough of the RSA-OAEP integration, see the [RSA Technical Report](rsa_report.md).

---

## Português

### 1. Normalização de Alfabeto e Mapeamento
O motor principal (`core/vigenere.py`) opera estritamente em um alfabeto latino de 26 caracteres (A-Z). Para garantir alta confiabilidade, o sistema realiza uma normalização rigorosa através das funções `normalize_text` e `remove_accents`.

- **Remoção de Acentos**: Um mapeamento estático (`accent_map`) é usado para converter caracteres como `á`, `ã`, `â` para `a`, e `ç` para `c`. Isso evita que a cifra quebre devido a índices não padronizados.
- **Filtragem por Regex**: Após a remoção de acentos, o sistema aplica `re.sub(r'[^A-Za-z]', '', text)` para extrair uma string limpa para as operações matemáticas puras.

```python
# Mapeamento e Regex em core/vigenere.py
def normalize_text(text: str) -> str:
    # Remove acentos e mantém apenas A-Z
    normalized = re.sub(r'[^A-Za-z]', '', text_without_accents)
    return normalized.upper()
```

### 2. Lógica de Vigenère com Preservação de Formato
Ao contrário das implementações acadêmicas padrão, a função `encrypt_preserve_format` mantém a integridade visual da entrada do usuário (maiúsculas/minúsculas, espaços, números e pontuação).

**O Fluxo do Algoritmo:**
1. **Validação da Chave**: A chave é normalizada para A-Z. Se estiver vazia, um `ValueError` é lançado.
2. **Expansão da Chave**: A chave é repetida modularmente usando `(normalized_key * ((len(text) // len(normalized_key)) + 1))`.
3. **Deslocamento Iterativo**:
   - Um `key_index` rastreia o progresso através da chave APENAS quando um caractere alfabético é encontrado.
   - Para cada caractere $P_i$ no texto simples:
     - Se $P_i$ for alfabético:
       - Determina a base (ASCII 65 para 'A', 97 para 'a') usando `char.isupper()`.
       - Calcula o deslocamento: $E_i = (P_i - \text{base} + K_{j \pmod m}) \pmod{26}$.
       - Atualiza o `key_index`.
     - Caso contrário:
       - Adiciona $P_i$ ao resultado sem modificação e sem avançar o `key_index`.

```python
# Lógica de deslocamento (core/vigenere.py)
if char.isalpha():
    # Aplica shift apenas em letras, mantém key_index sincronizado
    encrypted_num = (text_num + key_num) % 26
    ciphertext.append(chr(encrypted_num + base))
    key_index += 1
else:
    ciphertext.append(char)
```

### 3. Implementação AES-128 do Zero

O módulo `core/aes.py` implementa o Advanced Encryption Standard (FIPS-197) inteiramente em Python puro, sem depender de bibliotecas criptográficas externas. Ele suporta rodadas configuráveis (`1` a `14`), possibilitando experimentos educacionais com variantes de rodadas reduzidas.

#### 3.1 Representação do Estado e Transformações

O AES opera em uma matriz 4×4 de bytes chamada **estado**. Cada transformação é aplicada in-place:

1. **SubBytes**: Substituição não linear byte a byte usando uma S-box de 256 bytes.
2. **ShiftRows**: Deslocamento cíclico à esquerda das linhas (linha 0 em 0, linha 1 em 1, linha 2 em 2, linha 3 em 3).
3. **MixColumns**: Multiplicação matricial no corpo finito GF(2⁸) com polinômio irredutível `x⁸ + x⁴ + x³ + x + 1` (`0x11B`). Cada coluna é multiplicada por uma matriz fixa:
   ```
   [02 03 01 01]
   [01 02 03 01]
   [01 01 02 03]
   [03 01 01 02]
   ```
4. **AddRoundKey**: XOR do estado com uma chave de rodada de 16 bytes.

A multiplicação em GF(2⁸) é implementada via deslocamento bit a bit com redução:

```python
# De core/aes.py
def _gmul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a <<= 1
        if hi:
            a ^= 0x1B  # 0x11B sem o termo x^8
        b >>= 1
    return p & 0xFF
```

Tabelas pré-computadas (`_MUL2`, `_MUL3`, `_MUL9`, `_MUL11`, `_MUL13`, `_MUL14`) otimizam `MixColumns` e `InvMixColumns`.

#### 3.2 Expansão de Chave (Generalizada)

A função `key_expansion` gera `(num_rounds + 1)` chaves de rodada de 128 bits a partir de uma chave de 16 bytes. Segue o Key Schedule padrão do AES, mas generalizado para suportar qualquer `num_rounds` entre 1 e 14:

```python
# Trecho simplificado de core/aes.py
def key_expansion(key: bytes, num_rounds: int) -> List[bytes]:
    w = [key[i:i+4] for i in range(0, 16, 4)]
    for i in range(4, 4 * (num_rounds + 1)):
        temp = w[i - 1]
        if i % 4 == 0:
            temp = _sub_word(_rot_word(temp))
            temp = bytes(a ^ b for a, b in zip(temp, _rcon(i // 4)))
        w.append(bytes(a ^ b for a, b in zip(w[i - 4], temp)))
    # Agrupa words em chaves de rodada de 16 bytes
    return [b''.join(w[i:i+4]) for i in range(0, len(w), 4)]
```

#### 3.3 Cifração de Bloco

A função `encrypt_block` aplica as transformações de rodada sequencialmente:

```python
# Trecho de core/aes.py
def encrypt_block(block: bytes, round_keys: List[bytes], num_rounds: int) -> bytes:
    state = _bytes_to_state(block)
    _add_round_key(state, round_keys[0])
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[r])
    # Rodada final (sem MixColumns)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])
    return _state_to_bytes(state)
```

#### 3.4 Modos de Operação

**ECB (Electronic Codebook)** cifra cada bloco de 16 bytes independentemente. Blocos idênticos de plaintext produzem blocos idênticos de ciphertext, tornando padrões visíveis em imagens. O padding usa PKCS#7.

**CTR (Counter Mode)** transforma o AES em uma cifra de fluxo. Um nonce de 16 bytes é cifrado para produzir um keystream, que é XORado com o plaintext. Não requer padding, e o resultado visual é uniformemente ruidoso porque cada bloco é XORado com um bloco único de keystream.

```python
# De core/modes.py
def aes_ctr_encrypt(data: bytes, key: bytes, num_rounds: int = 10, iv=None):
    round_keys = key_expansion(key, num_rounds)
    nonce = iv or os.urandom(16)
    output = bytearray()
    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        keystream = encrypt_block(nonce, round_keys, num_rounds)
        output.extend(b ^ k for b, k in zip(block, keystream))
        nonce = _inc_nonce(nonce)
    return bytes(output), iv
```

### 4. A Cifra Didática Visual (Inovação)

Um AES padrão com apenas 3 rodadas já produz ciphertext estatisticamente indistinguível de ruído aleatório. Embora desejável do ponto de vista criptográfico, isso torna impossível *visualmente* demonstrar como cada transformação contribui para a imagem final embaralhada.

Para resolver isso, o projeto introduz o **`encrypt_block_visual`**, uma variante pedagógica que **omite o `MixColumns` nas rodadas intermediárias abaixo de um limiar** (`mixcol_after`, padrão 3). Isso cria um efeito visual progressivo:

| Rodadas | MixColumns Ativo A Partir De | Efeito Visual |
|---------|------------------------------|---------------|
| 3 | Nunca | Apenas SubBytes + ShiftRows + AddRoundKey. As cores são permutadas e as linhas deslocadas, mas a estrutura local (blocos, bordas) permanece visível. |
| 5 | Rodada 3 em diante | As cores começam a se misturar entre colunas. As formas se desfocam, mas grandes características sobrevivem. |
| 9 | Rodada 3 em diante | Difusão forte; a maior parte da estrutura é perdida; aproximando-se do ruído. |
| 13 | Rodada 3 em diante | Difusão total; visualmente indistinguível do AES padrão. |

```python
# De core/aes.py — a variante didática visual
def encrypt_block_visual(block: bytes, round_keys: List[bytes],
                         num_rounds: int, mixcol_after: int = 3) -> bytes:
    state = _bytes_to_state(block)
    _add_round_key(state, round_keys[0])
    for r in range(1, num_rounds):
        _sub_bytes(state)
        _shift_rows(state)
        if r >= mixcol_after:
            _mix_columns(state)
        _add_round_key(state, round_keys[r])
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[num_rounds])
    return _state_to_bytes(state)
```

Essa abordagem preserva o **mesmo key schedule e estrutura de rodadas** do AES real; a única diferença é a omissão condicional do `MixColumns` nas rodadas iniciais. Quando o limiar é alcançado, a cifra converge ao comportamento padrão do AES, garantindo que a saída de 13 rodadas seja genuinamente segura.

### 5. Pipeline de Visualização de Imagem

Para a demonstração com selfie:

1. **Conversão BMP**: Qualquer imagem de entrada é redimensionada para 512×512 e convertida para um BMP 24-bit não comprimido.
2. **Extração de Header**: Os 54 bytes do header BMP são preservados. Apenas os bytes brutos de pixel são cifrados.
3. **Cifração**: Os bytes de pixel são processados por `aes_ecb_encrypt_visual` ou `aes_ctr_encrypt_visual`.
4. **Reconstrução**: O header BMP original é prefixado aos pixels cifrados, produzindo um BMP válido que o Qt renderiza.
5. **Exportação**: O preview renderizado é salvo como arquivo PNG.

---

### 6. Implementação RSA-OAEP

O sub-pacote `core/rsa/` implementa RSA-2048 com padding OAEP inteiramente em Python puro, sem qualquer biblioteca criptográfica externa.

#### 6.1 Geração de Primos — Miller-Rabin

A geração de grandes números primos é o fundamento computacional do RSA. A implementação usa o **teste de primalidade probabilístico de Miller-Rabin** com `k=64` rounds, reduzindo a probabilidade de falso positivo para menos de $4^{-64} \approx 2.9 \times 10^{-39}$.

Dado um candidato $n$, escrevemos $n - 1 = 2^r \cdot d$ com $d$ ímpar. Para cada testemunha aleatória $a \in [2, n-2]$:

```python
# De core/rsa/keys.py
x = pow(a, d, n)
if x == 1 or x == n - 1:
    continue  # provavelmente primo para esta testemunha
for _ in range(r - 1):
    x = pow(x, 2, n)
    if x == n - 1:
        break
else:
    return False  # definitivamente composto
```

Todas as escolhas aleatórias usam `secrets.randbelow`, garantindo entropia criptograficamente forte.

#### 6.2 Geração do Par de Chaves

```
p, q ← generate_prime(1024)   # dois primos distintos de 1024 bits
n = p × q                      # módulo de 2048 bits
φ(n) = (p−1)(q−1)
e = 65537                      # expoente público (primo de Fermat F₄)
d ≡ e⁻¹ (mod φ(n))            # expoente privado via pow(e, -1, phi)
Chave pública:  (n, e)
Chave privada: (n, d)
```

#### 6.3 Padding OAEP (RFC 8017)

O Optimal Asymmetric Encryption Padding garante segurança semântica (IND-CCA2) introduzindo aleatoriedade em cada cifração. Usando SHA3-256 (`hLen = 32`) e MGF1:

| Símbolo | Valor | Descrição |
|---------|-------|-----------|
| `k` | 256 bytes | Tamanho em bytes do módulo RSA-2048 |
| `hLen` | 32 bytes | Tamanho do digest SHA3-256 |
| `mLen_max` | 190 bytes | `k − 2·hLen − 2` |

**Etapas de codificação:**

```
lHash  = SHA3-256(label)                          # label padrão = b""
PS     = b"\x00" × (k − mLen − 2·hLen − 2)       # zero-padding
DB     = lHash ‖ PS ‖ 0x01 ‖ M                    # data block
seed   = secrets.token_bytes(hLen)                # 32 bytes aleatórios
maskedDB   = DB   ⊕ MGF1(seed, k − hLen − 1)
maskedSeed = seed ⊕ MGF1(maskedDB, hLen)
EM     = 0x00 ‖ maskedSeed ‖ maskedDB             # mensagem codificada
```

A decodificação reverte esses passos e verifica `lHash` e o separador `0x01`, lançando `ValueError` em qualquer divergência.

#### 6.4 Cifração e Decifração

A cifração converte a mensagem codificada pelo OAEP em inteiro e aplica exponenciação modular:

```python
# De core/rsa/cipher.py
c = pow(int.from_bytes(oaep_encode(M, n), "big"), e, n)
```

A decifração é o inverso:

```python
m_int = pow(c, d, n)
M = oaep_decode(m_int.to_bytes(k, "big"), n)
```

O `pow(base, exp, mod)` do Python implementa o algoritmo *square-and-multiply* em C, tornando-o eficiente mesmo para expoentes de 2048 bits.

#### 6.5 Assinatura Digital

O esquema de assinatura assina o **hash** da mensagem, não a mensagem diretamente:

```
Assinar:   σ = pow(OAEP_encode(SHA3-256(M), n), d, n)
Verificar: H' = OAEP_decode(pow(σ, e, n), n)
           válido sse H' == SHA3-256(M)
```

Isso fornece:
- **Integridade**: Qualquer modificação em `M` altera `SHA3-256(M)`, invalidando a assinatura.
- **Autenticação**: Apenas quem possui `d` (chave privada) pode produzir um `σ` válido.
- **Não-repúdio**: O signatário não pode negar ter assinado `M`.

Para um detalhamento técnico completo da integração RSA-OAEP, consulte o [Relatório Técnico RSA](rsa_report.md).
