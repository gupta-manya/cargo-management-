from datetime import datetime

def log_action(log_collection, userId: str, actionType: str, itemId: str, details: dict):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "userId": userId,
        "actionType": actionType,
        "itemId": itemId,
        "details": details
    }
    log_collection.insert_one(log_entry)
