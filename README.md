### Car-rental setup
In cred.txt there is the credentials for the server with the delimeter ','
If the server for some reason is not running, these are given when starting a new server.

For texting functionality:
query, CRUD for employee, customer, and car.
To check the database is working as intended, I would recommend creating car, customer and employee.
For your convenience, I have put examples of the other CRUD commands in the pdf file with pictures.

### Start up:
1. Open new terminal.
2. Write 'python api.py'
3. The link provided should say "* Running on http://127.0.0.1:5050".

### Open postman:
1. In the url form put: http://127.0.0.1:5050.
2. From the code it should be clear which method is used in each function, i.e "GET", "POST", "DELETE" and so forth.
3. Choose the desired method.
4. The code gives a route to check the functionality, example: "/order-car/<int:customer_id>&<int:car_id>".
5. As a full example of a query for creating an employee would look like: http://127.0.0.1:5050/employee/create/Benjamin&100&Møllendal 4&Bergen.
6. Other example queries are provided in the pdf.


