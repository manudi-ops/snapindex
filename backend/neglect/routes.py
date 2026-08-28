from flask import Blueprint, request, jsonify
from neglect.engine import detect_neglect
from db.models import db, AcademicResource, Category, Reminder, KnowledgeNeglectAnalysis

neglect_bp = Blueprint("neglect", __name__)


@neglect_bp.route("/neglect/analyse", methods=["POST"])
def analyse():
    data = request.get_json()
    user_id = data.get("userID")

    if not user_id:
        return jsonify({"error": "userID is required"}), 400

    result = detect_neglect(user_id)
    return jsonify(result), 200


@neglect_bp.route("/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):
    resources = AcademicResource.query.filter_by(userID=user_id).all()

    by_category = {}
    for r in resources:
        if r.categoryID:
            by_category.setdefault(r.categoryID, []).append(r)

    from db.models import BehaviourLog

    module_counts = []
    for cat_id, res_list in by_category.items():
        cat = Category.query.get(cat_id)
        resource_ids = [r.resourceID for r in res_list]
        open_count = BehaviourLog.query.filter(
            BehaviourLog.resourceID.in_(resource_ids),
            BehaviourLog.activityType == "open"
        ).count()
        access_ratio = open_count / len(res_list) if res_list else 0
        module_counts.append({
            "categoryName": cat.categoryName if cat else "Unknown",
            "resourceCount": len(res_list),
            "openCount": open_count,
            "accessRatio": round(access_ratio, 2),
        })

    most_collected = max(module_counts, key=lambda m: m["resourceCount"]) if module_counts else None
    most_engaged = max(module_counts, key=lambda m: m["accessRatio"]) if module_counts else None
    least_engaged = min(module_counts, key=lambda m: m["accessRatio"]) if module_counts else None

    all_analyses = (KnowledgeNeglectAnalysis.query
                     .filter_by(userID=user_id)
                     .order_by(KnowledgeNeglectAnalysis.generatedDate.desc())
                     .all())
    seen_categories = set()
    neglect_summary = []
    for a in all_analyses:
        if a.categoryID in seen_categories:
            continue
        seen_categories.add(a.categoryID)
        cat = Category.query.get(a.categoryID)
        neglect_summary.append({
            "categoryName": cat.categoryName if cat else "Unknown",
            "summary": a.summary,
            "generatedDate": a.generatedDate.isoformat(),
        })
        if len(neglect_summary) >= 5:
            break

    active_reminders = (Reminder.query
                         .filter_by(userID=user_id, status="active")
                         .order_by(Reminder.reminderDate.desc())
                         .all())
    reminders = [{"reminderID": r.reminderID, "message": r.message} for r in active_reminders]

    recent_resources = (AcademicResource.query
                         .filter_by(userID=user_id)
                         .order_by(AcademicResource.uploadDate.desc())
                         .limit(5).all())
    recent = [{"resourceID": r.resourceID, "title": r.title, "uploadDate": r.uploadDate.isoformat()} for r in recent_resources]

    return jsonify({
        "totalResources": len(resources),
        "mostCollected": most_collected,
        "mostEngaged": most_engaged,
        "leastEngaged": least_engaged,
        "neglectSummary": neglect_summary,
        "reminders": reminders,
        "recentResources": recent,
    }), 200


@neglect_bp.route("/reminders/<int:reminder_id>/dismiss", methods=["PUT"])
def dismiss_reminder(reminder_id):
    reminder = Reminder.query.get(reminder_id)
    if not reminder:
        return jsonify({"error": "Reminder not found"}), 404
    reminder.status = "dismissed"
    db.session.commit()
    return jsonify({"message": "Reminder dismissed"}), 200