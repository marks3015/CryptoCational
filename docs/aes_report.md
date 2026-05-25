# Relatório Técnico: Implementação AES-128 no CryptoCational

## 1. Descrição da Cifra AES

O **Advanced Encryption Standard (AES)** é uma cifra de bloco simétrica adotada como padrão pelo NIST (National Institute of Standards and Technology) em 2001 (FIPS-197). No contexto deste trabalho, implementamos a variante **AES-128**, que opera com:

- **Tamanho do bloco**: 128 bits (16 bytes)
- **Tamanho da chave**: 128 bits (16 bytes)
- **Número de rodadas padrão**: 10
- **Estrutura**: Rede de substituição-permutação (SPN)

### Operações por Rodada

Cada rodada do AES (exceto a inicial e a final) executa quatro transformações em uma matriz de estado 4×4 de bytes:

1. **SubBytes**: Substituição não linear byte a byte utilizando uma **S-box** (tabela de substituição de 256 bytes). Cada byte do estado é trocado pelo byte correspondente na S-box.
2. **ShiftRows**: Deslocamento cíclico das linhas da matriz de estado. A linha 0 não é deslocada, a linha 1 é deslocada 1 posição à esquerda, a linha 2 em 2 posições, e a linha 3 em 3 posições.
3. **MixColumns**: Multiplicação matricial de cada coluna por uma matriz fixa no **corpo finito Galois GF(2⁸)** com polinômio irredutível *x⁸ + x⁴ + x³ + x + 1* (0x11B). Cada byte da coluna é combinado com todos os outros da mesma coluna através de operações de multiplicação e XOR.
4. **AddRoundKey**: XOR bit a bit do estado atual com a **chave de rodada** correspondente.

A **rodada inicial** executa apenas `AddRoundKey`. A **rodada final** executa `SubBytes`, `ShiftRows` e `AddRoundKey` (sem `MixColumns`), garantindo a simetria entre cifração e decifração.

### Expansão de Chave (Key Schedule)

A chave de 128 bits é expandida em `(Nr + 1)` chaves de rodada de 128 bits cada, onde `Nr` é o número de rodadas. O algoritmo de expansão:

1. Divide a chave em 4 palavras (words) de 32 bits.
2. Gera palavras subsequentes aplicando `RotWord` (rotação cíclica), `SubWord` (substituição via S-box) e XOR com uma constante de rodada `Rcon`.
3. A constante `Rcon[i] = [x^(i-1), 00, 00, 00]`, onde *x = {02}* em GF(2⁸).

Para atender ao requisito do trabalho de executar com **3, 5, 9 e 13 rodadas**, generalizamos o algoritmo de expansão de chave para suportar até 14 rodadas (máximo teórico do AES-128), gerando round keys adicionais conforme necessário.

---

## 2. Descrição dos Modos de Operação

### 2.1 ECB (Electronic Codebook)

O modo **ECB** é o mais simples dos modos de operação de cifra de bloco:

- **Funcionamento**: O texto claro é dividido em blocos de 16 bytes. Cada bloco é cifrado **independentemente** com a mesma chave.
- **Padding**: Utiliza-se o preenchimento **PKCS#7** (adiciona N bytes de valor N para completar o último bloco).
- **Decifração**: Cada bloco cifrado é decifrado individualmente e o padding é removido.

**Vantagens**:
- Paralelizável (blocos independentes).
- Erro em um bloco não se propaga.

**Desvantagens**:
- **Padrões visuais** no ciphertext: blocos idênticos de plaintext produzem blocos idênticos de ciphertext. Isso torna o modo vulnerável a análise estatística e torna padrões visíveis quando ciframos imagens.
- Não é recomendado para uso em aplicações reais.

### 2.2 CTR (Counter Mode)

O modo **CTR** transforma uma cifra de bloco em uma **cifra de fluxo**:

