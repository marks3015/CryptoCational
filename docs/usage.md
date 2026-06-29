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

### 4. RSA-OAEP Asymmetric Encryption
The RSA-OAEP page implements public-key encryption and digital signatures from scratch, without any external cryptographic library. All operations use RSA-2048 with OAEP padding (SHA3-256 / MGF1).

#### 4.1 Generating a Key Pair
1. **Navigation**: Select the **RSA-OAEP** icon from the sidebar.
2. Click the **Generate Key Pair** button in the home screen.
3. The application will display a status message while generating primes in a background thread (this may take 2–15 seconds).
4. Once complete, the **Public Key** and **Private Key** appear in JSON/Base64 format.
5. Use **Copy Public Key** to share your public key with others. Use **Copy Private Key** to save your private key in a secure location.
6. **Security warning**: Never share your private key. Anyone with access to it can decrypt all messages sent to you and impersonate you in signatures.

#### 4.2 Encrypting a Message
1. From the RSA home screen, click **Encrypt**.
2. Enter the message in the **Text to Encrypt** field. The maximum message size is approximately **190 bytes** for a 2048-bit key. The interface will show a warning if the limit is exceeded.
3. Paste the recipient's **Public Key** (JSON format) in the right panel.
4. Click **Encrypt**. The Base64-encoded ciphertext appears in the output panel.
5. Send the Base64 ciphertext to the recipient. It can only be decrypted with the corresponding private key.

#### 4.3 Decrypting a Message
1. From the RSA home screen, click **Decrypt**.
2. Paste the **Base64 ciphertext** received in the left field.
3. Paste your **Private Key** (JSON format) in the right field.
4. Click **Decrypt**. The original plaintext message is displayed.

#### 4.4 Signing a Message
1. From the RSA home screen, click **Sign / Verify**.
2. Ensure **Sign** mode is active (blue button).
3. Type the message in the **Message to Sign** field.
4. Paste your **Private Key** (JSON) in the right field.
5. Click **Sign Message**. A signed document (including PEM-like delimiters) is generated.
6. Share the complete signed document and your public key with the verifier.

#### 4.5 Verifying a Signature
1. From the **Sign / Verify** screen, click **Verify** to switch modes.
2. Paste the complete **signed document** (including `-----BEGIN RSA SIGNED MESSAGE-----` and end delimiters).
3. Paste the sender's **Public Key** (JSON) in the right field.
4. Click **Verify Signature**.
5. The result shows **"Signature VALID"** in green, or **"Signature INVALID"** in red. A valid result confirms both message authenticity (not tampered) and identity (signed with the matching private key).

### 5. Decrypting & Cryptanalysis (Vigenère)
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

### 4. Criptografia Assimétrica RSA-OAEP
A página RSA-OAEP implementa criptografia de chave pública e assinaturas digitais do zero, sem nenhuma biblioteca criptográfica externa. Todas as operações usam RSA-2048 com padding OAEP (SHA3-256 / MGF1).

#### 4.1 Gerar um Par de Chaves
1. **Navegação**: Selecione o ícone **RSA-OAEP** no menu lateral.
2. Clique no botão **Gerar Par de Chaves** na tela inicial.
3. O aplicativo exibirá uma mensagem de status enquanto gera primos em uma thread em segundo plano (pode levar de 2 a 15 segundos).
4. Após a conclusão, a **Chave Pública** e a **Chave Privada** aparecem no formato JSON/Base64.
5. Use **Copiar Chave Pública** para compartilhar com outros. Use **Copiar Chave Privada** para guardar em local seguro.
6. **Aviso de segurança**: Nunca compartilhe sua chave privada. Quem tiver acesso a ela poderá decifrar todas as mensagens enviadas a você e se passar por você em assinaturas.

#### 4.2 Cifrar uma Mensagem
1. Na tela inicial RSA, clique em **Cifrar**.
2. Digite a mensagem no campo **Texto para Cifrar**. O tamanho máximo é de aproximadamente **190 bytes** para uma chave de 2048 bits. A interface exibirá um aviso se o limite for excedido.
3. Cole a **Chave Pública** do destinatário (formato JSON) no painel direito.
4. Clique em **Cifrar**. O texto cifrado em Base64 aparece no painel de saída.
5. Envie o texto cifrado em Base64 ao destinatário. Somente ele, com a chave privada correspondente, pode decifrá-lo.

#### 4.3 Decifrar uma Mensagem
1. Na tela inicial RSA, clique em **Decifrar**.
2. Cole o **texto cifrado em Base64** recebido no campo esquerdo.
3. Cole sua **Chave Privada** (formato JSON) no campo direito.
4. Clique em **Decifrar**. A mensagem original é exibida.

#### 4.4 Assinar uma Mensagem
1. Na tela inicial RSA, clique em **Assinar / Verificar**.
2. Certifique-se de que o modo **Assinar** está ativo (botão azul).
3. Digite a mensagem no campo **Mensagem para Assinar**.
4. Cole sua **Chave Privada** (JSON) no campo direito.
5. Clique em **Assinar Mensagem**. Um documento assinado (com delimitadores estilo PEM) é gerado.
6. Compartilhe o documento assinado completo e sua chave pública com o verificador.

#### 4.5 Verificar uma Assinatura
1. Na tela **Assinar / Verificar**, clique em **Verificar** para mudar de modo.
2. Cole o **documento assinado completo** (incluindo os delimitadores `-----BEGIN RSA SIGNED MESSAGE-----`).
3. Cole a **Chave Pública** do remetente (JSON) no campo direito.
4. Clique em **Verificar Assinatura**.
5. O resultado exibirá **"Assinatura VALIDA"** em verde, ou **"Assinatura INVALIDA"** em vermelho. Um resultado válido confirma tanto a autenticidade da mensagem (não foi adulterada) quanto a identidade (assinada com a chave privada correspondente).

### 5. Descriptografar e Criptoanálise (Vigenère)
1. **Navegação**: Selecione o ícone **Descriptografar** na barra lateral.
2. **Decifração Direta**: Se a chave for conhecida, insira-a no campo de chave e clique em Descriptografar.
3. **Ataque Automatizado**:
   - Use a ferramenta **Estimar Tamanho de Chave** para encontrar o comprimento mais provável usando análise de IC.
   - Use o **Analisador de Frequência Interativo** para visualizar as distribuições de letras e encontrar os deslocamentos da chave.
4. **Resultado**: O texto simples recuperado será exibido no workspace de saída.
