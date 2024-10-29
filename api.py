from flask import Flask, jsonify, request, redirect, render_template
from neo4j import GraphDatabase
import csv

#establish the connection
with open("cred.txt") as f1:
    data=csv.reader(f1,delimiter=",")
    for row in data:
        username=row[0]
        pwd=row[1]
        uri=row[2]
print(username, pwd, uri)

driver=GraphDatabase.driver(uri=uri,auth=(username,pwd))
session=driver.session()

#CREATE
api=Flask(__name__)
@api.route("/employee/create/<string:name>&<int:id>&<string:address>&<string:branch>",methods=["POST"])
def create_node(name, id, address, branch):
    q1="""
    CREATE (e:Employee{NAME:$name, ID:$id, ADDRESS: $address, BRANCH: $branch})
    """
    map={"name": name, "id": id, "address": address, "branch": branch}
    try:
        session.run(q1, parameters=map)
        return (f"Employee node is created with employee name={name} and id={id}, Address={address}, Branch={branch}")
    except Exception as e:
        return (str(e))

#READ
@api.route("/employees/", methods=["GET"])
def display_node():
    q1="""
    MATCH (e:Employee) RETURN e.NAME AS name, e.ID AS id, e.ADDRESS AS address, e.BRANCH AS branch
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))

#UPDATE
#Eksempel på at update for nu, bruges i powershell
#Invoke-WebRequest -Uri "http://127.0.0.1:5050/update/100" -Method POST -Body '{"name": "Ben", "address": "test2", "branch": "test2"}' -ContentType "application/json"
@api.route("/employee/update/<int:id>", methods=["POST"])
def update_employee(id):
    name = request.json.get("name")
    address = request.json.get("address")
    branch = request.json.get("branch")

    q1 = """
    MATCH (e:Employee {ID: $id})
    SET e.NAME = $name, e.ADDRESS = $address, e.BRANCH = $branch
    RETURN e
    """

    map = {"id": id, "name": name, "address": address, "branch": branch}
    try:
        result = session.run(q1, parameters=map)
        if result.single():
            return f"Employee with ID={id} updated successfully"
        else:
            return f"No Employee found with ID={id}"
    except Exception as e:
        return str(e)

#DELETE
#Eksempel på delete for nu i powershell, senere postman
#Invoke-WebRequest -Uri "http://127.0.0.1:5050/delete/102" -Method DELETE
@api.route("/employee/delete/<int:id>", methods=["DELETE"])
def delete_employee(id):
    query ="""
    MATCH (e:Employee {ID: $id})
    DELETE e
"""
    try:
        result = session.run(query, parameters={"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return f"Employee with ID={id} deleted successfully"
        else:
            return f"No Employee found with ID={id}"
    except Exception as e:
        return str(e)
    

# Car CRUD
@api.route("/car/create/<string:make>&<string:model>&<int:year>&<string:location>&<string:status>", methods=["POST"])
def create_car(make, model, year, location, status):
    q1 = """
    CREATE (c:Car {MAKE: $make, MODEL: $model, YEAR: $year, LOCATION: $location, STATUS: $status})
    """
    map = {"make": make, "model": model, "year": year, "location": location, "status": status}
    try:
        session.run(q1, parameters=map)
        return f"Car created with Make={make}, Model={model}, Year={year}, Location={location}, Status={status}"
    except Exception as e:
        return str(e)
    

# Customer CRUD
@api.route("/customer/create/<string:name>&<int:age>&<string:address>", methods=["POST"])
def create_customer(name, age, address):
    query = """
    CREATE (cust:Customer {NAME: $name, AGE: $age, ADDRESS: $address})
    """
    parameters = {"name": name, "age": age, "address": address}
    try:
        session.run(query, parameters=parameters)
        return f"Customer created with Name={name}, Age={age}, Address={address}"
    except Exception as e:
        return str(e)


if __name__=="__main__":
    api.run(port=5050)