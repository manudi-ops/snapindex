from flask import Blueprint, request, jsonify
from db.models import db, Category, AcademicResource
from classification.category_service import reset_category_cache

classification_bp = Blueprint("classification", __name__)


@classification_bp.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify([
        {"categoryID": c.categoryID, "categoryName": c.categoryName}
        for c in categories
    ]), 200


@classification_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    name = data.get("categoryName", "").strip()
    description = data.get("description", "").strip()

    if not name:
        return jsonify({"error": "categoryName is required"}), 400

    existing = Category.query.filter_by(categoryName=name).first()
    if existing:
        return jsonify({"error": "Category already exists", "categoryID": existing.categoryID}), 400

    category = Category(categoryName=name, description=description or name)
    db.session.add(category)
    db.session.commit()

    reset_category_cache()  

    return jsonify({"message": "Category created", "categoryID": category.categoryID}), 201


@classification_bp.route("/resources/<int:resource_id>/category", methods=["PUT"])
def correct_category(resource_id):
    data = request.get_json()
    category_id = data.get("categoryID")

    if not category_id:
        return jsonify({"error": "categoryID is required"}), 400

    resource = AcademicResource.query.get(resource_id)
    if not resource:
        return jsonify({"error": "Resource not found"}), 404

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    resource.categoryID = category_id
    db.session.commit()

    return jsonify({"message": "Category updated", "category": category.categoryName}), 200