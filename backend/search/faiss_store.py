import faiss
import numpy as np
import os
import pickle

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size
INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
IDMAP_PATH = os.path.join(os.path.dirname(__file__), "faiss_idmap.pkl")

_index = None
_id_map = []  # position in FAISS index -> resourceID

def get_index():
    global _index, _id_map
    if _index is None:
        if os.path.exists(INDEX_PATH):
            _index = faiss.read_index(INDEX_PATH)
            with open(IDMAP_PATH, "rb") as f:
                _id_map = pickle.load(f)
        else:
            _index = faiss.IndexFlatIP(EMBEDDING_DIM)
            _id_map = []
    return _index

def add_embedding(resource_id, embedding_vector):
    index = get_index()
    vector = np.array([embedding_vector], dtype="float32")
    faiss.normalize_L2(vector)
    index.add(vector)
    _id_map.append(resource_id)
    _save()
    return len(_id_map) - 1  # position just added which matches the embeddingVectorID

def _save():
    faiss.write_index(_index, INDEX_PATH)
    with open(IDMAP_PATH, "wb") as f:
        pickle.dump(_id_map, f)