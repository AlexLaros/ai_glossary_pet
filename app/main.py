from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from app.schemas import GlossaryResponse, GlossaryItem
import fitz
import re
import json

load_dotenv()
app = FastAPI()
client = OpenAI(api_key=getenv("OPENROUTER_API_KEY", ""), base_url="https://openrouter.ai/api/v1")
MODEL_ID = "stepfun/step-3.5-flash:free"


def extract_text_from_pdf(pdf_bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts = []
    for page in doc: parts.append(page.get_text("text"))
    return "\n".join(parts).strip()


def clean_text(text: str) -> str:
    text = text.replace("-\n", "")

    text = re.sub(r"\n{3,}", "\n\n", text)

    MAX_CHARS = 60000
    text = text[:MAX_CHARS]

    return text


def build_glossary_llm(text: str, n_terms: int = 15) -> list[dict]:
    prompt = f""" Return ONLY valid JSON. No markdown. No extra text. 
    Pick {n_terms} difficult/technical terms from the scientific text. 
    For each term provide: term, definition (1-2 sentences), example (one short sentence). 
    
    Return JSON exactly like: 
    {{ 
    "items": [ {{"term": "...", "definition": "...", "example": "..."}} ] 
    }} 
    
    TEXT: {text} """

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[dict(role="user", content=prompt)],
        temperature=0.2, )
    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="LLM returned invalid JSON format.")

    if "items" not in data:
        raise HTTPException(status_code=502, detail="LLM response missing 'items' field.")
    items_raw = data["items"]

    if not isinstance(items_raw, list):
        raise HTTPException(status_code=502, detail="LLM 'items' is not a list.", )

    items = [GlossaryItem(**item).model_dump() for item in items_raw]
    return items


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/glossary", response_model=GlossaryResponse)
async def glossary(file: UploadFile = File(...), n_terms: int = Form(default=15)):
    if not (5 <= n_terms <= 50):
        raise HTTPException(status_code=400, detail="n_terms must be between 5 and 50.")
    data = await file.read()
    if not file.filename.lower().endswith(".pdf"): raise HTTPException(status_code=400,
                                                                       detail="Please, only PDF file format.")
    text = extract_text_from_pdf(data)
    if not text: raise HTTPException(status_code=422, detail="Could not extract text form PDF file.")
    text = clean_text(text)

    items = build_glossary_llm(text=text, n_terms=n_terms)
    return {
        "source": {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(data), },
        "model": MODEL_ID,
        "n_terms_requested": n_terms,
        "terms_returned": len(items),
        "text_chars_sent": len(text),
        "items": items, }
