from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model (first call only, may take a moment)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embedding(text):
    if not text or not text.strip():
        return None
    model = get_model()
    embedding = model.encode(text)
    return embedding