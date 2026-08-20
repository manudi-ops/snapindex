from app import app
from db.models import BehaviourLog

with app.app_context():
    logs = BehaviourLog.query.all()
    for l in logs:
        print(l.logID, l.userID, l.activityType, l.resourceID, l.accessDate)