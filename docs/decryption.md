# Decryption & Cryptanalysis Detail / Detalhes de Descriptografia e Criptoanálise

## English

### 1. Key Length Estimation (Index of Coincidence)
The application implements the Index of Coincidence (IC) method in `core/utils.py` and `core/attack.py` to automate the discovery of the key length.

**Mathematical Formula:**
$$IC = \frac{\sum_{i=A}^Z f_i(f_i - 1)}{N(N - 1)}$$
Where $f_i$ is the frequency of letter $i$ and $N$ is the total number of letters.

**Implementation Logic:**
- **Column Splitting**: For each suspected key length $L$ (from 1 to `max_length`), the `split_text_into_columns` function extracts $L$ sub-sequences.
- **Averaging IC**: The system calculates the IC for each sub-sequence and computes the mean. A sharp spike in the average IC (approaching ~0.067 for English or ~0.074 for Portuguese) indicates that $L$ is a multiple of the actual key length.
- **Scoring**: `estimate_key_length` ranks these lengths by their proximity to the target language's expected IC.

```python
# From core/attack.py
def estimate_key_length(ciphertext: str, ...):
    for key_length in range(1, max_length):
        columns = split_text_into_columns(ciphertext, key_length)
        # Calculates average IC across all columns
        avg_ic = sum(estimate_ic(col) for col in columns) / len(columns)
        # Score based on proximity to target (0.074 for PT, 0.067 for EN)
        score = 1.0 - abs(target_ic - avg_ic) / target_ic
        results.append((key_length, max(0.0, score)))
```

### 2. Finding the Key Letters (Chi-Squared Analysis)
Once the length is determined, the cipher is reduced to $L$ Caesar ciphers. The `find_best_shift` function solves each column using statistical comparison.

**The Brute-Force Strategy:**
The system iterates through all 26 possible alphabet shifts for each column. For every shift, it calculates the statistical distance between the resulting frequency distribution and the natural language's expected benchmarks.

```python
# From core/attack.py
def find_best_shift(column: str, language: str = 'pt'):
    # Tests all 26 possible shifts
    for shift in range(26):
        # Decrypts the column with this shift
        decrypted = ''.join(
            chr(((ord(c) - ord('A') - shift) % 26) + ord('A'))
            for c in column
        )
        # Calculates frequencies and Chi-Squared score
        score = chi_squared_score(calculate_frequencies(decrypted), expected)
        
        if score < best_score:
            best_score, best_shift = score, shift
    return best_shift, best_score
```

**Chi-Squared ($\chi^2$) Scoring:**
$$\chi^2 = \sum_{i=A}^Z \frac{(C_i - E_i)^2}{E_i}$$
Where $C_i$ is the observed frequency in the shifted column and $E_i$ is the expected frequency for that letter in the selected language.

**The Attack Workflow:**
1. **Iterative Shifts**: For each column, the algorithm tests all 26 possible Caesar shifts.
2. **Frequency Matching**: For each shift, it calculates the observed letter distribution.
3. **Minimization**: The shift that results in the lowest $\chi^2$ value (closest match to natural language) is selected as the key character for that position.
4. **Confidence Ranking**: A confidence score is calculated based on the margin between the best and second-best $\chi^2$ results.

```python
# From core/attack.py
def chi_squared_score(observed, expected):
    score = 0.0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        obs = observed.get(letter, 0)
        exp = expected.get(letter, 0)
        if exp >= 0.3: # Ignore rare letters
            score += ((obs - exp) ** 2) / exp
    return score
```

### 3. Integrated Language Data (`letter_frequencies.json`)
The accuracy of the cryptanalysis depends on the quality of the language statistical data. The file `data/letter_frequencies.json` stores the expected letter percentage distributions for supported languages (Portuguese and English).

- **Role**: Serves as the $E_i$ (Expected Frequency) constant in the Chi-Squared formula.
- **Auto-Detection**: The system compares the Index of Coincidence of the ciphertext against the typical values stored in this metadata to automatically identify the likely target language.

### 4. Interactive Frequency Analyzer (UI Integration)
The `InteractiveFrequencyAnalyzer` class in `ui/pages/ui_decripto.py` provides a bridge between these algorithms and the user, allowing for real-time visualization of column frequencies as the user adjusts the suspected key length.

### 5. Note on AES Decryption
The application also includes a dedicated **AES** page (`ui/pages/ui_aes.py`) that supports manual encryption and decryption using AES-128 in ECB and CTR modes. Unlike Vigenère, AES decryption is deterministic and does not require statistical cryptanalysis. The AES page is documented in detail in the [AES Technical Report](aes_report.md) and the [Encryption Deep-Dive](encryption.md).

