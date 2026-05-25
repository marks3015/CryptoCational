# User Manual / Manual de Uso

## English
This guide explains how to effectively use the primary features of the **CryptoCational** application.

### 1. Encrypting Text (Vigenère)
1. **Navigation**: Select the **Encrypt** icon from the sidebar menu.
2. **Input**: Either type text directly into the main workspace or use the **Select .TXT File** button to import a local document.
3. **Configuration**:
   - Select the desired **Algorithm** (e.g., Vigenère).
   - Enter your **Key** in the designated configuration card.
4. **Execution**: Click the red **Encrypt** button to trigger the core engine.
5. **Output**: The formatted result will appear in the read-only lower panel. Use **Copy Result** to send it to your system clipboard.

### 2. AES Encryption & Decryption (Text / Files)
1. **Navigation**: Select the **AES** icon (shield) from the sidebar.
2. **Tab "Texto"**: Choose between encrypting/decrypting text or uploading a file.
3. **Configuration**:
   - **Mode**: `ECB` ( Electronic Codebook ) or `CTR` ( Counter Mode ).
   - **Rounds**: Number of AES rounds (1 to 13; standard is 10).
   - **Key**: Plaintext key (up to 16 characters; padded with null bytes or truncated to 16 bytes).
4. **Execution**: Click **Encrypt** or **Decrypt**.
5. **Output**: The result is displayed in hexadecimal. Use **Copy Result** to clipboard.

### 3. AES Selfie Visualization (Didactic Mode)
1. **Navigation**: In the **AES** page, switch to the **"Selfie"** tab.
2. **Select Image**: Click **Select Selfie** and choose any image (PNG, JPG, BMP).
3. **Run Tests**: Click **Run Tests**. The app encrypts the image in 8 configurations:
   - ECB with 3, 5, 9, and 13 rounds.
   - CTR with 3, 5, 9, and 13 rounds.
4. **Interpret Results**:
   - **3 rounds**: The image structure is still recognizable (colours changed, rows shifted) because MixColumns is not yet active.
   - **5 rounds**: Strong distortion begins as MixColumns kicks in; shapes start to blur.
   - **9 rounds**: Near-complete diffusion; almost indistinguishable noise.
   - **13 rounds**: Full noise, equivalent to real AES encryption.
5. **Save**: Click **Save** on any card to export the visual result as a **PNG** file.

### 4. Decrypting & Cryptanalysis (Vigenère)
1. **Navigation**: Select the **Decrypt** icon from the sidebar.
2. **Direct Decryption**: If the key is known, enter it in the key field and click Decrypt.
3. **Automated Attack**:
   - Use the **Estimate Key Length** tool to find the most probable length using IC analysis.
   - Use the **Interactive Frequency Analyzer** to visualize letter distributions and find the key shifts.
4. **Result**: The recovered plaintext will be displayed in the output workspace.

---

## Português
Este guia explica como utilizar efetivamente as principais funcionalidades da aplicação **CryptoCational**.

### 1. Criptografar Texto (Vigenère)
1. **Navegação**: Selecione o ícone **Criptografar** no menu lateral.
2. **Entrada**: Digite o texto diretamente no workspace principal ou use o botão **Selecionar Arquivo .TXT** para importar um documento local.
3. **Configuração**:
   - Selecione o **Algoritmo** desejado (ex: Vigenère).
   - Insira sua **Chave** no card de configuração designado.
4. **Execução**: Clique no botão vermelho **Criptografar** para acionar o motor core.
5. **Saída**: O resultado formatado aparecerá no painel inferior. Use **Copiar Resultado** para enviá-lo para a área de transferência do sistema.

### 2. Cifração e Decifração AES (Texto / Arquivos)
1. **Navegação**: Selecione o ícone **AES** (escudo) no menu lateral.
2. **Aba "Texto"**: Escolha entre cifrar/decifrar texto ou fazer upload de um arquivo.
3. **Configuração**:
   - **Modo**: `ECB` (Electronic Codebook) ou `CTR` (Counter Mode).
   - **Rodadas**: Número de rodadas do AES (1 a 13; padrão é 10).
   - **Chave**: Chave em texto simples (até 16 caracteres; preenchida com bytes nulos ou truncada para 16 bytes).
4. **Execução**: Clique em **Cifrar** ou **Decifrar**.
5. **Saída**: O resultado é exibido em hexadecimal. Use **Copiar Resultado** para a área de transferência.

### 3. Visualização de Selfie AES (Modo Didático)
1. **Navegação**: Na página **AES**, mude para a aba **"Selfie"**.
2. **Selecionar Imagem**: Clique em **Selecionar Selfie** e escolha qualquer imagem (PNG, JPG, BMP).
3. **Executar Testes**: Clique em **Executar Testes**. O aplicativo cifra a imagem em 8 configurações:
   - ECB com 3, 5, 9 e 13 rodadas.
   - CTR com 3, 5, 9 e 13 rodadas.
4. **Interpretar Resultados**:
   - **3 rodadas**: A estrutura da imagem ainda é reconhecível (cores trocadas, linhas deslocadas) porque o MixColumns ainda não está ativo.
   - **5 rodadas**: Distorção forte começa quando o MixColumns entra em ação; as formas começam a se desfocar.
   - **9 rodadas**: Difusão quase completa; ruído praticamente indistinguível.
   - **13 rodadas**: Ruído total, equivalente à cifração real do AES.
5. **Salvar**: Clique em **Salvar** em qualquer card para exportar o resultado visual como arquivo **PNG**.

### 4. Descriptografar e Criptoanálise (Vigenère)
1. **Navegação**: Selecione o ícone **Descriptografar** na barra lateral.
2. **Decifração Direta**: Se a chave for conhecida, insira-a no campo de chave e clique em Descriptografar.
3. **Ataque Automatizado**:
   - Use a ferramenta **Estimar Tamanho de Chave** para encontrar o comprimento mais provável usando análise de IC.
   - Use o **Analisador de Frequência Interativo** para visualizar as distribuições de letras e encontrar os deslocamentos da chave.
4. **Resultado**: O texto simples recuperado será exibido no workspace de saída.
