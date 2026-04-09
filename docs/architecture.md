# System Architecture / Arquitetura do Sistema

## English
This document describes the technical structure and folder organization of the **CryptoCational** project. The application is built using a modular design to separate the cryptographic logic from the user interface.

### Folder Structure
- **/assets**: Contains visual resources.
  - `/icons`: SVG icons for buttons and menu navigation.
  - `/images`: Branding assets, including the official application logo.
- **/core**: The logical heart of the system.
  - `vigenere.py`: Implementation of Vigenère encryption and decryption algorithms.
  - `translator.py`: Internationalization (i18n) system for multi-language support.
  - `frequency.py`: Data and logic for character frequency analysis.
  - `attack.py`: Cryptanalysis algorithms (IC method, Chi-Squared attack).
  - `utils.py`: General helper functions for text processing.
- **/data**: Static resources.
  - `letter_frequencies.json`: Statistical letter distribution benchmarks for analysis.
- **/docs**: Detailed technical documentation in Markdown.
- **/ui**: UI components built with PySide6.
  - `/pages`: Individual screens (Home, Cripto, Decripto, Settings).
  - `/popups`: Custom modal dialogs for data entry.
- `main.py`: Entry point that orchestrates the primary window and navigation.

### Data Flow
1. **Input**: User provides text or loads a `.txt` file into the UI.
2. **Validation**: UI cleans the data and invokes the appropriate `core` module function.
3. **Processing**: The `core` engine performs the cryptographic or statistical operation.
4. **Display**: The result is returned and rendered in UI read-only panels or charts.

---

## Português
Este documento descreve a estrutura técnica e a organização de pastas do projeto **CryptoCational**. A aplicação foi construída com um design modular para separar a lógica criptográfica da interface do usuário.

### Estrutura de Pastas
- **/assets**: Contém recursos visuais da aplicação.
  - `/icons`: Ícones SVG para botões e navegação de menu.
  - `/images`: Ativos de marca, incluindo o logo oficial da aplicação.
- **/core**: O coração lógico do sistema.
  - `vigenere.py`: Implementação dos algoritmos de cifra e decifra de Vigenère.
  - `translator.py`: Sistema de internacionalização (i18n) para suporte multi-idioma.
  - `frequency.py`: Dados e lógica para análise de frequência de caracteres.
  - `attack.py`: Algoritmos de criptoanálise (Método IC, ataque Qui-Quadrado).
  - `utils.py`: Funções auxiliares gerais para processamento de texto.
- **/data**: Recursos estáticos.
  - `letter_frequencies.json`: Benchmarks estatísticos de distribuição de letras para análise.
- **/docs**: Documentação técnica detalhada em Markdown.
- **/ui**: Componentes de interface construídos com PySide6.
  - `/pages`: Telas individuais (Início, Cripto, Decripto, Configurações).
  - `/popups`: Diálogos modais personalizados para entrada de dados.
- `main.py`: Ponto de entrada que orquestra a janela principal e navegação.

### Fluxo de Dados
1. **Entrada**: O usuário fornece texto ou carrega um arquivo `.txt`.
2. **Validação**: A UI limpa os dados e invoca a função apropriada do módulo `core`.
3. **Processamento**: O motor `core` realiza a operação criptográfica ou estatística.
4. **Exibição**: O resultado é retornado e renderizado em painéis ou gráficos da UI.
