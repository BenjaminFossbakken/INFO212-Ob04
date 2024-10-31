from flask import Flask, jsonify, request, redirect, render_template
from employee_blueprint import employee_bp
from car_blueprint import car_bp
from customer_blueprint import customer_bp
from db import session

api=Flask(__name__)

api.register_blueprint(employee_bp)
api.register_blueprint(car_bp)
api.register_blueprint(customer_bp)

###ORDER-CAR END-POINT###
@api.route("/order-car/<int:customer_id>&<int:car_id>", methods=["POST"])
def order_car(customer_id, car_id):
    #Tejkker om kunden har booket en bil i forvejen
    check_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[:BOOKED]->(car:Car)
    RETURN car.ID AS car_id
    """
    booked_car = session.run(check_booking_query, parameters={"customer_id": customer_id}).single()

    #Hvis ja, så kan de ikke booke igen og får fejlmelding
    if booked_car:
        return f"Customer with ID={customer_id} already has a booking for Car with ID={booked_car['car_id']}", 400

    #Tjekker derefter om bilens status, hvis status ikke er = "available" -> fejlmelding
    check_car_status_query = """
    MATCH (car:Car {ID: $car_id})
    RETURN car.STATUS AS status
    """
    car_status = session.run(check_car_status_query, parameters={"car_id": car_id}).single()

    if car_status and car_status["status"] != "available":
        return f"Car with ID={car_id} is currently not available for booking", 400

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
        return str(e), 500

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
        return f"Customer with ID={customer_id} does not have a booking for Car with ID={car_id}", 400

    #Hvis relationship er booked, DELETE r og set bilens status tilbage til 'available'
    cancel_booking_query = """
    MATCH (cust:Customer {ID: $customer_id})-[r:BOOKED]->(car:Car {ID: $car_id})
    DELETE r
    SET car.STATUS = 'available'
    RETURN car
    """
    try:
        session.run(cancel_booking_query, parameters={"customer_id": customer_id, "car_id": car_id})
        return f"Booking for Car with ID={car_id} by Customer with ID={customer_id} has been cancelled. The car is now available."
    except Exception as e:
        return str(e), 500


if __name__=="__main__":
    api.run(port=5050)