# CryptoCational

## English
**CryptoCational** is a modern, interactive educational tool designed for studying and applying cryptographic algorithms. Built with **PySide6**, it emphasizes a minimalist user experience (UX), rigorous statistical honesty, and deep visual insight into how ciphers actually work.

The application implements **Vigenère** (classical cipher with cryptanalysis), **AES-128** (modern block cipher from scratch), and **RSA-OAEP** (asymmetric encryption and digital signatures from scratch), providing a complete hands-on cryptography toolkit.

### 🎯 Vision & Scalability
The project is designed to scale dynamically. Each algorithm is implemented as an independent module under `core/` with a dedicated UI page, making it straightforward to add new ciphers and analyses in future releases.

![Logo](assets/images/logo.png)

### 🚀 Key Features
- **RSA-OAEP from Scratch**: Pure Python RSA-2048 with OAEP padding (SHA3-256 / MGF1). Key generation via Miller-Rabin primality testing, encryption, decryption, and digital signatures — all without external cryptographic libraries.
- **AES-128 from Scratch**: Pure Python implementation of the Advanced Encryption Standard (FIPS-197) with configurable rounds (1–14). Supports ECB and CTR modes.
- **Visual Didactic Cipher**: A unique pedagogical mode that gradually introduces `MixColumns`, allowing students to *see* how each AES transformation (substitution, shift, diffusion) affects an image step-by-step across 3, 5, 9, and 13 rounds.
- **Selfie Encryption Tests**: Upload any image and watch it being encrypted under ECB and CTR with varying round counts — visualizing structural leakage vs. noise.
- **Format-Preserving Vigenère**: Encrypt texts while maintaining spaces, punctuation, casing, and line breaks.
- **Statistical Cryptanalysis**: Integrated tools for breaking Vigenère using Index of Coincidence (IC) and Chi-Squared ($\chi^2$) frequency analysis.
- **Modern UI**: A sleek, responsive interface designed for focus and productivity.
- **Bilingual Core**: Full interface and documentation support for both English and Portuguese.

### 📂 Technical Documentation
Explore the `docs` directory and project manifests for in-depth insights:
- 📐 [**Architecture Guide**](docs/architecture.md): Overview of modular design and data flows.
- 📖 [**User Manual**](docs/usage.md): Step-by-step instructions for all features.
- 🔐 [**Encryption Deep-Dive**](docs/encryption.md): Mathematical breakdown (Vigenère, AES, RSA-OAEP).
- 🔓 [**Decryption Deep-Dive**](docs/decryption.md): Statistical attack logic.
- 🛡️ [**AES Technical Report**](docs/aes_report.md): AES-128 implementation, modes, and visual methodology.
- 🔑 [**RSA-OAEP Technical Report**](docs/rsa_report.md): RSA-2048, Miller-Rabin, OAEP, and digital signatures.
- 🤝 [**Contributing Guide**](CONTRIBUTING.md): How to participate in the project.
- 📚 [**References**](REFERENCES.md): External cryptographic resources.

### 🛠️ Installation & Execution
1. Requirements: Python 3.10+
2. Install dependencies: `pip install -r requirements.txt`
3. Launch: `python main.py`

---

## Português
**CryptoCational** é uma ferramenta educacional moderna e interativa projetada para o estudo e aplicação de algoritmos criptográficos. Construída com **PySide6**, enfatiza uma experiência de usuário (UX) minimalista, rigor estatístico e uma compreensão visual profunda de como as cifras funcionam internamente.

A aplicação implementa **Vigenère** (cifra clássica com criptoanálise), **AES-128** (cifra moderna de bloco implementada do zero) e **RSA-OAEP** (criptografia assimétrica e assinaturas digitais do zero), formando um kit completo de criptografia prática.

### 🎯 Visão e Escalabilidade
O projeto foi desenvolvido para escalar dinamicamente. Cada algoritmo é implementado como um módulo independente em `core/` com uma página de UI dedicada, facilitando a adição de novas cifras e análises em lançamentos futuros.

### 🚀 Principais Funcionalidades
- **RSA-OAEP do Zero**: RSA-2048 em Python puro com padding OAEP (SHA3-256 / MGF1). Geração de chaves via teste de primalidade de Miller-Rabin, cifração, decifração e assinaturas digitais — tudo sem bibliotecas criptográficas externas.
- **AES-128 do Zero**: Implementação pura em Python do Advanced Encryption Standard (FIPS-197) com número de rodadas configurável (1–14). Suporta modos ECB e CTR.
- **Cifra Didática Visual**: Um modo pedagógico exclusivo que introduz gradualmente o `MixColumns`, permitindo que o estudante *veja* como cada transformação do AES (substituição, deslocamento, difusão) afeta uma imagem passo a passo em 3, 5, 9 e 13 rodadas.
- **Testes de Cifração com Selfie**: Faça upload de qualquer imagem e observe-a sendo cifrada em ECB e CTR com diferentes contagens de rodadas — visualizando vazamento estrutural vs. ruído.
- **Criptografia com Preservação de Formato (Vigenère)**: Criptografe textos mantendo espaços, pontuação, maiúsculas/minúsculas e quebras de linha.
- **Criptoanálise Estatística**: Ferramentas integradas para quebrar Vigenère usando Índice de Coincidência (IC) e análise de frequência Qui-Quadrado ($\chi^2$).
- **UI Moderna em Dark-Mode**: Uma interface elegante e responsiva projetada para foco e produtividade.
- **Core Bilíngue**: Suporte total de interface e documentação para Inglês e Português.

### 📂 Documentação Técnica
Explore o diretório `docs` e os manifestos do projeto para insights detalhados:
- 📐 [**Guia de Arquitetura**](docs/architecture.md): Visão geral do design modular.
- 📖 [**Manual do Usuário**](docs/usage.md): Instruções passo a passo.
- 🔐 [**Deep-Dive de Cifra**](docs/encryption.md): Detalhamento matemático (Vigenère, AES e RSA-OAEP).
- 🔓 [**Deep-Dive de Decifra**](docs/decryption.md): Explicação dos ataques estatísticos.
- 🛡️ [**Relatório Técnico do AES**](docs/aes_report.md): Implementação AES-128, modos e metodologia visual.
- 🔑 [**Relatório Técnico RSA-OAEP**](docs/rsa_report.md): RSA-2048, Miller-Rabin, OAEP e assinaturas digitais.
- 🤝 [**Guia de Contribuição**](CONTRIBUTING.md): Como participar do projeto.
- 📚 [**Referências**](REFERENCES.md): Recursos criptográficos externos.

### 🛠️ Instalação e Execução
1. Requisitos: Python 3.10+
2. Instale as dependências: `pip install -r requirements.txt`
3. Inicie: `python main.py`
