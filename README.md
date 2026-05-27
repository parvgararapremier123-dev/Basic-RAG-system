# Basic RAG System

A simple, local Retrieval-Augmented Generation (RAG) system built with Python, Eel (for the web GUI), Sentence Transformers, and Ollama. This project allows you to upload PDF documents, index their contents using embeddings, and ask questions about the document. It provides answers powered by a local Large Language Model (LLM).

## Features
- **Local PDF Processing**: Extracts text from PDFs using PyMuPDF (`fitz`).
- **Semantic Search**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to chunk text and embed it for fast, relevant context retrieval.
- **Local LLM Integration**: Uses [Ollama](https://ollama.com/) to run the `qwen2.5` model locally for answering questions based on the retrieved context. No data leaves your machine.
- **Web Interface**: A clean graphical user interface built with `eel`, HTML, CSS, and JavaScript, providing a chat-like experience to interact with your documents.

## Project Structure
- `main.py`: The entry point for the Web GUI application. It initializes the Eel web server, handles PDF processing, vector embeddings, and querying.
- `rag_system.py`: A standalone CLI script demonstrating the core RAG pipeline (extraction, chunking, embedding, similarity search, and answer generation).
- `web/`: Contains the frontend assets (`index.html`, `style.css`, `script.js`) for the Eel application.
- `requirements.txt`: List of required Python packages.
- `10K-NVDA.pdf`: A sample PDF document included for testing.

## Prerequisites

1. **Python 3.8+** installed on your system.
2. **Ollama**: You must have Ollama installed and running.
   - Download it from [ollama.com](https://ollama.com/).
   - Once installed, pull the required model by executing this command in your terminal (keep it running in the background):
     ```bash
     ollama run qwen2.5
     ```

## Installation

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web GUI (Recommended)
To launch the graphical user interface:
```bash
python main.py
```
1. Click the upload button to select a PDF file.
2. Wait for the application status to show that it is ready (the PDF is being chunked and embedded).
3. Type your question in the chat box to receive context-aware answers from the local AI based strictly on the uploaded document.

### Command Line Script
To run the basic standalone script (which runs a hardcoded query on the included sample `10K-NVDA.pdf`):
```bash
python rag_system.py
```
