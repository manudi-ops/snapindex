import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
from db.models import db, AcademicResource
from search.embedding_service import generate_embedding
from search.faiss_store import add_embedding

ingestion_bp = Blueprint("ingestion", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
OCR_CONFIDENCE_THRESHOLD = 60  # out of 100, per FR3

def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


@ingestion_bp.route("/resources/upload", methods=["POST"])
def upload_resource():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    user_id = request.form.get("userID")

    if not user_id:
        return jsonify({"error": "userID is required"}), 400
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    extension = get_extension(filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    extracted_text = None
    confidence = None
    needs_review = False

    if extension in IMAGE_EXTENSIONS:
        try:
            image = Image.open(save_path)
            ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            words = [w for w in ocr_data["text"] if w.strip() != ""]
            confidences = [int(c) for c, w in zip(ocr_data["conf"], ocr_data["text"]) if w.strip() != "" and c != "-1"]

            extracted_text = " ".join(words)
            confidence = sum(confidences) / len(confidences) if confidences else 0
            needs_review = confidence < OCR_CONFIDENCE_THRESHOLD

        except Exception as e:
            return jsonify({"error": f"OCR failed: {str(e)}"}), 500

    resource = AcademicResource(
        userID=user_id,
        title=filename,
        fileName=filename,
        filePath=save_path,
        fileType=extension,
        extractedText=extracted_text,
        ocrConfidence=confidence,
        needsReview=needs_review,
    )
    db.session.add(resource)
    db.session.commit()

    embedding_vector_id = None
    if extracted_text:
        embedding = generate_embedding(extracted_text)
        if embedding is not None:
            embedding_vector_id = add_embedding(resource.resourceID, embedding)
            resource.embeddingVectorID = embedding_vector_id
            db.session.commit()

    return jsonify({
        "message": "Resource uploaded successfully",
        "resourceID": resource.resourceID,
        "extractedText": extracted_text,
        "ocrConfidence": confidence,
        "needsReview": needs_review,
    }), 201