---

## Português

### 1. Estimativa de Comprimento de Chave (Índice de Coincidência)
A aplicação implementa o método do Índice de Coincidência (IC) em `core/utils.py` e `core/attack.py` para automatizar a descoberta do comprimento da chave.

**Fórmula Matemática:**
$$IC = \frac{\sum_{i=A}^Z f_i(f_i - 1)}{N(N - 1)}$$
Onde $f_i$ é a frequência da letra $i$ e $N$ é o número total de letras.

**Lógica de Implementação:**
- **Divisão em Colunas**: Para cada comprimento de chave suspeito $L$ (de 1 a `max_length`), a função `split_text_into_columns` extrai $L$ subsequências.
- **Média de IC**: O sistema calcula o IC para cada subsequência e computa a média. Um aumento acentuado no IC médio (aproximando-se de ~0,067 para inglês ou ~0,074 para português) indica que $L$ é um múltiplo do comprimento real da chave.
- **Pontuação**: `estimate_key_length` classifica esses comprimentos por sua proximidade com o IC esperado do idioma de destino.

```python
# Lógica de estimativa em core/attack.py
avg_ic = sum(estimate_ic(col) for col in columns) / len(columns)
score = 1.0 - abs(target_ic - avg_ic) / target_ic
```

### 2. Encontrando as Letras da Chave (Análise Qui-Quadrado)
Uma vez determinado o comprimento, a cifra é reduzida a $L$ cifras de César. A função `find_best_shift` resolve cada coluna usando comparação estatística.

**Estratégia de Força-Bruta:**
O sistema itera por todos os 26 deslocamentos possíveis do alfabeto para cada coluna. Para cada deslocamento, ele calcula a distância estatística entre a distribuição de frequência resultante e os marcos esperados do idioma natural.

```python
# Trecho de core/attack.py
for shift in range(26):
    # Decifra a coluna com este deslocamento (0-25)
    decrypted = ''.join(chr(((ord(c) - ord('A') - shift) % 26) + ord('A')) for c in column)
    
    # Calcula qui-quadrado comparando com o idioma
    score = chi_squared_score(observed_freq, expected_freq)
```

**Pontuação Qui-Quadrado ($\chi^2$):**
$$\chi^2 = \sum_{i=A}^Z \frac{(C_i - E_i)^2}{E_i}$$
Onde $C_i$ é a frequência observada na coluna deslocada e $E_i$ é a frequência esperada para essa letra no idioma selecionado.

**O Fluxo do Ataque:**
1. **Deslocamentos Iterativos**: Para cada coluna, o algoritmo testa todos os 26 deslocamentos de César possíveis.
2. **Correspondência de Frequência**: Para cada deslocamento, ele calcula a distribuição de letras observada.
3. **Minimização**: O deslocamento que resulta no menor valor de $\chi^2$ (maior proximidade com o idioma natural) é selecionado como o caractere da chave para essa posição.
4. **Ranking de Confiança**: Uma pontuação de confiança é calculada com base na margem entre o melhor e o segundo melhor resultado de $\chi^2$.

```python
# Cálculo Qui-Quadrado em core/attack.py
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    # Compara frequência observada vs esperada do idioma
    score += ((obs - exp) ** 2) / exp
```

### 3. Dados de Idioma Integrados (`letter_frequencies.json`)
A precisão da criptoanálise depende da qualidade dos dados estatísticos do idioma. O arquivo `data/letter_frequencies.json` armazena as distribuições percentuais esperadas das letras para os idiomas suportados (Português e Inglês).

- **Papel**: Serve como a constante $E_i$ (Frequência Esperada) na fórmula do Qui-Quadrado.
- **Auto-Detecção**: O sistema compara o Índice de Coincidência do criptograma com os valores típicos armazenados nestes metadados para identificar automaticamente o provável idioma de destino.

### 4. Analisador Interativo de Frequência (Integração com a UI)
A classe `InteractiveFrequencyAnalyzer` em `ui/pages/ui_decripto.py` fornece uma ponte entre esses algoritmos e o usuário, permitindo a visualização em tempo real das frequências das colunas conforme o usuário ajusta o comprimento da chave suspeito.

### 5. Nota sobre Decifração AES
A aplicação também inclui uma página dedicada ao **AES** (`ui/pages/ui_aes.py`) que suporta cifração e decifração manual usando AES-128 nos modos ECB e CTR. Ao contrário do Vigenère, a decifração AES é determinística e não requer criptoanálise estatística. A página AES é documentada em detalhes no [Relatório Técnico do AES](aes_report.md) e no [Deep-Dive de Cifra](encryption.md).
