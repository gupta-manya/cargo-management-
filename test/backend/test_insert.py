from datetime import datetime, timedelta
from configuration import cargo_collection, zone_collection

# Insert zones
zones_data = [
    {"zone_id": "Z1", "category": "vegetables", "capacity": 10, "used": 0},
    {"zone_id": "Z2", "category": "fruits", "capacity": 8, "used": 0},
    {"zone_id": "Z3", "category": "dairy", "capacity": 5, "used": 0},
    {"zone_id": "Z4", "category": "grains", "capacity": 12, "used": 0}
]

zone_collection.insert_many(zones_data)
print("✅ Zones inserted successfully.")

# Insert items
items_data = [
    {
        "name": "Tomato",
        "type": "vegetables",
        "expiry_date": (datetime.today() + timedelta(days=5)).isoformat(),
        "zone": "Z1"
    },
    {
        "name": "Apple",
        "type": "fruits",
        "expiry_date": (datetime.today() + timedelta(days=7)).isoformat(),
        "zone": "Z2"
    },
    {
        "name": "Milk",
        "type": "dairy",
        "expiry_date": (datetime.today() + timedelta(days=2)).isoformat(),
        "zone": "Z3"
    },
    {
        "name": "Rice",
        "type": "grains",
        "expiry_date": (datetime.today() + timedelta(days=30)).isoformat(),
        "zone": "Z4"
    }
]

cargo_collection.insert_many(items_data)
# Update zone usage counts
for item in items_data:
    zone_collection.update_one({"zone_id": item["zone"]}, {"$inc": {"used": 1}})

print("✅ Items inserted successfully.")
