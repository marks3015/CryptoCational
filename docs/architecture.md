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
- **/data**: Static resources.
  - `letter_frequencies.json`: Statistical letter distribution benchmarks for analysis.
- **/docs**: Detailed technical documentation in Markdown.
- **/ui**: UI components built with PySide6.
  - `/pages`: Individual screens (Home, Cripto, Decripto, AES, Settings).
  - `/popups`: Custom modal dialogs for data entry.
- `main.py`: Entry point that orchestrates the primary window and navigation.

### Data Flow

#### Text / Classical Cipher Pipeline
1. **Input**: User provides text or loads a `.txt` file into the UI.
2. **Validation**: UI cleans the data and invokes the appropriate `core` module function.
3. **Processing**: The `core` engine performs the cryptographic or statistical operation.
4. **Display**: The result is returned and rendered in UI read-only panels or charts.

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
- **/data**: Recursos estáticos.
  - `letter_frequencies.json`: Benchmarks estatísticos de distribuição de letras para análise.
- **/docs**: Documentação técnica detalhada em Markdown.
- **/ui**: Componentes de interface construídos com PySide6.
  - `/pages`: Telas individuais (Início, Cripto, Decripto, AES, Configurações).
  - `/popups`: Diálogos modais personalizados para entrada de dados.
- `main.py`: Ponto de entrada que orquestra a janela principal e navegação.

### Fluxo de Dados

#### Pipeline de Texto / Cifra Clássica
1. **Entrada**: O usuário fornece texto ou carrega um arquivo `.txt`.
2. **Validação**: A UI limpa os dados e invoca a função apropriada do módulo `core`.
3. **Processamento**: O motor `core` realiza a operação criptográfica ou estatística.
4. **Exibição**: O resultado é retornado e renderizado em painéis ou gráficos da UI.

#### Pipeline de Visualização de Imagem AES (Aba Selfie)
1. **Seleção da Imagem**: O usuário seleciona qualquer arquivo de imagem pela UI.
2. **Normalização BMP**: `core/bmp_utils.py` converte a imagem para um BMP 24-bit não comprimido padrão (512×512) e extrai o header BMP (54 bytes) dos dados brutos de pixel.
3. **Cifração**: `core/modes.py` cifra apenas os bytes de pixel usando ECB ou CTR com um número configurável de rodadas.
4. **Modo Visual Didático**: Para a demonstração com selfie, uma função especial `encrypt_block_visual` em `core/aes.py` omite o `MixColumns` nas rodadas iniciais, criando um efeito visual progressivo.
5. **Reconstrução**: O header BMP original é prefixado aos pixels cifrados, produzindo uma imagem BMP válida que o Qt renderiza como preview.
6. **Exportação**: O resultado visual é salvo como arquivo PNG.
