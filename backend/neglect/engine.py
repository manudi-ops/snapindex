from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from db.models import db, AcademicResource, BehaviourLog, KnowledgeNeglectAnalysis, Category

ACCESS_RATIO_THRESHOLD = 0.5


def build_category_features(user_id):
    """One feature vector per category the user has resources in:
    [upload_count, open_count, days_since_last_access, access_ratio].
    BehaviourLog is the sole data source — no other signal used."""
    resources = AcademicResource.query.filter_by(userID=user_id).all()

    by_category = {}
    for r in resources:
        if r.categoryID is None:
            continue
        by_category.setdefault(r.categoryID, []).append(r)

    category_ids = []
    features = []
    now = datetime.utcnow()

    for cat_id, cat_resources in by_category.items():
        resource_ids = [r.resourceID for r in cat_resources]
        upload_count = len(cat_resources)

        open_logs = BehaviourLog.query.filter(
            BehaviourLog.resourceID.in_(resource_ids),
            BehaviourLog.activityType == "open"
        ).all()
        open_count = len(open_logs)

        if open_logs:
            last_access = max(log.accessDate for log in open_logs)
        else:
            last_access = max(r.uploadDate for r in cat_resources)
        days_since_access = max((now - last_access).total_seconds() / 86400, 0)

        access_ratio = open_count / upload_count if upload_count else 0

        category_ids.append(cat_id)
        features.append([upload_count, open_count, days_since_access, access_ratio])

    return category_ids, features


def detect_neglect(user_id):
    category_ids, features = build_category_features(user_id)

    if len(features) < 2:
        return {"status": "insufficient_data",
                "message": "Not enough categories with resources yet to run neglect detection."}

    X = np.array(features)
    model = IsolationForest(contamination=0.3, random_state=42)
    predictions = model.fit_predict(X)   
    scores = model.score_samples(X)      

    neglected = []
    for i, cat_id in enumerate(category_ids):
        upload_count, open_count, days_since_access, access_ratio = features[i]
        is_outlier = predictions[i] == -1

        is_neglect_pattern = access_ratio < ACCESS_RATIO_THRESHOLD and upload_count >= 2

        if is_neglect_pattern:
            category = Category.query.get(cat_id)
            summary = (f"{upload_count} resource(s) collected, only {open_count} opened "
                       f"({round(access_ratio * 100)}% access rate).")

            neglected.append({
                "categoryID": cat_id,
                "categoryName": category.categoryName if category else "Unknown",
                "uploadCount": upload_count,
                "openCount": open_count,
                "daysSinceAccess": round(days_since_access, 1),
                "accessRatio": round(access_ratio, 2),
                "anomalyScore": round(float(scores[i]), 3),
                "summary": summary,
            })

            record = KnowledgeNeglectAnalysis(
                userID=user_id,
                categoryID=cat_id,
                neglectScore=float(scores[i]),
                summary=summary,
            )
            db.session.add(record)

    db.session.commit()

    if not neglected:
        return {"status": "no_neglect_found", "message": "No neglected topics identified."}

    return {"status": "neglect_found", "neglected": neglected}