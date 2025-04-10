from pymongo.collection import Collection
from pymongo import MongoClient
from typing import Tuple, List, Dict, Optional
from datetime import datetime
from itertools import permutations
client = MongoClient("mongodb+srv://manya:manya23@clusternew.wop6qyw.mongodb.net/?retryWrites=true&w=majority&appName=clusternew")
db = client["cargo"] 

zone_collection: Collection = db["zones"]       
cargo_collection: Collection = db["cargodata"]    


def get_sorted_containers(zone_collection: Collection, preferred_zone: Optional[str]) -> List[Dict]:
    query = {"zone": preferred_zone} if preferred_zone else {}
    containers = list(zone_collection.find(query))
    if preferred_zone:
        containers.sort(key=lambda c: c.get("zone") != preferred_zone)
    return containers


def is_overlapping(start1: Tuple[float, float, float], end1: Tuple[float, float, float],
                   start2: Tuple[float, float, float], end2: Tuple[float, float, float]) -> bool:
    return not (
        end1[0] <= start2[0] or start1[0] >= end2[0] or
        end1[1] <= start2[1] or start1[1] >= end2[1] or
        end1[2] <= start2[2] or start1[2] >= end2[2]
    )


def find_empty_space(container: dict, item_dims: Tuple[float, float, float],
                     used_space: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]]) -> Tuple:
    max_x, max_y, max_z = container["width_cm"], container["depth_cm"], container["height_cm"]
    item_w, item_d, item_h = item_dims

    step = 1
    for x in range(0, int(max_x - item_w) + 1, int(step)):

        for y in range(0, int(max_y - item_d) + 1, int(step)):
            for z in range(0, int(max_z - item_h) + 1, int(step)):
                start = (x, y, z)
                end = (x + item_w, y + item_d, z + item_h)

                if all(not is_overlapping(start, end, s, e) for s, e in used_space):
                    return start, end
    return None, None


def store_item(item: dict, cargo_collection: Collection, zone_collection: Collection) -> dict:
    preferred_zone = item.get("preferred_zone")
    item_dims = (item["width_cm"], item["depth_cm"], item["height_cm"])
    containers = get_sorted_containers(zone_collection, preferred_zone)
    failure_reasons = []

    for container in containers:
        container_id = container["container_id"]
        zone = container["zone"]
        max_dims = (container["width_cm"], container["depth_cm"], container["height_cm"])

        if any(i > c for i, c in zip(item_dims, max_dims)):
            failure_reasons.append(f"Container {container_id} too small (max: {max_dims}, item: {item_dims})")
            continue

        used_space = [
            (tuple(entry["startCoordinates"]), tuple(entry["endCoordinates"]))
            for entry in cargo_collection.find({"container_id": container_id})
            if "startCoordinates" in entry and "endCoordinates" in entry
        ]

        start, end = find_empty_space(container, item_dims, used_space)

        if start is not None and end is not None:

            item["container_id"] = container_id
            item["zone"] = zone
            item["startCoordinates"] = start
            item["endCoordinates"] = end
            item["placed_at"] = datetime.utcnow()
            item["usage_remaining"] = item["usage_limit"]
            cargo_collection.insert_one(item)

            print(f"Item {item['item_id']} successfully placed in container {container_id}.")
            return {
                "zone": zone,
                "container_id": container_id,
                "start_coordinates": start,
                "end_coordinates": end
            }
        else:
            failure_reasons.append(f"Container {container_id} has no empty space for item.")

    print(f"Item {item['item_id']} placement failed. Reasons:")
    for reason in failure_reasons:
        print(" -", reason)

    raise Exception(f"Failed to place item '{item['item_id']}' in any container.")
