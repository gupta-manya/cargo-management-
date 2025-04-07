from algorithms import logs
from configuration import log_collection
from datetime import datetime
from pymongo.collection import Collection


def identify_waste_items(cargo_collection: Collection):
    today = datetime.utcnow()
    query = {
        "$or": [
            {"expiry_date": {"$lt": today}},
            {"usage_limit": {"$lte": 0}}
        ]
    }
    waste_items = list(cargo_collection.find(query))
    result = []

    for item in waste_items:
        reason = "Expired" if item.get("expiry_date") and item["expiry_date"] < today else "Out of Uses"
        result.append({
            "itemId": item["item_id"],
            "name": item["name"],
            "reason": reason,
            "containerId": item["container_id"],
            "position": {
                "startCoordinates": item["startCoordinates"],
                "endCoordinates": item["endCoordinates"]
            }
        })

    return result


def plan_return_of_waste(cargo_collection: Collection, undocking_container_id: str, undocking_date: str, max_weight: float):
    waste_items = identify_waste_items(cargo_collection)
    selected_items = []
    total_weight = 0
    total_volume = 0

    for item in waste_items:
        mongo_item = cargo_collection.find_one({"item_id": item["itemId"]})
        item_weight = mongo_item["mass_kg"]
        item_volume = mongo_item["width_cm"] * mongo_item["depth_cm"] * mongo_item["height"]

        if total_weight + item_weight <= max_weight:
            selected_items.append((item, mongo_item))
            total_weight += item_weight
            total_volume += item_volume

    return_plan = []
    retrieval_steps = []
    return_manifest = []

    for idx, (item_info, mongo_item) in enumerate(selected_items, start=1):
        return_plan.append({
            "step": idx,
            "itemId": item_info["itemId"],
            "itemName": item_info["name"],
            "fromContainer": item_info["containerId"],
            "toContainer": undocking_container_id
        })
        retrieval_steps.append({
            "step": idx,
            "action": "retrieve",
            "itemId": item_info["itemId"],
            "itemName": item_info["name"]
        })
        return_manifest.append({
            "itemId": item_info["itemId"],
            "name": item_info["name"],
            "reason": item_info["reason"]
        })

    manifest = {
        "undockingContainerId": undocking_container_id,
        "undockingDate": undocking_date,
        "returnItems": return_manifest,
        "totalVolume": total_volume,
        "totalWeight": total_weight
    }

    return {
        "returnPlan": return_plan,
        "retrievalSteps": retrieval_steps,
        "returnManifest": manifest
    }


def complete_undocking(cargo_collection: Collection, undocking_container_id: str):
    result = cargo_collection.delete_many({"container_id": undocking_container_id})
    return result.deleted_count