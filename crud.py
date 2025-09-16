from fastapi import HTTPException
from bson import ObjectId
from database import employees_collection
from models import Employee, UpdateEmployee

# ------------------------
# Helper serializer
# ------------------------
def employee_serializer(emp) -> dict:
    return {
        "employee_id": emp["employee_id"],
        "name": emp["name"],
        "department": emp["department"],
        "salary": emp["salary"],
        "joining_date": str(emp["joining_date"]),  # ensure date is string
        "skills": emp["skills"],
    }

# ------------------------
# CRUD Operations
# ------------------------

#  Create Employee
def create_employee(emp: Employee):
    exists = employees_collection.find_one({"employee_id": emp.employee_id})
    if exists:
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    employees_collection.insert_one(emp.dict())
    return {"message": "Employee created successfully", "employee": emp.dict()}


#  Get Employee by ID
def get_employee(employee_id: str):
    employee = employees_collection.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_serializer(employee)


#  Update Employee (Partial Update)
def update_employee(employee_id: str, emp: UpdateEmployee):
    update_data = {k: v for k, v in emp.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = employees_collection.update_one(
        {"employee_id": employee_id}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    updated = employees_collection.find_one({"employee_id": employee_id})
    return {"message": "Employee updated successfully", "employee": employee_serializer(updated)}


#  Delete Employee
def delete_employee(employee_id: str):
    result = employees_collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


# ------------------------
# Queries & Aggregations
# ------------------------

# List Employees by Department (with pagination & sorted by joining_date)
def list_employees(department: str = None, page: int = 1, limit: int = 5):
    query = {"department": department} if department else {}
    skip = (page - 1) * limit

    employees = (
        employees_collection.find(query)
        .sort("joining_date", -1)
        .skip(skip)
        .limit(limit)
    )

    return [employee_serializer(emp) for emp in employees]


# Average Salary by Department
def avg_salary():
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "avg_salary": 1, "_id": 0}}
    ]
    result = employees_collection.aggregate(pipeline)
    return [r for r in result]


#  Search Employees by Skill
def search_employees(skill: str):
    employees = employees_collection.find({"skills": skill})
    return [employee_serializer(emp) for emp in employees]
