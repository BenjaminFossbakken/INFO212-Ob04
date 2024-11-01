from neo4j import GraphDatabase
import csv

#Loader cred.txt
with open("cred.txt") as f1:
    data = csv.reader(f1, delimiter=",")
    for row in data:
        username = row[0]
        pwd = row[1]
        uri = row[2]

#driver and session
driver = GraphDatabase.driver(uri=uri, auth=(username, pwd))
session = driver.session()
