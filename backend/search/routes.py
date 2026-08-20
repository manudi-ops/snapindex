from flask import Blueprint, request, jsonify
from db.models import AcademicResource
from search.embedding_service import generate_embedding
from search.faiss_store import search_index
from db.activity_logger import log_activity

search_bp = Blueprint("search", __name__)


def rerank(results, query_text):
    """Secondary relevance signal: boost results whose extracted text
    directly contains query words, correcting for surface-feature bias
    in raw embedding similarity alone."""
    query_words = set(query_text.lower().split())

    for r in results:
        resource = AcademicResource.query.get(r["resourceID"])
        if resource is None:
            r["keywordOverlap"] = 0
            r["combinedScore"] = r["score"]
        else:
            text = (resource.extractedText or "").lower()
            overlap = sum(1 for w in query_words if w in text)
            r["keywordOverlap"] = overlap
            r["combinedScore"] = r["score"] + (overlap * 0.05)

    results.sort(key=lambda r: r["combinedScore"], reverse=True)
    return results


@search_bp.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "").strip()
    user_id = data.get("userID")

    if not query:
        return jsonify({"error": "Search query cannot be empty"}), 400

    query_vector = generate_embedding(query)
    if query_vector is None:
        return jsonify({"error": "Could not process query"}), 500

    raw_results = search_index(query_vector, k=10)

    if not raw_results:
        return jsonify({"results": [], "message": "No results found"}), 200

    reranked = rerank(raw_results, query)

    output = []
    for r in reranked[:5]:
        resource = AcademicResource.query.get(r["resourceID"])
        if resource:
            output.append({
                "resourceID": resource.resourceID,
                "title": resource.title,
                "extractedText": (resource.extractedText or "")[:200],
                "similarityScore": round(r["score"] * 100, 1),
                "fileType": resource.fileType,
            })

    if user_id:
        log_activity(user_id, "search")

    return jsonify({"results": output}), 200

@search_bp.route("/resources/<int:resource_id>/open", methods=["POST"])
def open_resource(resource_id):
    data = request.get_json()
    user_id = data.get("userID")

    if not user_id:
        return jsonify({"error": "userID is required"}), 400

    log_activity(user_id, "open", resource_id)
    return jsonify({"message": "Access logged"}), 200