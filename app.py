from flask import Flask, jsonify, request
from neo4j import GraphDatabase
import uuid

app = Flask(__name__)

# Connect to database
uri = "*******"
username = "*******"
password = "*******"
driver = GraphDatabase.driver(uri, auth=(username, password))



# Create a car with unique ID
@app.route('/cars', methods=['POST'])
def create_car():
    data = request.json
    car_id = str(uuid.uuid4())  # Unique ID for each car
    make = data['make']
    model = data['model']
    year = data['year']
    location = data['location']
    status = data['status']
    
    with driver.session() as session:
        session.run(
            "CREATE (c:Car {car_id: $car_id, make: $make, model: $model, year: $year, location: $location, status: $status})",
            car_id=car_id, make=make, model=model, year=year, location=location, status=status
        )
    
    return jsonify({"message": "Car created successfully", "car_id": car_id}), 201

# Read all cars
@app.route('/cars', methods=['GET'])
def get_cars():
    with driver.session() as session:
        result = session.run("MATCH (c:Car) RETURN c")
        cars = [{"car_id": record['c']['car_id'], "make": record['c']['make'], "model": record['c']['model'],
                 "year": record['c']['year'], "location": record['c']['location'], "status": record['c']['status']} 
                for record in result]
    return jsonify(cars)

# Update a car
@app.route('/cars/<string:car_id>', methods=['PUT'])
def update_car(car_id):
    data = request.json
    with driver.session() as session:
        session.run(
            "MATCH (c:Car {car_id: $car_id}) SET c.make = $make, c.model = $model, c.year = $year, "
            "c.location = $location, c.status = $status",
            car_id=car_id, make=data['make'], model=data['model'], year=data['year'], 
            location=data['location'], status=data['status']
        )
    return jsonify({"message": "Car updated successfully"})

# Delete a car
@app.route('/cars/<string:car_id>', methods=['DELETE'])
def delete_car(car_id):
    with driver.session() as session:
        session.run("MATCH (c:Car {car_id: $car_id}) DELETE c", car_id=car_id)
    return jsonify({"message": "Car deleted successfully"}), 200




# Create a customer with unique ID
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    customer_id = str(uuid.uuid4())  # Unique ID for each customer
    name = data['name']
    age = data['age']
    address = data['address']
    
    with driver.session() as session:
        session.run(
            "CREATE (c:Customer {customer_id: $customer_id, name: $name, age: $age, address: $address})",
            customer_id=customer_id, name=name, age=age, address=address
        )
    
    return jsonify({"message": "Customer created successfully", "customer_id": customer_id}), 201

# Read all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    with driver.session() as session:
        result = session.run("MATCH (c:Customer) RETURN c")
        customers = [{"customer_id": record['c']['customer_id'], "name": record['c']['name'], 
                      "age": record['c']['age'], "address": record['c']['address']} 
                     for record in result]
    return jsonify(customers)

