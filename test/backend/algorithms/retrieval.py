from datetime import date
from algorithms import logs
from configuration import log_collection


def log_action(log_collection, item, userId=None, actionType="retrieval"):
    """
    Logs an action related to item retrieval.

    Args:
        log_collection: The collection where logs are stored.
        item: The item dictionary to log.
        userId: ID of the user who performed the action. Defaults to item["retrieved_by"] or "system".
        actionType: Type of the action, default is "retrieval".
    """
    if userId is None:
        userId = item.get("retrieved_by", "system")

    itemId = item["item_id"]
    details = {
        "fromContainer": item["container_id"],
        "zone": item.get("zone", ""),
        "coordinates": {
            "start": item.get("startCoordinates"),
            "end": item.get("endCoordinates")
        }
    }

    logs.log_action(
        log_collection,
        userId=userId,
        actionType=actionType,
        itemId=itemId,
        details=details
    )


def retrieve_item(item_id, cargo_collection, zone_collection):
    """
    Finds the best match for an itemId, preferring:
    - closest to expiry
    - easiest to access (lowest z, y, x)
    - logs and removes it from cargo_collection
    """
    matches = list(cargo_collection.find({"item_id": item_id}))
    if not matches:
        return {"message": "Item not found"}

    # Prioritize by expiry and coordinate accessibility
    def item_score(item):
        expiry = item.get("expiry_date")
        coords = item.get("startCoordinates", {})
        return (
            expiry or date.max,
            coords.get("z", 999),
            coords.get("y", 999),
            coords.get("x", 999)
        )

    matches.sort(key=item_score)
    target = matches[0]

    retrieval_steps = [{
        "step": 1,
        "action": "retrieve",
        "itemId": target["item_id"],
        "itemName": target["name"]
    }]

    # Log the action
    log_action(log_collection, target)

    # Remove item from storage
    cargo_collection.delete_one({"_id": target["_id"]})

    return {
        "item": {
            "itemId": target["item_id"],
            "name": target["name"],
            "containerId": target["container_id"],
            "zone": target.get("zone"),
            "position": {
                "startCoordinates": target.get("startCoordinates"),
                "endCoordinates": target.get("endCoordinates")
            }
        },
        "retrievalSteps": retrieval_steps,
        "steps_required": len(retrieval_steps)
    }
