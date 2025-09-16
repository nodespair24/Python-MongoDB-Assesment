from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

import crud
from models import Employee, UpdateEmployee
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="Employee Management API")

# -------------------------
# Auth Route
# -------------------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}

# -------------------------
# CRUD Routes
# -------------------------
@app.post("/employees")
def create_employee(emp: Employee, user: str = Depends(get_current_user)):
    return crud.create_employee(emp)

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str):
    return crud.get_employee(employee_id)

@app.put("/employees/{employee_id}")
def update_employee(employee_id: str, emp: UpdateEmployee, user: str = Depends(get_current_user)):
    return crud.update_employee(employee_id, emp)

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, user: str = Depends(get_current_user)):
    return crud.delete_employee(employee_id)

# -------------------------
# Querying & Aggregation
# -------------------------
@app.get("/employees")
def list_employees(department: str = None, page: int = 1, limit: int = 5):
    return crud.list_employees(department, page, limit)

@app.get("/employees/avg-salary")
def average_salary_by_department():
    return crud.avg_salary()

@app.get("/employees/search")
def search_employees_by_skill(skill: str = Query(...)):
    return crud.search_employees(skill)
