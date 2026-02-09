# 🤖 Production-Ready Dataset Bot

A streamlined, robust Telegram Bot for:
1.  **Secure File Retrieval:** Getting a ZIP dump of the server's temp folder (`MLparset`).
2.  **Dataset Discovery:** Instant link searching across Kaggle, HuggingFace, and GitHub.

> **Status:** Production Stable  
> **Python:** 3.10+

---

## 🚀 Features

### 1. The `MLparset` Command (Mode 1)
-   **Trigger:** Send exactly `MLparset`.
-   **Action:** The bot checks the configured `temp/` folder.
-   **Result:** It securely zips all files in that folder and sends a single `ml_datasets_bundle.zip` to the chat.
-   **Safety:** Handles concurrent requests via unique temporary zip paths.

### 2. Dataset Universal Search (Mode 2)
-   **Trigger:** Send ANY other text (e.g., "Brain Tumor CSV").
-   **Action:** Concurrently searches:
    -   🏆 **Kaggle**
    -   🤗 **HuggingFace**
    -   💻 **GitHub**
-   **Result:** Returns a clean list of **direct links** to the datasets.

---

## 📦 Installation

### Prerequisites
-   Python 3.10+
-   A Telegram Bot Token (from @BotFather)

### Setup

1.  **Clone & Install**
    ```bash
    git clone <repo_url>
    cd <repo_dir>
    pip install -r requirements.txt
    ```

2.  **Configuration**
    Create a `.env` file in the root directory:
    ```env
    TELEGRAM_BOT_TOKEN=your_token_here
    
    # Optional (for better search results)
    KAGGLE_USERNAME=your_user
    KAGGLE_KEY=your_key
    HF_TOKEN=your_token
    GITHUB_TOKEN=your_token
    ```

3.  **Run**
    ```bash
    python main.py
    ```

---

## 🛠 Engineering Notes

### Safety & Stability
-   **Thread-Safe Zipping:** The `MLparset` function uses `tempfile.NamedTemporaryFile` to ensure that if multiple users request a zip simultaneously, they don't corrupt each other's files.
-   **Error Isolation:** If `Kaggle` is down, `GitHub` and `HuggingFace` results will still be returned. The bot never crashes on partial service failure.
-   **Timeouts:** Network calls have strict timeouts (10s for APIs, 30s for Telegram) to prevent hanging processes.

### Directory Structure
-   `main.py`: Entry point and global error handling.
-   `config.py`: Environment validation and path management.
-   `handlers/`: Contains the logic for `MLparset` zip creation and Search routing.
-   `services/`: Encapsulated logic for external APIs.
-   `temp/`: The folder served by `MLparset`.

---

## 📄 License
MIT License.
