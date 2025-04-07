from pymongo.collection import Collection

def rebalance_zones(cargo_collection: Collection, zone_collection: Collection):
    # Get overloaded zones (more than 90% capacity)
    overloaded = list(zone_collection.find({
        "$expr": {"$gt": ["$used", {"$multiply": [0.9, "$capacity"]}]}
    }))
    
    # Get underloaded zones (less than 50% usage)
    underloaded = list(zone_collection.find({
        "$expr": {"$lt": ["$used", {"$multiply": [0.5, "$capacity"]}]}
    }))

    moved_count = 0
    for over in overloaded:
        items = list(cargo_collection.find({"zone": over["zone_id"]}).limit(5))  # Max 5 moves
        for item in items:
            for under in underloaded:
                if under["category"] == item["type"] and under["used"] < under["capacity"]:
                    cargo_collection.update_one({"_id": item["_id"]}, {"$set": {"zone": under["zone_id"]}})
                    zone_collection.update_one({"zone_id": over["zone_id"]}, {"$inc": {"used": -1}})
                    zone_collection.update_one({"zone_id": under["zone_id"]}, {"$inc": {"used": 1}})
                    moved_count += 1
                    break
    return {"message": f"Rebalanced {moved_count} items"}
