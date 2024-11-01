from neo4j import GraphDatabase
import csv

# Load credentials
with open("cred.txt") as f1:
    data = csv.reader(f1, delimiter=",")
    for row in data:
        username = row[0]
        pwd = row[1]
        uri = row[2]

# Establish Neo4j driver and session
driver = GraphDatabase.driver(uri=uri, auth=(username, pwd))
session = driver.session()