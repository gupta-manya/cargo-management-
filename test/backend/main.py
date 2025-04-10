from fastapi import FastAPI, HTTPException , UploadFile, File
from configuration import cargo_collection, zone_collection,log_collection

from models import Item, Container,RetrievalLog
from algorithms.placement import store_item
from algorithms.retrieval import retrieve_item
from fastapi import Body
from algorithms.waste import identify_waste_items, plan_return_of_waste, complete_undocking

from algorithms.rearrangement import rebalance_zones
from io import StringIO
import pandas as pd
import csv
from fastapi.responses import JSONResponse
from datetime import datetime, date  
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
@app.get("/summary")
def get_summary():
    container_count = zone_collection.count_documents({})  
   
    return {"total_containers": container_count}

@app.get("/")
def root():
    return {"message": "Inventory Management System Running "}

@app.post("/items")
def insert_item(item: Item):
    # logic to insert item
    return {"message": " Item inserted", "item": item}

@app.post("/containers")
def insert_container(container: Container):
    # logic to insert container
    return {"message": " Container inserted", "container": container}

@app.post("/retrievals")
def insert_retrieval(log: RetrievalLog):
    # logic to insert log
    return {"message": " Retrieval logged", "log": log}
@app.get("/retrieve/{item_id}")
def retrieve_route(item_id: str):
    result = retrieve_item(item_id, cargo_collection, zone_collection)
    if "message" in result and result["message"] == "Item not found":
        raise HTTPException(status_code=404, detail="Item not found")
    return result
@app.post("/relog-placement")
def relog_placement(data: dict):
    item_id = data.get("item_id")
    new_container = data.get("new_container")
    astronaut = data.get("astronaut")
    timestamp = data.get("timestamp")

    cargo_collection.update_one(
        {"item_id": item_id},
        {"$set": {
            "container_id": new_container,
            "replaced_by": astronaut,
            "replaced_at": timestamp
        }}
    )

    return {"message": "Re-placement logged"}

@app.get("/api/waste/identify")
def get_waste_items():
    result = identify_waste_items(cargo_collection)
    return {"success": True, "wasteItems": result}


@app.post("/api/waste/return-plan")
def return_plan(payload: dict = Body(...)):
    try:
        undocking_container_id = payload.get("undockingContainerId")
        undocking_date_str = payload.get("undockingDate")
        max_weight = float(payload.get("maxWeight", 0))

        if not undocking_container_id or not undocking_date_str:
            raise HTTPException(status_code=400, detail="Missing required fields")

        undocking_date = datetime.fromisoformat(undocking_date_str)

        result = plan_return_of_waste(
            cargo_collection,
            undocking_container_id,
            undocking_date,
            max_weight
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/waste/complete-undocking")
def complete_undocking_route(payload: dict = Body(...)):
    try:
        undocking_container_id = payload.get("undockingContainerId")
        if not undocking_container_id:
            raise HTTPException(status_code=400, detail="Missing container ID")

        removed = complete_undocking(
            cargo_collection,
            undocking_container_id
        )
        return {"success": True, "itemsRemoved": removed}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/rebalance")
def rebalance_route():
    return rebalance_zones(cargo_collection, zone_collection)
print("FastAPI app is starting...")
@app.post("/place-item")
def place_item(item: dict):
    try:
        item["type"] = "item"  # ensure type for indexing
        result = store_item(item, cargo_collection, zone_collection)
        return result
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

#-------------------------------------------------

@app.post("/import-items/")
async def import_items(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))
    df = df.where(pd.notnull(df), None)  

    inserted_items = []

    for row in df.to_dict(orient="records"):
        try:
            record = {str(k): v for k, v in row.items()}
            expiry_raw = record.get("expiry_date")
            expiry_date = pd.to_datetime(expiry_raw) if expiry_raw else None


            item = Item(
                item_id=str(record.get("item_id")),
                name=record.get("name") or "",
                width_cm=int(float(record.get("width_cm", 0))),
                depth_cm=int(float(record.get("depth_cm", 0))),
                height_cm=int(float(record.get("height_cm", 0))),
                mass_kg=float(record.get("mass_kg", 0.0)),
                priority=int(record.get("priority", 0)),
                expiry_date=expiry_date,
                usage_limit=int(record.get("usage_limit") or record.get("usage_limi", 0)),
                preferred_zone=record.get("preferred_zone") or "default"
            )
            if isinstance(item.expiry_date, date) and not isinstance(item.expiry_date, datetime):
                item.expiry_date = datetime.combine(item.expiry_date, datetime.min.time())

            # Add the required 'type' field
            item_data = item.dict()
            item_data["type"] = "item"

            store_item(item_data, cargo_collection, zone_collection)
            inserted_items.append(item.item_id)

        except Exception as e:
            print(f"Error inserting item {record}: {e}")

    return {
        "inserted_items": inserted_items,
        "count": len(inserted_items)
    }


    
@app.post("/import-containers/")
async def import_containers(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode("utf-8")))
        df = df.where(pd.notnull(df), None)

        inserted_containers = []

        for row in df.to_dict(orient="records"):
            try:
                record = {str(k): v for k, v in row.items()}

                container = Container(
                    zone=record.get("zone") or "default",
                    container_id=str(record.get("container_id")),
                    
                    width_cm=int(float(record.get("width_cm", 0))),
                    depth_cm=int(float(record.get("depth_cm", 0))),
                    height_cm=int(float(record.get("height_cm", 0)))
                )

                # Convert to dict and add a "type" field if needed
                container_data = container.dict()
                container_data["type"] = "container"

                # Insert into your storage or database
                zone_collection.insert_one(container_data)


                inserted_containers.append(container.container_id)

            except Exception as e:
                print(f"Error inserting container {record}: {e}")

        return {
            "inserted_containers": inserted_containers,
            "count": len(inserted_containers)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")

@app.get("/logs")
def get_logs():
    logs = list(log_collection.find({}, {"_id": 0}))
    return{"logs":logs}