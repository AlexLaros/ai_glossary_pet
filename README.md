
# AI Glossary from Scientific Papers

## Description

This is a FastAPI-based service that:

- Accepts a scientific paper in **PDF** format
- Extracts and preprocesses the text
- Uses an LLM (via **OpenRouter API**) to identify difficult technical terms
- Returns a structured glossary in **JSON** format

The glossary includes:

- `term`
- `definition`
- `example sentence`

## Tech Stack

- FastAPI
- PyMuPDF (PDF text extraction)
- OpenRouter (LLM via OpenAI-compatible API)
- Pydantic (response validation)
- python-dotenv

## Installation & Run

### 1) Clone project

```bash
git clone <your-repo-url>
cd <project-folder>
````

### 2) Create virtual environment

```bash
python -m venv .venv
```

Activate:

**Windows (PowerShell / CMD):**

```bash
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

If no `requirements.txt`:

```bash
pip install fastapi uvicorn pymupdf openai python-dotenv
```

### 4) Create `.env` file

In the project root, create a file named `.env`:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### 5) Run server

```bash
uvicorn main:app --reload
```

### 6) Open Swagger

```text
http://127.0.0.1:8000/docs
```
