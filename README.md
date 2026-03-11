# Australia Medical Insurance Claiming Copilot

An AI-powered copilot for matching and navigating Australian Medicare Benefits Schedule (MBS) insurance claims.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/BruceYuchen/Australia-Medical-Insurance-Claiming-Copilot.git
cd Australia-Medical-Insurance-Claiming-Copilot
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download models

The models are not included in this repository due to their size. Download them by running:

```bash
python download_models.py
```

Or download manually from HuggingFace:

```bash
pip install huggingface_hub

python - <<EOF
from huggingface_hub import snapshot_download

# Bio ClinicalBERT
snapshot_download(
    repo_id="emilyalsentzer/Bio_ClinicalBERT",
    local_dir="models/huggingface/models--emilyalsentzer--Bio_ClinicalBERT"
)

# Sentence Transformers - all-MiniLM-L6-v2
snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    local_dir="models/sentence_transformers/models--sentence-transformers--all-MiniLM-L6-v2"
)

# Sentence Transformers - all-mpnet-base-v2
snapshot_download(
    repo_id="sentence-transformers/all-mpnet-base-v2",
    local_dir="models/sentence_transformers/models--sentence-transformers--all-mpnet-base-v2"
)
EOF
```

### 5. Run the server

```bash
python run_server.py
```

### 6. Access the application

- **Web Interface**: http://localhost:8000
- **API**: Use the web interface or call the REST API endpoints directly

### 4. Download models

The models are not included in this repository due to their size. Download them by running:

```bash
python download_models.py
```

Or download manually from HuggingFace:

```bash
pip install huggingface_hub

python - <<EOF
from huggingface_hub import snapshot_download

# Bio ClinicalBERT
snapshot_download(
    repo_id="emilyalsentzer/Bio_ClinicalBERT",
    local_dir="models/huggingface/models--emilyalsentzer--Bio_ClinicalBERT"
)

# Sentence Transformers - all-MiniLM-L6-v2
snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    local_dir="models/sentence_transformers/models--sentence-transformers--all-MiniLM-L6-v2"
)

# Sentence Transformers - all-mpnet-base-v2
snapshot_download(
    repo_id="sentence-transformers/all-mpnet-base-v2",
    local_dir="models/sentence_transformers/models--sentence-transformers--all-mpnet-base-v2"
)
EOF
```

### 5. Run the application

```bash
python main.py
```

---

## Project Structure

```
mbs-matcher/
├── app/              # Application layer
├── core/             # Core logic
├── services/         # Business services
├── utils/            # Utility functions
├── data/             # MBS data files
├── static/           # Static assets
├── tests/            # Test cases
├── docs/             # Documentation
├── models/           # Downloaded models (not in repo, see setup above)
└── main.py           # Entry point
```

---

## Notes

- `models/` and `venv/` are excluded from version control via `.gitignore`
- Models are downloaded from [HuggingFace](https://huggingface.co) and cached locally
