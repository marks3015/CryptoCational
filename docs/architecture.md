# System Architecture / Arquitetura do Sistema

## English
This document describes the technical structure and folder organization of the **CryptoCational** project. The application is built using a modular design to separate the cryptographic logic from the user interface.

### Folder Structure
- **/assets**: Contains visual resources.
  - `/icons`: SVG icons for buttons and menu navigation.
  - `/images`: Branding assets, including the official application logo.
- **/core**: The logical heart of the system.
  - `vigenere.py`: Implementation of Vigenère encryption and decryption algorithms.
  - `aes.py`: Pure Python AES-128 implementation (FIPS-197) with configurable rounds, S-box, ShiftRows, MixColumns in GF(2⁸), and key expansion.
  - `modes.py`: Block cipher modes of operation — ECB and CTR (standard and visual didactic variants).
  - `bmp_utils.py`: Image conversion and BMP header manipulation for the AES selfie visualization pipeline.
  - `translator.py`: Internationalization (i18n) system for multi-language support.
  - `frequency.py`: Data and logic for character frequency analysis.
  - `attack.py`: Cryptanalysis algorithms (IC method, Chi-Squared attack).
  - `utils.py`: General helper functions for text processing.
  - `/rsa`: RSA-OAEP sub-package (pure Python, no external cryptographic dependencies).
    - `keys.py`: Prime generation with Miller-Rabin (k=64 rounds) and RSA-2048 key pair generation.
    - `oaep.py`: Full OAEP encoding/decoding (RFC 8017) using SHA3-256 and MGF1.
    - `cipher.py`: RSA-OAEP encryption and decryption via modular exponentiation.
    - `signature.py`: Digital signature and verification; PEM-like signed document format.
- **/data**: Static resources.
  - `letter_frequencies.json`: Statistical letter distribution benchmarks for analysis.
- **/docs**: Detailed technical documentation in Markdown.
- **/ui**: UI components built with PySide6.
  - `/pages`: Individual screens (Home, Cripto, Decripto, AES, Settings, RSA-OAEP).
    - `ui_rsa.py`: RSA page with five sub-pages (Home, Key Generation, Encrypt, Decrypt, Sign/Verify). Includes `RSAKeyWorker(QThread)` for non-blocking key generation.
  - `/popups`: Custom modal dialogs for data entry.
- `main.py`: Entry point that orchestrates the primary window and navigation.

### Data Flow

#### Text / Classical Cipher Pipeline
1. **Input**: User provides text or loads a `.txt` file into the UI.
2. **Validation**: UI cleans the data and invokes the appropriate `core` module function.
3. **Processing**: The `core` engine performs the cryptographic or statistical operation.
4. **Display**: The result is returned and rendered in UI read-only panels or charts.

#### RSA-OAEP Asymmetric Encryption Pipeline
1. **Key Generation**: `RSAKeyWorker` (QThread) calls `core/rsa/keys.py → generate_keypair(bits=1024)`, running Miller-Rabin primality tests to produce two 1024-bit primes and computes the 2048-bit RSA key pair.
2. **Serialisation**: Both public and private keys are serialised to JSON (Base64-encoded `n` and `exp` integers) for display and clipboard copy.
3. **Encryption**: User provides plaintext and pastes the public key JSON. `core/rsa/cipher.py → rsa_encrypt` applies OAEP padding then modular exponentiation (`pow(m, e, n)`). Result is rendered as Base64.
4. **Decryption**: User provides Base64 ciphertext and private key JSON. `rsa_decrypt` reverses the operation: modular exponentiation → OAEP decode → UTF-8 decode.
5. **Digital Signature**: `core/rsa/signature.py → _sign_hash` computes `SHA3-256(message)`, OAEP-encodes the digest, then applies `pow(encoded, d, n)`. Output is wrapped in a PEM-like delimited document.
6. **Verification**: The inverse operation recovers the digest via `pow(sig, e, n)` and compares it against `SHA3-256(message)`. Result is displayed with green (valid) or red (invalid) styling.

#### AES Image Visualization Pipeline (Selfie Tab)
1. **Image Selection**: User selects any image file via the UI.
2. **BMP Normalization**: `core/bmp_utils.py` converts the image to a standard 24-bit uncompressed BMP (512×512) and extracts the BMP header (54 bytes) from the raw pixel data.
3. **Encryption**: `core/modes.py` encrypts only the pixel bytes using either ECB or CTR with a configurable number of rounds.
4. **Didactic Visual Mode**: For the selfie demonstration, a special `encrypt_block_visual` function in `core/aes.py` omits `MixColumns` in early rounds, creating a progressive visual effect.
5. **Reconstruction**: The original BMP header is prepended to the encrypted pixel bytes, producing a valid BMP image that Qt renders as a preview.
6. **Export**: The visual result is saved as a PNG file.

---

## Português
Este documento descreve a estrutura técnica e a organização de pastas do projeto **CryptoCational**. A aplicação foi construída com um design modular para separar a lógica criptográfica da interface do usuário.

### Estrutura de Pastas
- **/assets**: Contém recursos visuais da aplicação.
  - `/icons`: Ícones SVG para botões e navegação de menu.
  - `/images`: Ativos de marca, incluindo o logo oficial da aplicação.
