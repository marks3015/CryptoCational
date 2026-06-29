# Relatório Técnico: Implementação RSA-OAEP no CryptoCational

## 1. Descrição do RSA-OAEP

O **RSA-OAEP** (Optimal Asymmetric Encryption Padding) é um esquema de criptografia assimétrica que combina a primitiva RSA com um padding probabilístico, garantindo segurança semântica (IND-CCA2) contra ataques de texto cifrado escolhido. No contexto deste trabalho, implementamos **RSA-2048** com OAEP (RFC 8017) inteiramente em Python puro, sem depender de bibliotecas criptográficas externas.

### Parâmetros Adotados

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| Tamanho do módulo `n` | 2048 bits | Produto de dois primos de 1024 bits. |
| Expoente público `e` | 65537 (F₄) | Primo de Fermat, padrão na indústria. |
| Função de hash | SHA3-256 | Usada tanto no OAEP quanto nas assinaturas. |
| Tamanho do hash `hLen` | 32 bytes | Digest size do SHA3-256. |
| Tamanho máximo da mensagem | 190 bytes | `k − 2·hLen − 2`, onde `k = 256` bytes. |
| Teste de primalidade | Miller-Rabin | `k = 64` rounds de testemunhas aleatórias. |

### Por que OAEP?

O RSA "textbook" (sem padding) é deterministico: a mesma mensagem sempre gera o mesmo ciphertext. Isso o torna vulnerável a ataques de dicionário e não atinge segurança semântica. O OAEP resolve isso introduzindo aleatoriedade via uma *seed* criptograficamente segura, fazendo com que cada cifração da mesma mensagem produza um ciphertext diferente.

---

## 2. Descrição da Implementação

### 2.1 Arquitetura dos Módulos

| Arquivo | Responsabilidade |
|---------|------------------|
| `core/rsa/keys.py` | Geração de primos grandes via Miller-Rabin e construção do par de chaves RSA `(n, e)` e `(n, d)`. |
| `core/rsa/oaep.py` | Codificação/decodificação OAEP com SHA3-256 e MGF1, incluindo validação de padding e tamanho de mensagem. |
| `core/rsa/cipher.py` | Primitivas de cifração e decifração RSA-OAEP: exponenciação modular sobre a mensagem OAEP-encoded. |
| `core/rsa/signature.py` | Assinatura e verificação de arquivos usando OAEP + SHA3-256, com formato de documento assinado estilo PEM. |
| `ui/pages/ui_rsa.py` | Interface gráfica da página RSA-OAEP: geração de chaves, cifração, decifração, assinatura e verificação. |
| `main.py` | Integração da página no menu lateral (botão "RSA-OAEP" com ícone `rsa.svg`) e no stack de páginas. |
| `core/translator.py` | Strings bilíngues (PT/EN) para todos os elementos da nova interface. |

### 2.2 Destaques Técnicos

- **Sem bibliotecas criptográficas externas**: Toda a primitiva RSA (geração de primos, exponenciação modular, OAEP, hash) é implementada com a biblioteca padrão do Python (`secrets`, `hashlib`, `pow`).
- **Entropia segura**: Todos os valores aleatórios (primos, seed OAEP) usam `secrets`, projetado para aplicações criptográficas.
- **Exponenciação eficiente**: A função embutida `pow(base, exp, mod)` do Python implementa *square-and-multiply* em C, tornando viável o uso de chaves RSA-2048 em tempo aceitável.
- **Thread worker para geração de chaves**: A geração de primos de 1024 bits é executada em uma `QThread` (`RSAKeyWorker`), evitando bloqueio da interface gráfica.
- **Serialização JSON**: As chaves pública e privada são expostas ao usuário como JSON com os campos `n` e `exp` (ou `n` e `d`), facilitando cópia e transporte.
- **Assinaturas de arquivos**: O módulo `signature.py` suporta assinar e verificar arquivos inteiros, produzindo um documento com delimitadores legíveis (estilo PEM) contendo a mensagem original e a assinatura em Base64.

---

## 3. Detalhes dos Algoritmos

### 3.1 Geração de Primos — Teste de Miller-Rabin

A segurança do RSA depende da dificuldade de fatorar o módulo `n = p × q`. Portanto, `p` e `q` devem ser primos grandes e gerados de forma segura. O projeto utiliza o **teste de primalidade probabilístico de Miller-Rabin** com 64 rounds (`k = 64`).

Dado um candidato ímpar `n`:
1. Escrevemos `n − 1 = 2ʳ · d`, com `d` ímpar.
2. Escolhemos uma testemunha aleatória `a ∈ [2, n − 2]`.
3. Calculamos `x = aᵈ mod n`.
   - Se `x == 1` ou `x == n − 1`, `n` é provavelmente primo para essa testemunha.
4. Caso contrário, elevamos `x` ao quadrado até `r − 1` vezes.
   - Se em algum momento `x == n − 1`, `n` é provavelmente primo.
   - Se o loop terminar sem atingir `n − 1`, `n` é definitivamente composto.

Com `k = 64`, a probabilidade de um composto passar no teste é menor que `4⁻⁶⁴ ≈ 2.9 × 10⁻³⁹`.

```python
# De core/rsa/keys.py
def _miller_rabin_test(n: int, k: int = 64) -> bool:
    # ... decompõe n-1 = 2^r * d ...
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True
```

### 3.2 Geração do Par de Chaves

```
p, q ← generate_prime(1024)    # dois primos distintos de 1024 bits
n  = p × q                      # módulo de 2048 bits
φ  = (p − 1)(q − 1)
e  = 65537                      # expoente público padrão
d  = e⁻¹ mod φ                  # calculado via pow(e, -1, phi)

Chave pública:  (n, e)
Chave privada:  (n, d)
```

