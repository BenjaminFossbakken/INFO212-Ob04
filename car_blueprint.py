from flask import Blueprint, jsonify, request
from db import session

car_bp = Blueprint('car', __name__)


#CREATE
@car_bp.route("/car/create/<string:make>&<string:model>&<int:year>&<string:location>&<string:status>&<int:id>", methods=["POST"])
def create_car(make, model, year, location, status, id):
    check_id_query = """
    MATCH (c:Car {ID: $id})
    RETURN c.ID AS id
    """
    while session.run(check_id_query, parameters={"id": id}).single():
        id += 1 

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
@car_bp.route("/cars/", methods=["GET"])
def display_cars():
    q1="""
    MATCH (c:Car) RETURN c.MAKE AS make, c.MODEL AS model, c.YEAR AS year, c.LOCATION as location, c.STATUS as status, c.ID as id
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))

#UPDATE
@car_bp.route("/car/update/<int:id>", methods=["POST"])
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
    
@car_bp.route("/car/delete/<int:id>", methods=["DELETE"])
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