- **Funcionamento**: Um **nonce/IV** de 16 bytes é cifrado com AES para gerar um **keystream**. Esse keystream é XORado com o plaintext para produzir o ciphertext.
- **Contador**: Após cada bloco, o nonce é incrementado como um contador de 128 bits (big-endian).
- **Padding**: **Não necessário**. O último bloco é truncado para o tamanho exato do plaintext.
- **Decifração**: Idêntica à cifração. Basta reaplicar o XOR com o mesmo keystream (o AES-CTR é simétrico).

**Vantagens**:
- Totalmente paralelizável (keystream pode ser pré-computado).
- Não propaga erros (erro em um byte afeta apenas aquele byte).
- Ideal para cifração de streams e dados onde o tamanho não é múltiplo do bloco.
- Não revela padrões visuais (resultado visual é ruidoso, sem estrutura aparente).

**Desvantagens**:
- Requer IV/nonce único para cada mensagem (reuso de IV com a mesma chave compromete a segurança).

### 2.3 Modos Visuais Didáticos

Além dos modos criptográficos padrão, o projeto introduz variantes didáticas para a demonstração com imagens:

- **`aes_ecb_encrypt_visual`**: Usa `encrypt_block_visual` (que omite `MixColumns` nas rodadas iniciais) para preservar a estrutura visual em rodadas baixas.
- **`aes_ctr_encrypt_visual`**: Gera o keystream com `encrypt_block_visual`, mantendo a mesma progressão visual no modo CTR.

A omissão controlada do `MixColumns` é uma decisão **puramente pedagógica**: o AES real com 3 rodadas já produz ruído indistinguível, o que impede a observação visual do papel de cada transformação. As funções visuais usam o mesmo key schedule e as mesmas operações (`SubBytes`, `ShiftRows`, `AddRoundKey`), diferindo apenas pela introdução gradual do `MixColumns`.

---

## 3. Descrição da Implementação

### 3.1 Arquitetura dos Módulos

| Arquivo | Responsabilidade |
|---------|------------------|
| `core/aes.py` | Implementação manual do AES-128: S-box, transformações de rodada, expansão de chave generalizada, cifração/decifração de bloco único, padding PKCS#7, normalização de chave, e a variante didática `encrypt_block_visual`. |
| `core/modes.py` | Implementação dos modos ECB e CTR (padrão e visual) sobre `core/aes`. |
| `core/bmp_utils.py` | Conversão de imagens para BMP 24-bit, extração de header/pixels e reconstrução de BMP válido. |
| `ui/pages/ui_aes.py` | Interface gráfica dedicada ao AES: configuração de modo/rodadas/chave, área de cifração/decifração de textos/arquivos, seção de testes com selfie (8 configurações: ECB/CTR × 4 contagens de rodadas). |
| `main.py` | Integração da nova página no menu lateral (botão "AES" com ícone shield.svg) e no stack de páginas. |
| `core/translator.py` | Strings bilíngues (PT/EN) para todos os elementos da nova interface. |

### 3.2 Destaques Técnicos

- **Sem bibliotecas criptográficas externas**: Toda a primitiva (AES, KeyExpansion, MixColumns em GF(2⁸)) foi implementada manualmente em Python puro.
- **Controle de rodadas**: A `key_expansion` foi generalizada para gerar round keys para qualquer `Nr` entre 1 e 14 (conforme exigido pelo trabalho), permitindo os testes com 3, 5, 9, 10 e 13 rodadas.
- **Multiplicação em GF(2⁸)**: Implementada via multiplicação bit a bit com redução pelo polinômio 0x11B. Foram pré-computadas tabelas `_MUL2`, `_MUL3`, `_MUL9`, `_MUL11`, `_MUL13`, `_MUL14` para otimizar `MixColumns` e `InvMixColumns`.
- **Cifra visual didática**: A função `encrypt_block_visual` omite `MixColumns` nas rodadas intermediárias abaixo de um limiar (`mixcol_after=3`), criando um efeito visual progressivo que permite observar o impacto isolado de `SubBytes`, `ShiftRows` e `AddRoundKey` antes da difusão completa.
- **Manipulação de BMP**: A cifração visual preserva o header BMP original (54 bytes) e cifra apenas os pixels. Isso garante que o resultado seja uma imagem BMP válida que pode ser renderizada diretamente pelo Qt.
- **Salvamento como PNG**: Os resultados dos testes de selfie são salvos como arquivos PNG, não como `.dat` bruto. O arquivo exportado é exatamente a imagem visual exibida na tela.
- **Interface em 2 abas**: A página AES foi dividida em duas abas separadas — **"Texto"** para cifração/decifração de dados e **"Selfie"** para testes com imagens — mantendo a interface organizada e focada.

