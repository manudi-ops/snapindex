import numpy as np
from db.models import Category
from search.embedding_service import generate_embedding

FALLBACK_THRESHOLD = 0.15 

_category_cache = None  # list of - (categoryID, categoryName, embedding)

def reset_category_cache():
    global _category_cache
    _category_cache = None

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_category_embeddings():
    global _category_cache
    if _category_cache is None:
        print("Generating category anchor embeddings (first call only)...")
        categories = Category.query.all()
        _category_cache = []
        for c in categories:
            anchor_text = c.description or c.categoryName
            embedding = generate_embedding(anchor_text)
            _category_cache.append((c.categoryID, c.categoryName, embedding))
    return _category_cache

def classify_text(resource_embedding):
    if resource_embedding is None:
        return None, "General / Uncategorized", 0.0

    categories = get_category_embeddings()
    best_id, best_name, best_score = None, "General / Uncategorized", -1.0

    for cat_id, cat_name, cat_embedding in categories:
        if cat_name == "General / Uncategorized":
            continue
        score = cosine_similarity(resource_embedding, cat_embedding)
        if score > best_score:
            best_id, best_name, best_score = cat_id, cat_name, score

    if best_score < FALLBACK_THRESHOLD:
        fallback = next((c for c in categories if c[1] == "General / Uncategorized"), None)
        if fallback:
            return fallback[0], fallback[1], best_score

    return best_id, best_name, best_score