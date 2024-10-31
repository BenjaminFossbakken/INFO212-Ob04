from flask import Flask, jsonify, request, redirect, render_template
from neo4j import GraphDatabase
from employee_blueprint import employee_bp
from db import session
import csv

#CREATE
api=Flask(__name__)

# Register Employee Blueprint
api.register_blueprint(employee_bp)

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
    #Tejkker om kunden har booket en bil i forvejen
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car)
    RETURN car.ID AS car_id
    """
    booked_car = session.run(check_booking_query, parameters={"customer_id": customer_id}).single()

    #Hvis ja, så kan de ikke booke igen og får fejlmelding
    if booked_car:
        return f"Customer with ID={customer_id} already has a booking for Car with ID={booked_car['car_id']}", 400

    #Tjekker derefter om bilens status, hvis status ikke er = "available" -> fejlmelding
    check_car_status_query = """
    MATCH (car:Car {ID: $car_id})
    RETURN car.STATUS AS status
    """
    car_status = session.run(check_car_status_query, parameters={"car_id": car_id}).single()

    if car_status and car_status["status"] != "available":
        return f"Car with ID={car_id} is currently not available for booking", 400

    #Laver booking relationship og opdaterer bilens status til 'booked'
    order_query = """
    MATCH (cust:Customer {ID: $customer_id}), (car:Car {ID: $car_id})
    CREATE (cust)-[:BOOKED]->(car)
    SET car.STATUS = 'booked'
    RETURN car
    """
    try:
        session.run(order_query, parameters={"customer_id": customer_id, "car_id": car_id})
        return f"Car with ID={car_id} successfully booked for Customer with ID={customer_id}"
    except Exception as e:
        return str(e), 500


@api.route("/cancel-order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def cancel_order_car(customer_id, car_id):
    #Tjekker relationship mellem customer og bil
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car {ID: $car_id})
    RETURN car.ID AS car_id
    """
    booking = session.run(check_booking_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not booking:
        return f"Customer with ID={customer_id} does not have a booking for Car with ID={car_id}", 400

    #Hvis relationship er booked, DELETE r og set bilens status tilbage til 'available'
    cancel_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[r:BOOKED]->(car:Car {ID: $car_id})
    DELETE r
    SET car.STATUS = 'available'
    RETURN car
    """
    try:
        session.run(cancel_booking_query, parameters={"customer_id": customer_id, "car_id": car_id})
        return f"Booking for Car with ID={car_id} by Customer with ID={customer_id} has been cancelled. The car is now available."
    except Exception as e:
        return str(e), 500
    



if __name__=="__main__":
    api.run(port=5050)