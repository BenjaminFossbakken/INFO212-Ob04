from flask import Flask, render_template, request, redirect, url_for, jsonify
from employee_blueprint import employee_bp
from car_blueprint import car_bp
from customer_blueprint import customer_bp
from db import session

###Efter at have givet den al min kode og hele set uppet, så har den ikke lavet css, kun lavet html for customer, og kun js for car.	
api = Flask(__name__)

# Registrer Blueprints
api.register_blueprint(employee_bp)
api.register_blueprint(car_bp)
api.register_blueprint(customer_bp)

@api.route("/emp_home")
def emp_home_page():
    return render_template("emp_home.html")

@api.route("/employees_page")
def employee_page():
    return render_template("employee.html")

# Rute til at vise Customer-siden
@api.route("/customers")
def customer_page():
    return render_template("customer.html")

# Rute til at vise Car-siden
@api.route("/cars")
def car_page():
    return render_template("car.html")

@api.route("/operations")
def operations_page():
    return render_template("operations.html")

@api.route("/")
def index():
    return render_template("index.html")

# Customer login page
@api.route("/customer_login")
def customer_login_page():
    return render_template("customer_login.html")

# Customer registration page
@api.route("/customer_register")
def customer_register_page():
    return render_template("customer_register.html")

@api.route("/customer_page")
def customer_dashboard():
    return render_template("customer_page.html")



###ORDER-CAR END-POINT###
@api.route("/order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def order_car(customer_id, car_id):
    #Checks if the id's exist
    existence_query = """
    MATCH (cust:Customer {ID: $customer_id}), (car:Car {ID: $car_id})
    RETURN cust, car
    """
    existence_result = session.run(existence_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not existence_result:
        return f"Either customer with ID={customer_id} or car with ID={car_id} does not exist."
    
    #Checks if the customer has booked a car already
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car)
    RETURN car.ID AS car_id
    """
    booked_car = session.run(check_booking_query, parameters={"customer_id": customer_id}).single()

    #If yes, then they can not book again the receive an error message
    if booked_car:
        return f"Customer with ID={customer_id} already has a booking for car with ID={booked_car['car_id']}"

    #Then checks the status of the car, if the statis is not 'available', they receive error message
    check_car_status_query = """
    MATCH (car:Car {ID: $car_id})
    RETURN car.STATUS AS status
    """
    car_status = session.run(check_car_status_query, parameters={"car_id": car_id}).single()

    if car_status and car_status["status"] != "available":
        return f"Car with ID={car_id} is currently not available for booking"

    #Creates a booking relationship and updates the car's status to 'booked'
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
        return str(e)

###CANCEL-ORDER END-POINT###
@api.route("/cancel-order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def cancel_order_car(customer_id, car_id):
    #Checks relationship between customer node and car node
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car {ID: $car_id})
    RETURN car.ID AS car_id
    """
    booking = session.run(check_booking_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not booking:
        return f"Customer with ID={customer_id} does not have a booking for Car with ID={car_id}"

    #If the relationship is 'booked', DELETE it and set the car's status back to 'available'
    cancel_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[r:BOOKED]->(car:Car {ID: $car_id})
    DELETE r
    SET car.STATUS = 'available'
    RETURN car
    """
    try:
        session.run(cancel_booking_query, parameters={"customer_id": customer_id, "car_id": car_id})
        return f"Booking for car with ID={car_id} by customer with ID={customer_id} has been cancelled."
    except Exception as e:
        return str(e)

###RENT END-POINT###
@api.route("/rent-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def rent_car(customer_id, car_id):
    #Checks relationship between ids
    check_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car {ID: $car_id})
    WHERE car.STATUS = 'booked'
    RETURN car.ID AS car_id
    """
    booking = session.run(check_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()
    #Error message
    if not booking:
        return f"Customer with ID={customer_id} does not have a booking for car with ID={car_id} or the car is not in 'booked' status."
    
    #Deletes 'booked' relationship and creates a 'rented' relationship
    rent_query = """
    MATCH (cust:Customer {ID: $customer_id})-[r:BOOKED]->(car:Car {ID: $car_id})
    DELETE r
    CREATE (cust)-[:RENTED]->(car)
    SET car.STATUS = 'rented'
    RETURN car
    """
    try:
        session.run(rent_query, parameters={"customer_id": customer_id, "car_id": car_id})
        return f"Car with ID={car_id} has been rented by customer with ID={customer_id}. The car status is now 'rented'."
    except Exception as e:
        return str(e)
    
###RETURN END-POINT###
@api.route("/return-car/<int:customer_id>&<int:car_id>&<string:status>", methods=["POST"])
def return_car(customer_id, car_id, status):
    #Checks if there is a 'rented' relationship between the two chosen ids
    check_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:RENTED]->(car:Car {ID: $car_id})
    RETURN car.ID AS car_id
    """
    rented_car = session.run(check_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not rented_car:
        return f"Customer with ID={customer_id} has not rented car with ID={car_id}."

    #Sets status back to available if the car is not damaged
    final_status = "available" if status == "ok" else "damaged"

    #Depending on whether the car is ok or damaged, the status is set to either available or damaged
    return_query = """
    MATCH (cust:Customer {ID: $customer_id})-[r:RENTED]->(car:Car {ID: $car_id})
    DELETE r
    SET car.STATUS = $final_status
    RETURN car
    """
    try:
        session.run(return_query, parameters={"customer_id": customer_id, "car_id": car_id, "final_status": final_status})
        return f"Car with ID={car_id} returned by Customer with ID={customer_id}. The car status is now '{final_status}'."
    except Exception as e:
        return str(e)
    
@api.route("/customer_login", methods=["POST"])
def customer_login():
    data = request.json
    username = data["username"]
    password = data["password"]

    query = """
    MATCH (cust:Customer {username: $username, password: $password})
    RETURN cust
    """
    result = session.run(query, parameters={"username": username, "password": password}).single()
    if result:
        # Omdirigerer kunden til den opdaterede funktion
        return redirect(url_for("customer_dashboard"))
    else:
        return "Login failed: Invalid username or password.", 400



# Customer registration endpoint
@api.route("/customer_register", methods=["POST"])
def customer_register():
    data = request.json
    name = data["name"]
    username = data["username"]
    password = data["password"]
    address = data["address"]

    # Find the next available customer ID, starting from 200
    query = "MATCH (c:Customer) RETURN MAX(c.ID) AS max_id"
    max_id_result = session.run(query).single()
    customer_id = max_id_result["max_id"] + 1 if max_id_result["max_id"] else 200

    # Create the new customer node
    create_query = """
    CREATE (cust:Customer {ID: $id, name: $name, username: $username, password: $password, address: $address})
    RETURN cust
    """
    session.run(create_query, parameters={
        "id": customer_id,
        "name": name,
        "username": username,
        "password": password,
        "address": address
    })
    return f"Customer {name} created successfully with ID={customer_id}."

@api.route("/find_available_cars")
def find_available_cars():
    location = request.args.get("location")
    date = request.args.get("date")  # This can be used for additional filtering if needed

    query = """
    MATCH (c:Car {LOCATION: $location, STATUS: 'available'})
    RETURN c.MAKE AS make, c.MODEL AS model, c.YEAR AS year, c.STATUS AS status
    """
    results = session.run(query, parameters={"location": location})
    
    cars = [{"make": record["make"], "model": record["model"], "year": record["year"], "status": record["status"]} 
            for record in results]
    
    return jsonify(cars)


if __name__=="__main__":
    api.run(port=5050)