Antes de retornar, o código verifica:
- Se `bits >= 1024` (mínimo seguro).
- Se `e` é ímpar e maior ou igual a 3.
- Se `p != q`.
- Se `e` é coprimo com `φ(n)` (caso contrário, levanta `RuntimeError`).

### 3.3 Padding OAEP

O OAEP funciona como uma "cobertura" aleatória sobre a mensagem antes da exponenciação RSA. Os passos de codificação são:

```
lHash  = SHA3-256(label)                           # label padrão = b""
PS     = b"\x00" × (k − mLen − 2·hLen − 2)        # padding de zeros
DB     = lHash ‖ PS ‖ 0x01 ‖ M                     # data block
seed   = secrets.token_bytes(hLen)                 # 32 bytes aleatórios
maskedDB   = DB   ⊕ MGF1(seed, k − hLen − 1)
maskedSeed = seed ⊕ MGF1(maskedDB, hLen)
EM     = 0x00 ‖ maskedSeed ‖ maskedDB              # encoded message
```

A decodificação reverte as máscaras, verifica `lHash` e o separador `0x01`, e só então extrai a mensagem original. Qualquer inconsistência levanta `ValueError`, evitando vazamento de informação por mensagens de erro diferenciadas.

### 3.4 Cifração e Decifração

A cifração converte a mensagem OAEP em um inteiro e aplica a primitiva RSA:

```python
# De core/rsa/cipher.py
def rsa_encrypt(message: bytes, public_key: PublicKey) -> bytes:
    n, e = public_key
    encoded = oaep_encode(message, n)
    ciphertext_int = pow(int.from_bytes(encoded, byteorder="big"), e, n)
    return ciphertext_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
```

A decifração aplica o expoente privado `d` e depois decodifica o OAEP:

```python
def rsa_decrypt(ciphertext: bytes, private_key: PrivateKey) -> bytes:
    n, d = private_key
    ciphertext_int = int.from_bytes(ciphertext, byteorder="big")
    encoded_int = pow(ciphertext_int, d, n)
    encoded = encoded_int.to_bytes((n.bit_length() + 7) // 8, byteorder="big")
    return oaep_decode(encoded, n)
```

### 3.5 Assinatura Digital

O esquema de assinatura do projeto usa o paradigma **hash-then-sign**: em vez de assinar a mensagem diretamente, assinamos o hash SHA3-256 do arquivo.

```
H      = SHA3-256(arquivo)
σ      = OAEP_encode(H, n)ᵈ mod n   # assinatura

Verificar:
H'     = OAEP_decode(σᵉ mod n, n)
válido sse H' == SHA3-256(arquivo)
```

Isso garante:
- **Integridade**: qualquer alteração no arquivo invalida a assinatura.
- **Autenticidade**: apenas o detentor de `d` pode ter gerado `σ`.
- **Não-repúdio**: o signatário não pode negar ter assinado o documento.

O arquivo assinado segue um formato legível inspirado em PEM:

```
-----BEGIN RSA SIGNED MESSAGE-----
<Base64 da mensagem original>
-----BEGIN RSA SIGNATURE-----
<Base64 da assinatura>
-----END RSA SIGNED MESSAGE-----
```

---

## 4. Instruções de Uso

### 4.1 Gerar um Par de Chaves

1. Navegue até a aba **RSA-OAEP** pelo menu lateral.
2. Na tela inicial, clique em **Gerar Par de Chaves**.
3. Aguarde a geração (2–15 segundos, executada em background).
4. Copie a **Chave Pública** (JSON) para compartilhar.
5. Copie a **Chave Privada** (JSON) e guarde em local seguro — **nunca a compartilhe**.

### 4.2 Cifrar uma Mensagem

1. Na tela inicial RSA, clique em **Cifrar**.
2. Insira a mensagem no campo apropriado (máximo **190 bytes** para RSA-2048).
3. Cole a **chave pública** do destinatário no painel direito.
4. Clique em **Cifrar**. O resultado em Base64 aparecerá no painel inferior.
5. Envie o texto cifrado ao destinatário.

### 4.3 Decifrar uma Mensagem

1. Na tela inicial RSA, clique em **Decifrar**.
2. Cole o ciphertext em Base64 no campo esquerdo.
3. Cole sua **chave privada** no campo direito.
4. Clique em **Decifrar**. A mensagem original será exibida.

### 4.4 Assinar e Verificar um Arquivo

1. Na tela inicial RSA, clique em **Assinar / Verificar**.
2. Para assinar:
   - Escolha o modo **Assinar**.
   - Cole sua **chave privada**.
   - Clique em **Assinar Mensagem**.
   - O documento assinado (com delimitadores PEM) é gerado.
3. Para verificar:
   - Escolha o modo **Verificar**.
   - Cole o documento assinado completo, incluindo os delimitadores.
   - Cole a **chave pública** do remetente.
   - Clique em **Verificar Assinatura**.
   - O resultado indicará se a assinatura é **válida** ou **inválida**.

---

## 5. Validação

A implementação foi validada com:

- **Round-trip tests**: cifração seguida de decifração recupera a mensagem original para diversos tamanhos de entrada (1 a 190 bytes).
- **Testes de assinatura**: assinatura de arquivos seguida de verificação confirma autenticidade; alterações no arquivo fazem a verificação falhar.
- **Geração de chaves**: verificação de que `n` possui 2048 bits, que `e = 65537` é coprimo com `φ(n)`, e que `d · e ≡ 1 (mod φ(n))`.
- **OAEP determinístico para sanity check**: dada uma seed fixa, a codificação/decodificação OAEP é reversível e consistente.
