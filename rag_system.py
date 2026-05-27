# Run `ollama run qwen2.5` before executing this script
import re
import fitz
import numpy as np
import pandas as pd
import ollama
from sentence_transformers import SentenceTransformer

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page in doc:
        text = page.get_text()
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text_blocks.append(text)
    return " ".join(text_blocks).strip()

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    if not words:
        return chunks
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        if i + chunk_size >= len(words):
            break
        i += chunk_size - overlap
    return chunks

def embed_chunks(chunks: list[str]) -> tuple[pd.DataFrame, SentenceTransformer]:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    df = pd.DataFrame({
        'chunk_text': chunks,
        'embedding': list(embeddings)
    })
    return df, model

def query_pdf(question: str, dataframe: pd.DataFrame, model: SentenceTransformer) -> str:
    question_vector = model.encode(question)
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    similarities = dataframe['embedding'].apply(lambda x: cosine_similarity(question_vector, x))
    best_idx = similarities.idxmax()
    return dataframe.loc[best_idx, 'chunk_text']

def generate_answer(question: str, context_chunk: str) -> str:
    prompt = f"Context: {context_chunk}\n\nUser Question: {question}\n\nInstruction: Answer the question strictly based on the provided context. If the answer isn't in the context, say you don't know."
    response = ollama.chat(
        model='qwen2.5',
        messages=[{'role': 'user', 'content': prompt}],
        stream=True
    )
    answer = ""
    for chunk in response:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        answer += content
    print()
    return answer

if __name__ == "__main__":
    pdf_file = '10K-NVDA.pdf'
    try:
        extracted_text = extract_text(pdf_file)
        text_chunks = chunk_text(extracted_text, chunk_size=400, overlap=50)
        df, embed_model = embed_chunks(text_chunks)
        user_question = 'What are the main risk factors mentioned for NVIDIA?'
        best_chunk = query_pdf(user_question, df, embed_model)
        final_answer = generate_answer(user_question, best_chunk)
    except Exception as e:
        print(e)