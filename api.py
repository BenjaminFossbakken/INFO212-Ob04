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
    DETACH DELETE e
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
@api.route("/car/create/<string:make>&<string:model>&<int:year>&<string:location>&<string:status>&<int:id>", methods=["POST"])
def create_car(make, model, year, location, status, id):
    q1 = """
    CREATE (c:Car {MAKE: $make, MODEL: $model, YEAR: $year, LOCATION: $location, STATUS: $status, ID: $id})
    """
    map = {"make": make, "model": model, "year": year, "location": location, "status": status, "id": id}
    try:
        session.run(q1, parameters=map)
        return f"Car created with Make={make}, Model={model}, Year={year}, Location={location}, Status={status}, ID={id}"
    except Exception as e:
        return str(e)
    
#READ
@api.route("/cars/", methods=["GET"])
def display_cars():
    q1="""
    MATCH (c:Car) RETURN c.MAKE AS make, c.MODEL AS model, c.YEAR AS year, c.LOCATION as location, c.STATUS as status, c.ID as id
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))


@api.route("/car/update/<int:id>", methods=["POST"])
def update_car(id):
    make = request.json.get("make")
    model = request.json.get("model")
    year = request.json.get("year")
    location = request.json.get("location")
    status = request.json.get("status")

    q1 = """
    MATCH (c:Car {ID: $id})
    SET c.MAKE = $make, c.MODEL = $model, c.YEAR = $year, c.LOCATION = $location, c.STATUS = $status
    RETURN c
    """

    map = {"id": id,"make": make, "model": model, "year": year, "location": location, "status": status}
    try:
        result = session.run(q1, parameters=map)
        if result.single():
            return f"Car with ID={id} updated successfully"
        else:
            return f"No Car found with ID={id}"
    except Exception as e:
        return str(e)
    
@api.route("/car/delete/<int:id>", methods=["DELETE"])
def delete_car(id):
    query = """
    MATCH (c:Car {ID: $id})
    DETACH DELETE c
    """
    try:
        result = session.run(query, parameters={"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return f"Car with ID={id} deleted successfully"
        else:
            return f"No Car found with ID={id}"
    except Exception as e:
        return str(e)


# Customer CRUD
@api.route("/customer/create/<string:name>&<int:age>&<string:address>&<int:id>", methods=["POST"])
def create_customer(name, age, address, id):
    q1 = """
    CREATE (cust:Customer {NAME: $name, AGE: $age, ADDRESS: $address, ID: $id})
    """
    map = {"name": name, "age": age, "address": address, "id": id}
    try:
        session.run(q1, parameters=map)
        return f"Customer created with Name={name}, Age={age}, Address={address}, ID={id}"
    except Exception as e:
        return str(e)

@api.route("/customers/", methods=["GET"])
def display_customers():
    q1="""
    MATCH (cust:Customer) RETURN cust.NAME AS name, cust.AGE AS age, cust.ADDRESS AS address, cust.ID AS id
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))


@api.route("/customer/update/<int:id>", methods=["POST"])
def update_customer(id):
    name = request.json.get("name")
    address = request.json.get("address")
    age = request.json.get("age")

    q1 = """
    MATCH (cust:Customer {ID: $id})
    SET cust.NAME = $name, cust.ADDRESS = $address, cust.age = $age
    RETURN cust
    """
    map = {"name": name, "age": age, "address": address, "id": id}
    try:
        result = session.run(q1, parameters=map)
        if result.single():
            return f"Customer with ID={id} updated successfully"
        else:
            return f"No Customer found with ID={id}"
    except Exception as e:
        return str(e)

@api.route("/customer/delete/<int:id>", methods=["DELETE"])
def delete_customer(id):
    query ="""
    MATCH (cust:Customer {ID: $id})
    DETACH DELETE cust
"""
    try:
        result = session.run(query, parameters={"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return f"Customer with ID={id} deleted successfully"
        else:
            return f"No Customer found with ID={id}"
    except Exception as e:
        return str(e)









@api.route("/order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def order_car(customer_id, car_id):
    check_car_query = """
    MATCH (c:Car {ID: $car_id})
    RETURN c.STATUS AS status
    """
    car_status = session.run(check_car_query, parameters={"car_id": car_id}).single()

    if car_status and car_status["status"] in ["available", "booked"]:
        order_query = """
        MATCH (cust:Customer {ID: $customer_id}), (c:Car {ID: $car_id})
        CREATE (cust)-[:RENTED]->(c)
        SET c.STATUS = 'rented'
        RETURN c
        """
        try:
            session.run(order_query, parameters={"customer_id": customer_id, "car_id": car_id})
            return f"Customer {customer_id} successfully rented Car {car_id}"
        except Exception as e:
            return str(e)
    elif car_status:
        return f"Car {car_id} is not available for rent."
    else:
        return f"Car {car_id} not found."



if __name__=="__main__":
    api.run(port=5050)