import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import openai
from docx import Document

ORIENTATION_PATH = Path(__file__).with_name("orientacao.docx")


def _load_orientation() -> str:
    try:
        doc = Document(ORIENTATION_PATH)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        try:
            with open(ORIENTATION_PATH.with_suffix(".txt"), "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""


ORIENTATION_TEXT = _load_orientation()
openai.api_key = os.getenv("OPENAI_API_KEY")


def answer_question(question: str) -> str:
    """Return an answer to the question using the orientation text."""
    messages = [
        {
            "role": "system",
            "content": (
                "Responda em português utilizando o texto de orientação a seguir como"
                " referência:\n" + ORIENTATION_TEXT
            ),
        },
        {"role": "user", "content": question},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def analyze_answers(answers: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
    """Analyze form answers and suggest clause markers to keep or remove."""
    messages = [
        {
            "role": "system",
            "content": (
                "Você é um assistente que avalia respostas de um formulário para gerar"
                " um Termo de Referência. Utilize o texto de orientação abaixo para"
                " embasar suas decisões. Retorne um JSON com as chaves 'manter',"
                " 'excluir' e 'sugestoes'.\n" + ORIENTATION_TEXT
            ),
        },
        {
            "role": "user",
            "content": "Respostas do usuário:\n" + json.dumps(answers, ensure_ascii=False, indent=2),
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0,
    )
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        keep = data.get("manter", [])
        remove = data.get("excluir", [])
        suggestions = data.get("sugestoes", [])
    except Exception:
        keep, remove, suggestions = [], [], [content]
    return keep, remove, suggestions