---

## 4. Instruções de Uso

### 4.1 Cifração/Decifração de Dados (Aba "Texto")

1. Navegue até a aba **AES** pelo menu lateral.
2. Na aba **"Texto"**, configure:
   - **Modo**: `ECB` ou `CTR`.
   - **Rodadas**: número desejado (1 a 13, padrão 10).
   - **Chave**: texto simples (até 16 caracteres; preenchido com zeros ou truncado para 16 bytes).
3. Insira os dados na área de entrada (texto ou hexadecimal) ou faça upload de um arquivo via botão **Selecionar Arquivo**.
4. Clique em **Cifrar** ou **Decifrar**.
5. O resultado em hexadecimal é exibido no painel inferior. Use **Copiar Resultado** para transferir.

### 4.2 Testes com Selfie (Aba "Selfie")

1. Na aba **AES**, clique na sub-aba **"Selfie"**.
2. Clique em **Selecionar Selfie** e escolha uma imagem do seu computador.
3. A imagem original será exibida como preview.
4. Clique em **Executar Testes**. O aplicativo cifrará a selfie em 8 configurações:
   - ECB com 3, 5, 9 e 13 rodadas.
   - CTR com 3, 5, 9 e 13 rodadas.
5. Cada resultado é renderizado como uma imagem visual e seu **hash SHA-256** é exibido.
6. Use o botão **Salvar** em cada card para exportar a imagem visual como **PNG**.

### 4.3 O que Esperar Visualmente em Cada Configuração

- **3 rodadas**: A estrutura da imagem ainda é reconhecível. Apenas `SubBytes` (troca de cores), `ShiftRows` (deslocamento de linhas) e `AddRoundKey` foram aplicados. Blocos de cor uniforme no plaintext ainda aparecem como blocos no ciphertext (especialmente em ECB).
- **5 rodadas**: Distorção significativa. `MixColumns` começa a atuar a partir da 3ª rodada, misturando bytes dentro de cada coluna. Grandes formas ainda podem ser identificadas, mas detalhes se perdem.
- **9 rodadas**: Difusão quase total. A imagem se assemelha a ruído aleatório, com pouquíssima estrutura remanescente.
- **13 rodadas**: Ruído completo, indistinguível do AES padrão. A cifra visual converge ao comportamento criptográfico real.

---

## 5. Validação

A implementação foi validada com:

- **Vetor de teste NIST FIPS-197** para AES-128 (10 rodadas): plaintext `00112233...EEFF` com chave `00010203...0E0F` produz ciphertext `69C4E0D8...C55A`, confirmando a exatidão da implementação.
- **Round-trip tests**: ECB e CTR com 3, 5, 9, 10 e 13 rodadas foram testados com cifração seguida de decifração, recuperando o plaintext original em todos os casos.
- **Testes de visualização**: A contagem de blocos repetidos em imagens sintéticas (blocos de cor uniforme 64×64) confirmou que ECB preserva padrões estruturais (blocos idênticos → blocos cifrados idênticos), enquanto CTR produz blocos únicos em todos os casos.
