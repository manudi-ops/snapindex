from flask import Blueprint, request, jsonify
from neglect.engine import detect_neglect

neglect_bp = Blueprint("neglect", __name__)


@neglect_bp.route("/neglect/analyse", methods=["POST"])
def analyse():
    data = request.get_json()
    user_id = data.get("userID")

    if not user_id:
        return jsonify({"error": "userID is required"}), 400

    result = detect_neglect(user_id)
    return jsonify(result), 200