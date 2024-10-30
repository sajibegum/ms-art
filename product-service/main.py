from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId

# App setup
app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://mongo:27017")
db = client["product_db"]
product_collection = db["products"]


LOGGING_SERVICE_URL = "http://logging-service:8002/log"  # Internal Docker network URL

# Pydantic models
class Product(BaseModel):
    name: str
    description: str
    price: float
    stock: int


def log_event(message):
    try:
        requests.post(LOGGING_SERVICE_URL, json={"message": message})
    except requests.exceptions.RequestException as e:
        print(f"Failed to log event: {e}")

# Example usage in /products endpoint
@app.post("/products")
async def create_product(product: Product):
    product_id = product_collection.insert_one(product.dict()).inserted_id
    log_event(f"Product created: {product.name} with ID {product_id}")
    return {"id": str(product_id)}

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = product_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: Product):
    result = product_collection.update_one({"_id": ObjectId(product_id)}, {"$set": product.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product updated"}

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = product_collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product deleted"}
