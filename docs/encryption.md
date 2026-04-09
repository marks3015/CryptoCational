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
