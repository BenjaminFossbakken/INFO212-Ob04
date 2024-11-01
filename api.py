from flask import Flask
from employee_blueprint import employee_bp
from car_blueprint import car_bp
from customer_blueprint import customer_bp
from db import session

api=Flask(__name__)

api.register_blueprint(employee_bp)
api.register_blueprint(car_bp)
api.register_blueprint(customer_bp)

#Error 400 for bad request
#Error 500 for internal server error

###ORDER-CAR END-POINT###
@api.route("/order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def order_car(customer_id, car_id):
    #Tjekker først om id'erne eksisterer
    existence_query = """
    MATCH (cust:Customer {ID: $customer_id}), (car:Car {ID: $car_id})
    RETURN cust, car
    """
    existence_result = session.run(existence_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not existence_result:
        return f"Either customer with ID={customer_id} or car with ID={car_id} does not exist."
    
    #Tejkker om kunden har booket en bil i forvejen
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car)
    RETURN car.ID AS car_id
    """
    booked_car = session.run(check_booking_query, parameters={"customer_id": customer_id}).single()

    #Hvis ja, så kan de ikke booke igen og får fejlmelding
    if booked_car:
        return f"Customer with ID={customer_id} already has a booking for car with ID={booked_car['car_id']}"

    #Tjekker derefter om bilens status, hvis status ikke er = "available" -> fejlmelding
    check_car_status_query = """
    MATCH (car:Car {ID: $car_id})
    RETURN car.STATUS AS status
    """
    car_status = session.run(check_car_status_query, parameters={"car_id": car_id}).single()

    if car_status and car_status["status"] != "available":
        return f"Car with ID={car_id} is currently not available for booking"

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
        return str(e)

###CANCEL-ORDER END-POINT###
@api.route("/cancel-order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def cancel_order_car(customer_id, car_id):
    #Tjekker relationship mellem customer og bil
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car {ID: $car_id})
    RETURN car.ID AS car_id
    """
    booking = session.run(check_booking_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not booking:
        return f"Customer with ID={customer_id} does not have a booking for Car with ID={car_id}"

    #Hvis relationship er booked, DELETE r og set bilens status tilbage til 'available'
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
    #Tjekker relationship mellem ids
    check_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car {ID: $car_id})
    WHERE car.STATUS = 'booked'
    RETURN car.ID AS car_id
    """
    booking = session.run(check_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()
    #error message
    if not booking:
        return f"Customer with ID={customer_id} does not have a booking for car with ID={car_id} or the car is not in 'booked' status."
    
    #fjerner booked relationship og laver rented relationship
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
    #tjekker om der er et rented relationship
    check_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:RENTED]->(car:Car {ID: $car_id})
    RETURN car.ID AS car_id
    """
    rented_car = session.run(check_query, parameters={"customer_id": customer_id, "car_id": car_id}).single()

    if not rented_car:
        return f"Customer with ID={customer_id} has not rented car with ID={car_id}."

    #setter status tilbage til available hvis den bilen ikke er damaged
    final_status = "available" if status == "ok" else "damaged"

    #afhængigt af om den er ok eller damaged bliver den set til den status
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

if __name__=="__main__":
    api.run(port=5050)