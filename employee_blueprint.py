from flask import Blueprint, jsonify, request
from db import session

employee_bp = Blueprint('employee', __name__)

#CREATE
@employee_bp.route("/employee/create/<string:name>&<int:id>&<string:address>&<string:branch>",methods=["POST"])
def create_employee(name, id, address, branch):
    #Checks id, if id exists +1 is added until id is unique
    check_id_query = """
    MATCH (e:Employee {ID: $id})
    RETURN e.ID AS id
    """
    while session.run(check_id_query, parameters={"id": id}).single():
        id += 1 
    #Creates node with given parameters
    q1="""
    CREATE (e:Employee{NAME:$name, ID:$id, ADDRESS: $address, BRANCH: $branch})
    """
    map={"name": name, "id": id, "address": address, "branch": branch}
    try:
        session.run(q1, parameters=map)
        return (f"Employee node is created with employee Name={name}, ID={id}, Address={address}, Branch={branch}")
    except Exception as e:
        return (str(e))

#READ
@employee_bp.route("/employees/", methods=["GET"])
def display_employee():
    q1="""
    MATCH (e:Employee) 
    RETURN e.NAME AS name, e.ID AS id, e.ADDRESS AS address, e.BRANCH AS branch
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))

#UPDATE
@employee_bp.route("/employee/update/<int:id>", methods=["POST"])
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
            return f"No employee found with ID={id}"
    except Exception as e:
        return str(e)

#DELETE
@employee_bp.route("/employee/delete/<int:id>", methods=["DELETE"])
def delete_employee(id):
    q1 ="""
    MATCH (e:Employee {ID: $id})
    DETACH DELETE e
"""
    try:
        result = session.run(q1, parameters={"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return f"Employee with ID={id} deleted successfully"
        else:
            return f"No employee found with ID={id}"
    except Exception as e:
        return str(e)
    