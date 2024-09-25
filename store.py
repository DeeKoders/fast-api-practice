from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

# Define the item model
class Item(BaseModel):
    id: int
    name: str
    price: float

# File path for the store data
STORE_FILE = 'store.json'

# Function to read items from the store file
def read_store():
    if not os.path.exists(STORE_FILE):
        return []
    with open(STORE_FILE, 'r') as file:
        return json.load(file)

# Function to write items to the store file
def write_store(items):
    with open(STORE_FILE, 'w') as file:
        json.dump(items, file, indent=4)

# 1. Get all items from the store
@app.get("/items", response_model=List[Item])
def get_all_items():
    return read_store()

# 2. Get a single item by id or name
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, ):
    items = read_store()
    if item_id is not None:
        item = items[item_id]
    else:
        item = None
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 3. Add items to the store
@app.post("/items", response_model=Item)
def add_item(item: Item):
    items = read_store()
    if any(existing_item["id"] == item.id for existing_item in items):
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    items.append(item.dict())
    write_store(items)
    return item

# 4. Delete an item from the store
@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int):
    items = read_store()
    items = [item for item in items if item["id"] != item_id]
    write_store(items)
    return {"detail": "Item deleted"}

# 5. Edit an existing item
@app.put("/items/{item_id}", response_model=Item)
def edit_item(item_id: int, updated_item: Item):
    items = read_store()
    for index, item in enumerate(items):
        if item["id"] == item_id:
            items[index] = updated_item.dict()
            write_store(items)
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")
