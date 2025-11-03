import os
import chromadb
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# 1. Inisialisasi ChromaDB
db_path = "./chroma_db"
client = chromadb.PersistentClient(path=db_path)

# 2. Buat atau dapatkan Collection (tabel)
collection_name = "haji_umrah_kb" # <-- KITA AKAN PAKAI NAMA INI
try:
    collection = client.get_collection(name=collection_name)
    logger.info(f"Collection '{collection_name}' sudah ada.")
except Exception:
    collection = client.create_collection(name=collection_name)
    logger.info(f"Collection '{collection_name}' telah dibuat.")

# 3. Path ke Knowledge Base Anda
kb_path = "./knowledge_base" # <-- Pastikan folder ini ada dan berisi .txt

# 4. Fungsi untuk membaca dan memproses file
def ingest_data():
    doc_id = 1
    if not os.path.exists(kb_path):
        logger.warning(f"Folder '{kb_path}' tidak ditemukan. Tidak ada data untuk ingest.")
        return

    for filename in os.listdir(kb_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(kb_path, filename)
            logger.info(f"Memproses file: {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                chunks = f.read().split('\n\n')
                
                for i, chunk in enumerate(chunks):
                    if chunk.strip(): 
                        unique_id = f"doc_{doc_id}_{i}"
                        
                        collection.add(
                            documents=[chunk.strip()],
                            metadatas=[{"source": filename}],
                            ids=[unique_id]
                        )
                        doc_id += 1 # Pindahkan increment ke sini agar ID unik
                        
    logger.info("Semua dokumen berhasil diproses dan disimpan ke Vector DB.")

if __name__ == "__main__":
    if collection.count() == 0:
        ingest_data()
    else:
        logger.info("Data sudah ada di Vector DB, proses ingest dilewati.")