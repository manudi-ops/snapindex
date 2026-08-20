from db.models import db, BehaviourLog

def log_activity(user_id, activity_type, resource_id=None):
    """Records an interaction event. This is the sole data source
    the neglect-detection engine (Isolation Forest) will analyse."""
    entry = BehaviourLog(
        userID=user_id,
        resourceID=resource_id,
        activityType=activity_type,
    )
    db.session.add(entry)
    db.session.commit()