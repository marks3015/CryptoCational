# CryptoCational — Agent Guide

> This file contains context for AI coding agents working on the CryptoCational project. Read it before making changes.

---

## 1. Project Overview

**CryptoCational** is an interactive educational desktop application for learning and applying cryptographic algorithms. It is built with **Python 3.10+** and **PySide6**, featuring a custom frameless dark/light UI, bilingual support (English / Portuguese), and pure-Python implementations of classical and modern ciphers.

Current algorithms:
- **Vigenère** — encryption/decryption + format-preserving mode + statistical cryptanalysis (IC and Chi-Squared).
- **AES-128** — pure Python implementation (FIPS-197) with configurable rounds (1–14), ECB/CTR modes, and a didactic visual mode.
- **RSA-OAEP** — key generation, encryption/decryption, and digital signatures.

The project prioritizes:
- Pedagogical clarity over production security.
- Modular separation between cryptographic logic (`core/`) and user interface (`ui/`).
- Minimal, readable code with consistent naming in English.

---

## 2. Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI Framework | PySide6 >= 6.4.0 |
| Build / Package | None currently; run directly with `python main.py` |
| Resources | SVG icons, PNG images, JSON frequency data |

**Dependencies:** see `requirements.txt` (only `PySide6>=6.4.0`).

---

## 3. Directory Structure

```
CryptoCational/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md               # Human-readable project overview
├── CONTRIBUTING.md         # Contribution guidelines
├── REFERENCES.md           # External cryptographic references
├── AGENTS.md               # This file
│
├── core/                   # Cryptographic engine (no UI code)
│   ├── __init__.py
│   ├── vigenere.py         # Vigenère cipher + format-preserving variants
│   ├── aes.py              # Pure-Python AES-128 (S-box, MixColumns, key expansion)
│   ├── modes.py            # ECB/CTR modes + visual didactic variants
│   ├── attack.py           # Vigenère cryptanalysis (IC, Chi-Squared)
│   ├── frequency.py        # Letter-frequency data and helpers
│   ├── utils.py            # General text utilities (IC, chunking, resource path)
│   ├── bmp_utils.py        # BMP conversion for AES selfie visualization
│   ├── translator.py       # Bilingual i18n singleton
│   └── rsa/                # RSA-OAEP implementation
│       ├── __init__.py
│       ├── keys.py         # Prime generation and key-pair creation
│       ├── oaep.py         # OAEP padding (MGF1, encode/decode)
│       ├── cipher.py       # RSA encrypt/decrypt primitives
│       └── signature.py    # File signing and verification
│
├── ui/                     # PySide6 user interface
│   ├── pages/              # Main tab pages
│   │   ├── ui_home.py
│   │   ├── ui_cripto.py    # Vigenère encryption page
│   │   ├── ui_decripto.py  # Frequency analysis / decryption page
│   │   ├── ui_aes.py       # AES text + selfie page
│   │   ├── ui_rsa.py       # RSA-OAEP page
│   │   └── ui_settings.py  # Settings + instructions
│   └── popups/             # Reusable modal dialogs
│       ├── error_popup.py
│       ├── warning_popup.py
│       ├── info_popup.py
│       └── input_popup.py
│
├── data/
│   └── letter_frequencies.json
│
├── docs/                   # Technical documentation
│   ├── architecture.md
│   ├── usage.md
│   ├── encryption.md
│   ├── decryption.md
│   ├── aes_report.md
│   └── rsa_report.md
│
└── assets/
    ├── icons/              # SVG icons used in the UI
    └── images/             # Logos and branding
```

---

## 4. Coding Conventions

### 4.1 Style
- Follow **PEP 8**.
- Use **4 spaces** for indentation.
- Maximum line length: **88 characters** (Black-compatible when possible).
- Use **English** identifiers, comments, and docstrings.
- Use **type hints** for function signatures (`typing` imports allowed).
- Docstrings should follow the existing Google-style pattern with `Args:` and `Returns:`.

### 4.2 Naming
- `snake_case` for functions, variables, and modules.
- `PascalCase` for classes.
- `UPPER_CASE` for module-level constants.
- UI page classes: `HomePage`, `AESPage`, `RSAPage`, etc.
- UI helper widgets: `CardWidget`, `SelfieTestWorker`, `RSAKeyWorker`.

### 4.3 Imports
Group imports in this order, separated by blank lines:
1. Standard library.
2. Third-party (`PySide6`).
3. Local project modules.

Example:
```python
import sys
from typing import Tuple, List

from PySide6.QtWidgets import QWidget, QVBoxLayout

from core.translator import translator
from core.utils import get_resource_path
```

