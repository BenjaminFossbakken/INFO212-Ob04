from flask import Blueprint, jsonify, request
from db import session

customer_bp = Blueprint('customer', __name__)

#CREATE
@customer_bp.route("/customer/create/<string:name>&<int:age>&<string:address>&<int:id>", methods=["POST"])
def create_customer(name, age, address, id):
    #Matches id, if id exists +1 is added until id is unique
    check_id_query = """
    MATCH (cust:Customer {ID: $id})
    RETURN cust.ID AS id
    """
    while session.run(check_id_query, parameters={"id": id}).single():
        id += 1
    #Creates node with given parameters
    q1 = """
    CREATE (cust:Customer {NAME: $name, AGE: $age, ADDRESS: $address, ID: $id})
    """
    map = {"name": name, "age": age, "address": address, "id": id}
    try:
        session.run(q1, parameters=map)
        return f"Customer created with Name={name}, Age={age}, Address={address}, ID={id}"
    except Exception as e:
        return str(e)
    
#READ
@customer_bp.route("/customers/", methods=["GET"])
def display_customers():
    #Match all employee nodes
    q1="""
    MATCH (cust:Customer) RETURN cust.NAME AS name, cust.AGE AS age, cust.ADDRESS AS address, cust.ID AS id
    """
    #Return data in json format
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))

#UPDATE
@customer_bp.route("/customer/update/<int:id>", methods=["POST"])
def update_customer(id):
    #Extract parameters
    name = request.json.get("name")
    address = request.json.get("address")
    age = request.json.get("age")

    #Match an employee by id and updates it
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
            return f"No customer found with ID={id}"
    except Exception as e:
        return str(e)

#DELETE
@customer_bp.route("/customer/delete/<int:id>", methods=["DELETE"])
def delete_customer(id):
    #Match id and detach, delete
    q1 ="""
    MATCH (cust:Customer {ID: $id})
    DETACH DELETE cust
    """
    try:
        result = session.run(q1, parameters={"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return f"Customer with ID={id} deleted successfully"
        else:
            return f"No customer found with ID={id}"
    except Exception as e:
        return str(e)