# Update a customer
@app.route('/customers/<string:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    with driver.session() as session:
        session.run(
            "MATCH (c:Customer {customer_id: $customer_id}) SET c.name = $name, c.age = $age, c.address = $address",
            customer_id=customer_id, name=data['name'], age=data['age'], address=data['address']
        )
    return jsonify({"message": "Customer updated successfully"})

# Delete a customer
@app.route('/customers/<string:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    with driver.session() as session:
        session.run("MATCH (c:Customer {customer_id: $customer_id}) DELETE c", customer_id=customer_id)
    return jsonify({"message": "Customer deleted successfully"}), 200




# Create an employee with unique ID
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    employee_id = str(uuid.uuid4())  # Unique ID for each employee
    name = data['name']
    address = data['address']
    branch = data['branch']
    
    with driver.session() as session:
        session.run(
            "CREATE (e:Employee {employee_id: $employee_id, name: $name, address: $address, branch: $branch})",
            employee_id=employee_id, name=name, address=address, branch=branch
        )
    
    return jsonify({"message": "Employee created successfully", "employee_id": employee_id}), 201

# Read all employees
@app.route('/employees', methods=['GET'])
def get_employees():
    with driver.session() as session:
        result = session.run("MATCH (e:Employee) RETURN e")
        employees = [{"employee_id": record['e']['employee_id'], "name": record['e']['name'], 
                      "address": record['e']['address'], "branch": record['e']['branch']} 
                     for record in result]
    return jsonify(employees)

# Update an employee
@app.route('/employees/<string:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json
    with driver.session() as session:
        session.run(
            "MATCH (e:Employee {employee_id: $employee_id}) SET e.name = $name, e.address = $address, e.branch = $branch",
            employee_id=employee_id, name=data['name'], address=data['address'], branch=data['branch']
        )
    return jsonify({"message": "Employee updated successfully"})

# Delete an employee
@app.route('/employees/<string:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    with driver.session() as session:
        session.run("MATCH (e:Employee {employee_id: $employee_id}) DELETE e", employee_id=employee_id)
    return jsonify({"message": "Employee deleted successfully"}), 200



# Ordering a car (book a car)
@app.route('/order-car', methods=['POST'])
def order_car():
    data = request.json
    customer_id = data['customer_id']
    car_id = data['car_id']
    
    with driver.session() as session:
        # Check if the customer has already booked a car
        result = session.run("MATCH (c:Customer {customer_id: $customer_id})-[:BOOKED]->(car:Car) RETURN car", customer_id=customer_id)
        if result.single():
            return jsonify({"message": "Customer has already booked another car"}), 400
        
        # Check if the car is available
        result = session.run("MATCH (car:Car {car_id: $car_id, status: 'available'}) RETURN car", car_id=car_id)
        if not result.single():
            return jsonify({"message": "Car is not available"}), 400
        
        # Book the car for the customer
        session.run(
            "MATCH (c:Customer {customer_id: $customer_id}), (car:Car {car_id: $car_id}) "
            "SET car.status = 'booked' "
            "CREATE (c)-[:BOOKED]->(car)",
            customer_id=customer_id, car_id=car_id
        )
    
    return jsonify({"message": "Car booked successfully"}), 200

# Cancel a car order
@app.route('/cancel-order-car', methods=['POST'])
def cancel_order_car():
    data = request.json
    customer_id = data['customer_id']
    car_id = data['car_id']
    
    with driver.session() as session:
        # Check if the customer has booked the car
        result = session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[:BOOKED]->(car:Car {car_id: $car_id}) RETURN car",
            customer_id=customer_id, car_id=car_id
        )
        if not result.single():
            return jsonify({"message": "No booking found for this car"}), 400
        
        # Cancel the booking
        session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[r:BOOKED]->(car:Car {car_id: $car_id}) "
            "DELETE r "
            "SET car.status = 'available'",
            customer_id=customer_id, car_id=car_id
        )
    
    return jsonify({"message": "Booking canceled successfully"}), 200

# Rent a car
@app.route('/rent-car', methods=['POST'])
def rent_car():
    data = request.json
    customer_id = data['customer_id']
    car_id = data['car_id']
    
    with driver.session() as session:
        # Check if the customer has booked the car
        result = session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[:BOOKED]->(car:Car {car_id: $car_id}) RETURN car",
            customer_id=customer_id, car_id=car_id
        )
        if not result.single():
            return jsonify({"message": "Customer has not booked this car"}), 400
        
        # Rent the car
        session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[r:BOOKED]->(car:Car {car_id: $car_id}) "
            "DELETE r "
            "SET car.status = 'rented' "
            "CREATE (c)-[:RENTED]->(car)",
            customer_id=customer_id, car_id=car_id
        )
    
    return jsonify({"message": "Car rented successfully"}), 200

# Return a car
@app.route('/return-car', methods=['POST'])
def return_car():
    data = request.json
    customer_id = data['customer_id']
    car_id = data['car_id']
    status = data['status']  # Can be 'available' or 'damaged'
    
    with driver.session() as session:
        # Check if the customer has rented the car
        result = session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[:RENTED]->(car:Car {car_id: $car_id}) RETURN car",
            customer_id=customer_id, car_id=car_id
        )
        if not result.single():
            return jsonify({"message": "Car not rented by this customer"}), 400
        
        # Return the car and update its status
        session.run(
            "MATCH (c:Customer {customer_id: $customer_id})-[r:RENTED]->(car:Car {car_id: $car_id}) "
            "DELETE r "
            "SET car.status = $status",
            customer_id=customer_id, car_id=car_id, status=status
        )
    
    return jsonify({"message": "Car returned successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
