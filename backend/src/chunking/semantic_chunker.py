import os
import re
import json
import yaml
import numpy as np
from pypdf import PdfReader
import spacy
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Import the helper we just made
try:
    from src.chunking.buffer_merger import BufferMerger
except ImportError:
    from buffer_merger import BufferMerger

# Load Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

nlp = spacy.load("en_core_web_sm")

class SemanticChunker:
    def __init__(self):
        print(f"Loading embedding model: {config['chunking']['model_name']}...")
        self.model = SentenceTransformer(config['chunking']['model_name'])
        
        # Initialize the separate Merger class [cite: 2280]
        self.merger = BufferMerger(
            threshold=config['chunking']['similarity_threshold'],
            max_tokens=config['chunking']['chunk_size_tokens']
        )

    def clean_text(self, text):
        # FIXED: Simplified regex to avoid SyntaxError
        text = re.sub(r"source: \d+", "", text) 
        text = re.sub(r"\n\d+\n", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def get_sentences(self, pdf_path):
        full_path = os.path.join(BASE_DIR, pdf_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"PDF not found at {full_path}")
            
        reader = PdfReader(full_path)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text += t + " "
        
        full_text = self.clean_text(full_text)
        doc = nlp(full_text)
        # Filter noise (short segments)
        return [sent.text for sent in doc.sents if len(sent.text) > 20]

    def chunk_data(self):
        sentences = self.get_sentences(config['paths']['pdf_path'])
        print(f"Generating embeddings for {len(sentences)} sentences...")
        embeddings = self.model.encode(sentences)
        
        chunks = []
        current_chunk_text = []
        current_chunk_emb = []
        current_tokens = 0
        
        print("Grouping sentences into semantic chunks...")
        for i in tqdm(range(len(sentences))):
            sent = sentences[i]
            emb = embeddings[i]
            tokens = len(sent.split())
            
            # Use the separate Merger Logic
            should_merge = self.merger.should_merge(
                current_chunk_emb, emb, current_tokens, tokens
            )
            
            if should_merge:
                current_chunk_text.append(sent)
                current_chunk_emb.append(emb)
                current_tokens += tokens
            else:
                # Save chunk
                chunks.append({
                    "id": len(chunks),
                    "text": " ".join(current_chunk_text),
                    "token_count": current_tokens,
                    "embedding": np.mean(current_chunk_emb, axis=0).tolist()
                })
                # Start new chunk
                current_chunk_text = [sent]
                current_chunk_emb = [emb]
                current_tokens = tokens
        
        # Save final piece
        if current_chunk_text:
            chunks.append({
                "id": len(chunks),
                "text": " ".join(current_chunk_text),
                "token_count": current_tokens,
                "embedding": np.mean(current_chunk_emb, axis=0).tolist()
            })
            
        output_path = os.path.join(BASE_DIR, config['paths']['output_chunks'])
        with open(output_path, 'w') as f:
            json.dump(chunks, f)
        print(f"SUCCESS: Saved {len(chunks)} chunks to {output_path}")

if __name__ == "__main__":
    chunker = SemanticChunker()
    chunker.chunk_data()