### 4.4 Cryptographic Code
- Keep cryptographic logic inside `core/`; never import UI modules from `core/`.
- AES functions are byte-oriented; Vigenère functions are string-oriented.
- All user-facing keys/texts are normalized inside `core` before processing.
- Avoid introducing external crypto libraries unless explicitly requested.

---

## 5. Internationalization (i18n)

Translations live in `core/translator.py` as a global singleton `translator`.

- Default language is **Portuguese (pt)**.
- Supported languages: `"pt"`, `"en"`.
- Use `translator.get("key")` anywhere (UI or core).
- Add new strings to **both** `"pt"` and `"en"` dictionaries.
- Signal `translator.language_changed` is emitted when the language changes; UI pages can connect to it to retranslate dynamically.

When adding a new UI string:
1. Choose a descriptive key, e.g. `"aes_new_feature_label"`.
2. Add it under both `"pt"` and `"en"`.
3. Use it in the UI with `translator.get("aes_new_feature_label")`.

---

## 6. UI Patterns

### 6.1 General
- Pages are `QWidget` subclasses in `ui/pages/`.
- The main window (`main.py`) owns a `QStackedWidget` and switches pages by index.
- Reusable popups live in `ui/popups/`; prefer `show_*` helper functions over instantiating dialogs directly.

### 6.2 Resource Paths
Always use `get_resource_path(...)` from `core/utils.py` to load assets. This supports both development and PyInstaller builds:
```python
from core.utils import get_resource_path
icon = QIcon(get_resource_path("assets/icons/lock.svg"))
```

### 6.3 Long-Running Operations
- Do **not** run blocking cryptography on the main GUI thread.
- Use `QThread` workers (see `SelfieTestWorker` in `ui/pages/ui_aes.py` and `RSAKeyWorker` in `ui/pages/ui_rsa.py`).
- Communicate results via signals/slots.

### 6.4 Adding a New Page
1. Create `ui/pages/ui_<name>.py` with a `<Name>Page(QWidget)` class.
2. Import it in `main.py` and add it to the `QStackedWidget`.
3. Add a navigation button in the side menu with an SVG icon in `assets/icons/`.
4. Add menu/title translation keys in `core/translator.py`.
5. Connect the button in `MainWindow.__init__` to `self.switch_tab(new_index)`.
6. Update `switch_tab`, `_update_menu_texts`, and `retranslate_ui` accordingly.

---

## 7. Running and Testing

### 7.1 Setup
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 7.2 Run
```bash
python main.py
```

### 7.3 Testing
There is **no automated test suite yet**. When adding new cryptographic features:
- Add manual sanity checks to the relevant UI page.
- Verify round-trip encryption/decryption.
- For AES, compare against known test vectors when possible.
- Keep deterministic behavior; avoid `random` in crypto paths unless for IV/nonce generation.

If you add a test suite, prefer `pytest` and place tests under a new `tests/` directory at the project root.

---

## 8. Git Workflow

- Default branch: `main`.
- Create feature/fix branches from `main`.
- Branch naming: `feature/short-description` or `fix/issue-description`.
- Commit messages should be in English, e.g. `feat: add caesar cipher implementation`.
- See `CONTRIBUTING.md` for the full PR process.

---

## 9. Common Pitfalls

1. **PySide6 thread safety** — only manipulate Qt widgets from the main thread.
2. **Resource paths** — do not use hardcoded relative paths for assets; always use `get_resource_path`.
3. **Translations** — always add both Portuguese and English entries.
4. **Crypto correctness** — the AES implementation is educational; validate against FIPS-197 test vectors for any low-level change.
5. **Key validation** — UI should not crash on bad keys; raise `ValueError` from `core` and catch it in the UI to show a popup.

---

## 10. Documentation

Technical documentation is in `docs/`:
- `architecture.md` — system design and data flow.
- `usage.md` — user instructions.
- `encryption.md` — mathematical deep-dive (Vigenère, AES, RSA-OAEP).
- `decryption.md` — attack logic.
- `aes_report.md` — AES implementation details.
- `rsa_report.md` — RSA-OAEP implementation: Miller-Rabin, OAEP, key serialisation, signatures.

Keep these docs updated if you change architecture, pipelines, or core algorithms.

---

## 11. Where to Start

- **Bug in cipher logic?** → `core/` (and `docs/encryption.md` or `docs/decryption.md`).
- **UI bug or new page?** → `ui/pages/` and `main.py`.
- **Translation missing?** → `core/translator.py`.
- **New cipher?** → Add a module under `core/`, a page under `ui/pages/`, and wire it in `main.py`.
