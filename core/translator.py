from PySide6.QtCore import QObject, Signal

class Translator(QObject):
    language_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._lang = "pt"
        
        self.TRANSLATIONS = {
            "pt": {
                # Menu / Top Bar
                "menu_home": " Home",
                "menu_encrypt": " Criptografar",
                "menu_decrypt": " Descriptografar",
                "menu_instructions": " Instruções",
                "menu_settings": " Configurações",
                "menu_toggle": " Menu",
                "app_title_home": "CryptoCational - Home",
                "app_title_encrypt": "CryptoCational - Criptografar",
                "app_title_decrypt": "CryptoCational - Decifrar",
                "app_title_instructions": "CryptoCational - Instruções",
                "app_title_settings": "CryptoCational - Configurações",
                "app_title_aes": "CryptoCational - AES",
                "menu_aes": " AES",
                
                # Home
                "home_subtitle": "Escolha uma opção para continuar",
                "btn_encrypt": "Criptografar",
                "btn_decrypt": "Descriptografar",
                "btn_instructions": "Instruções",
                
                # Cripto Page
                "cripto_title": "Criptografar Texto",
                "cripto_file_btn": "Selecionar Arquivo .TXT",
                "cripto_algorithm": "Método de Criptografia",
                "cripto_algo_aes": "AES-128",
                "input_text": "Texto para Criptografar",
                "input_placeholder": "Digite ou cole seu texto aqui... Ou faça o upload de um arquivo ao lado.",
                "key_label": "Chave",
                "key_placeholder": "Digite a chave...",
                "result_label": "Resultado",
                "btn_copy": "Copiar Resultado",
                "btn_encrypt_action": "Criptografar",
                "msg_no_key": "A chave não pode estar vazia ou conter números.",
                "msg_no_text": "O texto para criptografar não pode estar vazio.",
                
                # AES Page
                "aes_title": "Cifra AES-128",
                "aes_mode_label": "Modo de Operação",
                "aes_mode_ecb": "ECB (Electronic Codebook)",
                "aes_mode_ctr": "CTR (Counter)",
                "aes_rounds_label": "Número de Rodadas",
                "aes_key_label": "Chave",
                "aes_key_placeholder": "Digite a chave (texto simples)",
                "aes_input_text": "Dados de Entrada",
                "aes_input_placeholder": "Digite texto ou hex... Ou faça upload de um arquivo.",
                "aes_result_label": "Resultado (Hex)",
                "aes_btn_encrypt": "Cifrar",
                "aes_btn_decrypt": "Decifrar",
                "aes_btn_select_file": "Selecionar Arquivo",
                "aes_btn_copy": "Copiar Resultado",
                "aes_msg_no_key": "A chave não pode estar vazia.",
                "aes_msg_no_text": "Os dados de entrada não podem estar vazios.",
                "aes_error_key_length": "A chave deve ter até 16 caracteres.",
                "aes_selfie_title": "Testes com Selfie",
                "aes_selfie_select": "Selecionar Selfie",
                "aes_selfie_run_tests": "Executar Testes",
                "aes_hash_label": "Hash SHA-256:",
                "aes_save_btn": "Salvar",
                "aes_test_ecb_3": "ECB - 3 rodadas",
                "aes_test_ecb_5": "ECB - 5 rodadas",
                "aes_test_ecb_9": "ECB - 9 rodadas",
                "aes_test_ecb_13": "ECB - 13 rodadas",
                "aes_test_ctr_3": "CTR - 3 rodadas",
                "aes_test_ctr_5": "CTR - 5 rodadas",
                "aes_test_ctr_9": "CTR - 9 rodadas",
                "aes_test_ctr_13": "CTR - 13 rodadas",
                "aes_file_dialog_title": "Selecionar arquivo",
                "aes_file_filter_all": "Todos os Arquivos (*.*)",
                "aes_file_filter_txt": "Arquivos de Texto (*.txt)",
                "aes_file_filter_img": "Imagens (*.png *.jpg *.jpeg *.bmp)",
                "aes_tab_text": "Texto",
                "aes_tab_selfie": "Selfie",
                "aes_selfie_none": "Nenhuma imagem selecionada",
                "aes_waiting_test": "Aguardando teste...",
                "aes_preview_na": "Preview não disponível",
                "aes_saved_to": "Salvo em:",
                "aes_msg_no_selfie": "Selecione uma selfie primeiro.",
                "aes_msg_ctr_short": "Dados CTR muito curtos (precisa de IV de 16 bytes)",
                
                "decripto_tab_vigenere": "Análise de Frequência",
                "decripto_tab_aes": "Decifração AES",
                "decripto_aes_input": "Ciphertext (Hex)",
                "decripto_home_title": "Decifração",
                "decripto_home_subtitle": "Selecione um método de decifração",
                "btn_back": "Voltar",
                
                # Decripto Page
                "decripto_title": "Análise Manual por Frequência",
                "crypto_text": "Criptograma",
                "decrypted_text": "Texto Decifrado",
                "stats_ic": "IC desta coluna: {ic}",
                "stats_ic_none": "IC desta coluna: --",
                "stats_alignment": "Alinhamento: {score}%",
                "stats_legibility": "Legibilidade: {score}%",
                "config_label": "Configurações",
                "config_lang": "Idioma",
                "config_key_size": "Tamanho da chave",
                "btn_estimate_size": "Estimar Tamanho",
                "btn_start_analysis": "Iniciar Análise",
                "interactive_analysis": "Análise Interativa",
                "btn_prev": "< Anterior",
                "btn_next": "Próxima >",
                "col_label": "Coluna {curr} de {total}",
                "shift_label": "Shift: {shift} ({letter})",
                "btn_confirm_letter": "Confirmar Letra",
                "key_display_label": "Chave",
                "btn_edit_key": "Editar Chave",
                "chart_expected": "Esperada",
                "chart_observed": "Observada",
                "chart_x": "Letra",
                "chart_y": "Freq. (%)",
                "popup_text_empty": "O texto cifrado não pode estar vazio.",
                "popup_key_size_invalid": "Por favor, insira um tamanho válido para a chave.",
                "popup_no_analysis": "Realize a análise antes de testar chaves manuais.",
                "popup_enter_key": "Digite a nova chave de tamanho {size}:",

                # Settings Page
                "settings_title": "Configurações",
                "settings_lang": "Idioma do Aplicativo",
                "settings_lang_pt": "Português",
                "settings_lang_en": "Inglês",
                "settings_save": "Salvar",
                "settings_tab_general": "Geral",
                "settings_tab_license": "Licença",
                "settings_tab_instructions": "Instruções",
                "settings_version": "Versão do Sistema",
                "settings_tab_license_content": "Licença do aplicativo não definida.",

                # Instructions Page
                "inst_title": "Instruções de Uso",
                "inst_sec1_title": "Sobre o CryptoCational",
                "inst_sec1_body": "O CryptoCational é uma ferramenta educacional projetada para facilitar o entendimento de métodos criptográficos famosos. Nesta versão inicial, o foco é a Cifra de Vigenère, oferecendo funções de cifragem, decifragem e análise de frequência interativa. O projeto foi arquitetado para escalar, visando incorporar novos algoritmos em versões futuras para proporcionar um ambiente prático e intuitivo de aprendizado.",
                "inst_sec2_title": "Como Criptografar",
                "inst_sec2_body": "1. Na aba 'Criptografar', digite ou cole o texto que deseja proteger.\n2. Insira a Chave (apenas letras). A cifra de Vigenère repetirá essa chave ao longo de todo o texto.\n3. Clique em 'Criptografar' para gerar o resultado.",
                "inst_sec3_title": "Como Descriptografar (Texto Simples)",
                "inst_sec3_body": "Se você já sabe a chave, vá à aba 'Descriptografar', cole o texto cifrado, insira a chave correta e clique em 'Descriptografar'. (Nota: você deve inserir a chave manualmente através do botão 'Editar Chave' se souber o tamanho e as letras).",
                "inst_sec4_title": "Análise de Frequência (Quebra da Cifra)",
                "inst_sec4_body": "Caso não possua a chave, você pode tentar descobri-la:\n\n1. Insira o texto cifrado.\n2. Clique em 'Estimar Tamanho'. O app calculará possíveis tamanhos de chave com base no IC.\n3. Após definir o tamanho da chave, clique em 'Iniciar Análise'.\n4. A Análise Interativa será aberta. Você verá as frequências das letras na sua coluna comparadas às da língua.\n5. Deslize a barra para mudar o Shift até que os gráficos se alinhem.\n6. Pressione 'Confirmar Letra' e continue para as próximas colunas.",
                
                # Dynamic App Text & Popups
                "stats_label": "Estatísticas",
                "warn_insert_crypto": "Insira um criptograma primeiro.",
                "msg_probable_sizes": "Tamanhos mais prováveis:\n\n",
                "msg_key_size_pct": "  Chave {length}:  {pct}\n",
                "info_crypto_divided": "Criptograma dividido em {num} colunas.\n\nUse os controles para ajustar o shift de cada coluna.",
                "edit_key_prompt": "Digite a chave completa:"
            },
            "en": {
                # Menu / Top Bar
                "menu_home": " Home",
                "menu_encrypt": " Encrypt",
                "menu_decrypt": " Decrypt",
                "menu_instructions": " Instructions",
                "menu_settings": " Settings",
                "menu_toggle": " Menu",
                "app_title_home": "CryptoCational - Home",
                "app_title_encrypt": "CryptoCational - Encrypt",
                "app_title_decrypt": "CryptoCational - Decrypt",
                "app_title_instructions": "CryptoCational - Instructions",
                "app_title_settings": "CryptoCational - Settings",
                "app_title_aes": "CryptoCational - AES",
                "menu_aes": " AES",
                
                # Home
                "home_subtitle": "Choose an option to continue",
                "btn_encrypt": "Encrypt",
                "btn_decrypt": "Decrypt",
                "btn_instructions": "Instructions",
                
                # Cripto Page
                "cripto_title": "Encrypt Text",
                "cripto_file_btn": "Select .TXT File",
                "cripto_algorithm": "Encryption Method",
                "cripto_algo_aes": "AES-128",
                "input_text": "Text to Encrypt",
                "input_placeholder": "Type or paste your text here... Or upload a file on the button next to.",
                "key_label": "Key",
                "key_placeholder": "Enter the key...",
                "result_label": "Result",
                "btn_copy": "Copy Result",
                "btn_encrypt_action": "Encrypt",
                "msg_no_key": "The key cannot be empty or contain numbers.",
                "msg_no_text": "The text to encrypt cannot be empty.",
                
                # AES Page
                "aes_title": "AES-128 Cipher",
                "aes_mode_label": "Operation Mode",
                "aes_mode_ecb": "ECB (Electronic Codebook)",
                "aes_mode_ctr": "CTR (Counter)",
                "aes_rounds_label": "Number of Rounds",
                "aes_key_label": "Key",
                "aes_key_placeholder": "Enter the key (plain text)",
                "aes_input_text": "Input Data",
                "aes_input_placeholder": "Type text or hex... Or upload a file.",
                "aes_result_label": "Result (Hex)",
                "aes_btn_encrypt": "Encrypt",
                "aes_btn_decrypt": "Decrypt",
                "aes_btn_select_file": "Select File",
                "aes_btn_copy": "Copy Result",
                "aes_msg_no_key": "The key cannot be empty.",
                "aes_msg_no_text": "Input data cannot be empty.",
                "aes_error_key_length": "Key must be up to 16 characters.",
                "aes_selfie_title": "Selfie Tests",
                "aes_selfie_select": "Select Selfie",
                "aes_selfie_run_tests": "Run Tests",
                "aes_hash_label": "SHA-256 Hash:",
                "aes_save_btn": "Save",
                "aes_test_ecb_3": "ECB - 3 rounds",
                "aes_test_ecb_5": "ECB - 5 rounds",
                "aes_test_ecb_9": "ECB - 9 rounds",
                "aes_test_ecb_13": "ECB - 13 rounds",
                "aes_test_ctr_3": "CTR - 3 rounds",
                "aes_test_ctr_5": "CTR - 5 rounds",
                "aes_test_ctr_9": "CTR - 9 rounds",
                "aes_test_ctr_13": "CTR - 13 rounds",
                "aes_file_dialog_title": "Select file",
                "aes_file_filter_all": "All Files (*.*)",
                "aes_file_filter_txt": "Text Files (*.txt)",
                "aes_file_filter_img": "Images (*.png *.jpg *.jpeg *.bmp)",
                "aes_tab_text": "Text",
                "aes_tab_selfie": "Selfie",
                "aes_selfie_none": "No image selected",
                "aes_waiting_test": "Waiting for test...",
                "aes_preview_na": "Preview not available",
                "aes_saved_to": "Saved to:",
                "aes_msg_no_selfie": "Please select a selfie first.",
                "aes_msg_ctr_short": "CTR data too short (needs 16-byte IV)",
                
                "decripto_tab_vigenere": "Frequency Analysis",
                "decripto_tab_aes": "AES Decryption",
                "decripto_aes_input": "Ciphertext (Hex)",
                "decripto_home_title": "Decryption",
                "decripto_home_subtitle": "Select a decryption method",
                "btn_back": "Back",
                
                # Decripto Page
                "decripto_title": "Manual Frequency Analysis",
                "crypto_text": "Ciphertext",
                "decrypted_text": "Decrypted Text",
                "stats_ic": "Column IC: {ic}",
                "stats_ic_none": "Column IC: --",
                "stats_alignment": "Alignment: {score}%",
                "stats_legibility": "Legibility: {score}%",
                "config_label": "Configuration",
                "config_lang": "Language",
                "config_key_size": "Key size",
                "btn_estimate_size": "Estimate Size",
                "btn_start_analysis": "Start Analysis",
                "interactive_analysis": "Interactive Analysis",
                "btn_prev": "< Previous",
                "btn_next": "Next >",
                "col_label": "Column {curr} of {total}",
                "shift_label": "Shift: {shift} ({letter})",
                "btn_confirm_letter": "Confirm Letter",
                "key_display_label": "Key",
                "btn_edit_key": "Edit Key",
                "chart_expected": "Expected",
                "chart_observed": "Observed",
                "chart_x": "Letter",
                "chart_y": "Freq. (%)",
                "popup_text_empty": "The ciphertext cannot be empty.",
                "popup_key_size_invalid": "Please enter a valid key size.",
                "popup_no_analysis": "Run the analysis before testing manual keys.",
                "popup_enter_key": "Enter the new key of size {size}:",

                # Settings Page
                "settings_title": "Settings",
                "settings_lang": "Application Language",
                "settings_lang_pt": "Portuguese",
                "settings_lang_en": "English",
                "settings_save": "Save",
                "settings_tab_general": "General",
                "settings_tab_license": "License",
                "settings_tab_instructions": "Instructions",
                "settings_version": "System Version",
                "settings_tab_license_content": "Application license is not defined.",

                # Instructions Page
                "inst_title": "Instructions",
                "inst_sec1_title": "About CryptoCational",
                "inst_sec1_body": "CryptoCational is an educational tool designed to facilitate the understanding of famous cryptographic methods. In this initial version, the focus is on the Vigenère Cipher, offering encryption, decryption, and interactive frequency analysis. The project is built to scale, with future versions aiming to incorporate new algorithms to provide a practical and intuitive learning environment.",
                "inst_sec2_title": "How to Encrypt",
                "inst_sec2_body": "1. Go to the 'Encrypt' tab and paste the text you wish to protect.\n2. Enter the Key (letters only). The Vigenère cipher repeats this key throughout the text.\n3. Click 'Encrypt' to generate the result.",
                "inst_sec3_title": "How to Decrypt (Simple Text)",
                "inst_sec3_body": "If you already know the key, go to the 'Decrypt' tab, paste the ciphertext, enter the correct key in 'Edit Key' and click 'Decrypt'.",
                "inst_sec4_title": "Frequency Analysis (Breaking the Cipher)",
                "inst_sec4_body": "If you don't know the key, try breaking it:\n\n1. Paste the ciphertext.\n2. Click 'Estimate Size'. The app will calculate possible key sizes using IC.\n3. After setting the key size, click 'Start Analysis'.\n4. The Interactive Analysis will open. You will see the frequencies of your column's letters compared to language frequencies.\n5. Move the slider to change the Shift until the charts align.\n6. Press 'Confirm Letter' and proceed to the next columns.",
                
                # Dynamic App Text & Popups
                "stats_label": "Statistics",
                "warn_insert_crypto": "Please insert a ciphertext first.",
                "msg_probable_sizes": "Most probable sizes:\n\n",
                "msg_key_size_pct": "  Key {length}:  {pct}\n",
                "info_crypto_divided": "Ciphertext split into {num} columns.\n\nUse the controls to adjust the shift for each column.",
                "edit_key_prompt": "Enter the full key:"
            }
        }

    def set_language(self, lang_code):
        if lang_code in self.TRANSLATIONS and self._lang != lang_code:
            self._lang = lang_code
            self.language_changed.emit(self._lang)

    def get_language(self):
        return self._lang

    def get(self, key, default=None, **kwargs):
        text = self.TRANSLATIONS.get(self._lang, {}).get(key, default if default else key)
        if kwargs:
            return text.format(**kwargs)
        return text

# Global singleton
translator = Translator()
