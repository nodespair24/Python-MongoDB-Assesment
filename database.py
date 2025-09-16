from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)

db = client["assessment_db"]
employees_collection = db["employees"]

# Ensure unique index on employee_id
employees_collection.create_index("employee_id", unique=True)