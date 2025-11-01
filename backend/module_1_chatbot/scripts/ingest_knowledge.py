# /module_1_chatbot/scripts/ingest_knowledge.py
import os
import chromadb
from sentence_transformers import SentenceTransformer

# 1. Inisialisasi ChromaDB (akan membuat folder 'chroma_db' di root)
# MENGAPA: PersistentClient menyimpan DB ke disk, jadi kita tidak
# kehilangan data saat container restart.
db_path = "./chroma_db"
client = chromadb.PersistentClient(path=db_path)

# 2. Buat atau dapatkan Collection (tabel)
# MENGAPA: Kita pakai embedding default SOTA (all-MiniLM-L6-v2)
# yang ringan dan efektif.
collection_name = "haji_umrah_kb"
try:
    collection = client.get_collection(name=collection_name)
    print(f"Collection '{collection_name}' sudah ada.")
except Exception:
    collection = client.create_collection(name=collection_name)
    print(f"Collection '{collection_name}' telah dibuat.")

# 3. Path ke Knowledge Base Anda
kb_path = "./knowledge_base"

# 4. Fungsi untuk membaca dan memproses file
def ingest_data():
    doc_id = 1
    for filename in os.listdir(kb_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(kb_path, filename)
            print(f"Memproses file: {filename}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                # Kita bagi per paragraf kosong
                chunks = f.read().split('\n\n')
                
                for i, chunk in enumerate(chunks):
                    if chunk.strip(): # Hanya jika tidak kosong
                        unique_id = f"doc_{doc_id}_{i}"
                        
                        # Menambahkan dokumen ke ChromaDB
                        # ChromaDB akan otomatis menghitung embeddings
                        collection.add(
                            documents=[chunk.strip()],
                            metadatas=[{"source": filename}],
                            ids=[unique_id]
                        )
    print("Semua dokumen berhasil diproses dan disimpan ke Vector DB.")

if __name__ == "__main__":
    # Cek apakah data sudah ada untuk menghindari duplikat
    if collection.count() == 0:
        ingest_data()
    else:
        print("Data sudah ada di Vector DB, proses ingest dilewati.")