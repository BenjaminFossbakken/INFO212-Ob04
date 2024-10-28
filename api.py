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
@api.route("/create/<string:name>&<int:id>&<string:address>&<string:branch>",methods=["GET", "POST"])
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
@api.route("/employees", methods=["GET"])
def display_node():
    q1="""
    MATCH (e:Employee) RETURN e.NAME AS name, e.ID AS id, e.ADDRESS AS address, e.BRANCH AS branch
    """
    results=session.run(q1)
    data=results.data()
    return(jsonify(data))

#UPDATE

#DELETE

if __name__=="__main__":
    api.run(port=5050)