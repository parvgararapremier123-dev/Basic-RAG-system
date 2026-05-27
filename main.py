import eel
import re
import fitz
import numpy as np
import pandas as pd
import ollama
import threading
import time
from sentence_transformers import SentenceTransformer
from tkinter import filedialog, Tk

# Initialize Eel
eel.init('web')

class RAGBackend:
    def __init__(self):
        self.model = None
        self.vector_db = None
        self.library = []

    def load_model(self):
        print("[BACKEND] Loading SentenceTransformer model...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[BACKEND] Model loaded successfully.")
            eel.updateStatus("Ready")
        except Exception as e:
            print(f"[BACKEND] Error loading model: {e}")
            eel.updateStatus(f"Model Error")

    def process_pdf(self, pdf_path):
        if not self.model: 
            print("[BACKEND] Model not loaded yet.")
            return False
        try:
            print(f"[BACKEND] Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            text = " ".join([page.get_text() for page in doc])
            text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE).strip()
            words = text.split()
            chunks = [" ".join(words[i:i+400]) for i in range(0, len(words), 350)]
            
            if not chunks: 
                print("[BACKEND] No text found in PDF.")
                return False
            
            print(f"[BACKEND] Embedding {len(chunks)} chunks...")
            embeddings = self.model.encode(chunks)
            self.vector_db = pd.DataFrame({'chunk_text': chunks, 'embedding': list(embeddings)})
            
            filename = pdf_path.split("/")[-1]
            if filename not in self.library:
                self.library.append(filename)
            print("[BACKEND] PDF processed and indexed.")
            return filename
        except Exception as e:
            print(f"[BACKEND] Error processing PDF: {e}")
            return False

    def query(self, question):
        if self.vector_db is None or self.model is None: 
            return None
        print(f"[BACKEND] Searching for relevant context...")
        q_vec = self.model.encode(question)
        sims = self.vector_db['embedding'].apply(
            lambda x: np.dot(q_vec, x) / (np.linalg.norm(q_vec) * np.linalg.norm(x))
        )
        return self.vector_db.loc[sims.idxmax(), 'chunk_text']

backend = RAGBackend()


@eel.expose
def ask_ai(question):
    print(f"[UI] Question received: {question}")
    
    if backend.vector_db is None:
        eel.streamResponse("⚠️ Please upload and index a PDF document first using the '+' button.")
        eel.finishResponse()
        return

    def run():
        try:
            context = backend.query(question)
            if not context:
                eel.streamResponse("System Error: Context retrieval failed.")
                eel.finishResponse()
                return

            print("[BACKEND] Querying Ollama...")
            response = ollama.chat(
                model='qwen2.5',
                messages=[{'role': 'user', 'content': f"Context: {context}\n\nQuestion: {question}"}],
                stream=True
            )
            
            # Send an initial signal to hide the thinking indicator instantly
            eel.streamResponse("") 
            
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    eel.streamResponse(content)
            
            eel.finishResponse()
            print("[BACKEND] Response stream complete.")
        except Exception as e:
            print(f"[BACKEND] AI Error: {e}")
            eel.streamResponse(f"System Error: Is Ollama running? {str(e)}")
            eel.finishResponse()

    threading.Thread(target=run, daemon=True).start()

@eel.expose
def upload_pdf():
    print("[UI] Opening file picker...")
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    root.destroy()

    if file_path:
        eel.updateStatus("Processing PDF...")
        def process():
            filename = backend.process_pdf(file_path)
            if filename:
                eel.addDocumentToList(filename)
                eel.updateStatus("Ready")
            else:
                eel.updateStatus("Processing Error")
        threading.Thread(target=process, daemon=True).start()
    else:
        eel.updateStatus("Ready")

@eel.expose
def start_backend():
    threading.Thread(target=backend.load_model, daemon=True).start()

if __name__ == "__main__":
    start_backend()
    try:
        eel.start('index.html', size=(1200, 850))
    except Exception:
        eel.start('index.html', size=(1200, 850), mode='default')