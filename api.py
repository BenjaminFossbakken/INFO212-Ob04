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

api=Flask(__name__)
@api.route("/create/<string:name>&<int:id>",methods=["GET", "POST"])
def create_node(name, id):
    q1="""
    create (n:Employee{NAME:$name, ID:$id})
    """
    map={"name": name, "id": id}
    try:
        session.run(q1, parameters=map)
        return (f"employee node is created with employee name={name} and id={id}")
    except Exception as e:
        return (str(e))


if __name__=="__main__":
    api.run(port=5050)