- **/core**: O coração lógico do sistema.
  - `vigenere.py`: Implementação dos algoritmos de cifra e decifra de Vigenère.
  - `aes.py`: Implementação pura em Python do AES-128 (FIPS-197) com rodadas configuráveis, S-box, ShiftRows, MixColumns em GF(2⁸) e expansão de chave.
  - `modes.py`: Modos de operação de cifra de bloco — ECB e CTR (variantes padrão e visuais didáticas).
  - `bmp_utils.py`: Conversão de imagens e manipulação de header BMP para o pipeline de visualização do AES selfie.
  - `translator.py`: Sistema de internacionalização (i18n) para suporte multi-idioma.
  - `frequency.py`: Dados e lógica para análise de frequência de caracteres.
  - `attack.py`: Algoritmos de criptoanálise (Método IC, ataque Qui-Quadrado).
  - `utils.py`: Funções auxiliares gerais para processamento de texto.
  - `/rsa`: Sub-pacote RSA-OAEP (Python puro, sem dependências criptográficas externas).
    - `keys.py`: Geração de primos via Miller-Rabin (k=64 rounds) e geração de par de chaves RSA-2048.
    - `oaep.py`: Codificação/decodificação OAEP completa (RFC 8017) usando SHA3-256 e MGF1.
    - `cipher.py`: Cifração e decifração RSA-OAEP via exponenciação modular.
    - `signature.py`: Assinatura digital e verificação; formato de documento assinado estilo PEM.
- **/data**: Recursos estáticos.
  - `letter_frequencies.json`: Benchmarks estatísticos de distribuição de letras para análise.
- **/docs**: Documentação técnica detalhada em Markdown.
- **/ui**: Componentes de interface construídos com PySide6.
  - `/pages`: Telas individuais (Início, Cripto, Decripto, AES, Configurações, RSA-OAEP).
    - `ui_rsa.py`: Página RSA com cinco sub-páginas (Início, Gerar Chaves, Cifrar, Decifrar, Assinar/Verificar). Inclui `RSAKeyWorker(QThread)` para geração de chaves sem bloquear a UI.
  - `/popups`: Diálogos modais personalizados para entrada de dados.
- `main.py`: Ponto de entrada que orquestra a janela principal e navegação.

### Fluxo de Dados

#### Pipeline de Texto / Cifra Clássica
1. **Entrada**: O usuário fornece texto ou carrega um arquivo `.txt`.
2. **Validação**: A UI limpa os dados e invoca a função apropriada do módulo `core`.
3. **Processamento**: O motor `core` realiza a operação criptográfica ou estatística.
4. **Exibição**: O resultado é retornado e renderizado em painéis ou gráficos da UI.

#### Pipeline de Criptografia Assimétrica RSA-OAEP
1. **Geração de Chaves**: `RSAKeyWorker` (QThread) chama `core/rsa/keys.py → generate_keypair(bits=1024)`, executando testes de primalidade Miller-Rabin para produzir dois primos de 1024 bits e calcular o par de chaves RSA-2048.
2. **Serialização**: Ambas as chaves são serializadas como JSON (inteiros `n` e `exp` em Base64) para exibição e cópia.
3. **Cifração**: O usuário fornece o plaintext e cola o JSON da chave pública. `core/rsa/cipher.py → rsa_encrypt` aplica o padding OAEP e exponenciação modular (`pow(m, e, n)`). O resultado é exibido em Base64.
4. **Decifração**: O usuário fornece o ciphertext em Base64 e o JSON da chave privada. `rsa_decrypt` reverte a operação: exponenciação modular → decodificação OAEP → decodificação UTF-8.
5. **Assinatura Digital**: `core/rsa/signature.py → _sign_hash` calcula `SHA3-256(mensagem)`, codifica o digest com OAEP e aplica `pow(encoded, d, n)`. A saída é encapsulada em um documento delimitado estilo PEM.
6. **Verificação**: A operação inversa recupera o digest via `pow(sig, e, n)` e o compara com `SHA3-256(mensagem)`. O resultado é exibido em verde (válido) ou vermelho (inválido).

#### Pipeline de Visualização de Imagem AES (Aba Selfie)
1. **Seleção da Imagem**: O usuário seleciona qualquer arquivo de imagem pela UI.
2. **Normalização BMP**: `core/bmp_utils.py` converte a imagem para um BMP 24-bit não comprimido padrão (512×512) e extrai o header BMP (54 bytes) dos dados brutos de pixel.
3. **Cifração**: `core/modes.py` cifra apenas os bytes de pixel usando ECB ou CTR com um número configurável de rodadas.
4. **Modo Visual Didático**: Para a demonstração com selfie, uma função especial `encrypt_block_visual` em `core/aes.py` omite o `MixColumns` nas rodadas iniciais, criando um efeito visual progressivo.
5. **Reconstrução**: O header BMP original é prefixado aos pixels cifrados, produzindo uma imagem BMP válida que o Qt renderiza como preview.
6. **Exportação**: O resultado visual é salvo como arquivo PNG.
