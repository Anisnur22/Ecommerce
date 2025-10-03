# app.py
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
import random
from flask import flash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tables.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'HomeCook'

db = SQLAlchemy(app)

class Vendor(db.Model):
    VendorID = db.Column(db.String(10), primary_key=True)
    RegistrationID = db.Column(db.String(10), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(200), nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(10), nullable=False)

class Customer(db.Model):
    CustomerID = db.Column(db.String(10), primary_key=True)
    RegistrationID = db.Column(db.String(10), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(200), nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(10), nullable=False)

class DeliveryPersonnel(db.Model):
    PersonnelID = db.Column(db.String(10), primary_key=True)
    RegistrationID = db.Column(db.String(10), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    LicenseNumber = db.Column(db.String(10), nullable=False)
    VehicleType = db.Column(db.String(40), nullable=False)
    Status = db.Column(db.String(10), nullable=False)

class SystemManager(db.Model):
    ManagerID = db.Column(db.String(10), primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(20), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)

class Order(db.Model):
    OrderID = db.Column(db.String(10), primary_key=True)
    VendorID = db.Column(db.String(10), nullable=False)
    CustomerID = db.Column(db.String(10), nullable=False)
    PersonnelID = db.Column(db.String(10), nullable=False)
    Date = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(10), nullable=False)

class Item(db.Model):
    ItemID = db.Column(db.String(10), primary_key=True)
    VendorID = db.Column(db.String(10), nullable=False)
    ItemName = db.Column(db.String(50), nullable=False)
    ItemPrice = db.Column(db.Double, nullable=False)
    Availability = db.Column(db.Boolean, nullable=False)

class OrderItem(db.Model):
    OrderID = db.Column(db.String(10), primary_key=True)
    Date = db.Column(db.String(20), nullable=False)
    ItemID = db.Column(db.String(10), nullable=False)
    VendorID = db.Column(db.String(10), nullable=False)
    ItemName = db.Column(db.String(50), nullable=False)
    Quantity = db.Column(db.Integer, nullable=True)
    UnitCost = db.Column(db.Float, nullable=True)
    Subtotal = db.Column(db.Float, nullable=True)

class CustomerApproval(db.Model):
    RegistrationID = db.Column(db.String(4), primary_key=True)
    CustomerID = db.Column(db.String(10), nullable=True)
    CustomerName = db.Column(db.String(50), nullable=False)
    CustomerEmail = db.Column(db.String(100), nullable=False)
    CustomerPassword = db.Column(db.String(20), nullable=False)
    ConfirmCustomerPassword = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(200), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)

class VendorApproval(db.Model):
    RegistrationID = db.Column(db.String(10), primary_key=True)
    VendorID = db.Column(db.String(10), nullable=False)
    VendorName = db.Column(db.String(50), nullable=False)
    VendorEmail = db.Column(db.String(100), nullable=False)
    PhoneNumber = db.Column(db.String(20), nullable=False)
    Address = db.Column(db.String(200), nullable=False)
    VendorPassword = db.Column(db.String(20), nullable=False)
    ConfirmVendorPassword = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id
    
# Main page
    
# Route for the main homepage
@app.route('/')
def main():
    return render_template('MainPage.html')

# Routes for login pages
@app.route('/customer-login')
def customer_login():
    return render_template('CustomerLogin.html')

@app.route('/vendor-login')
def vendor_login():
    return render_template('VendorLoginPage.html')

@app.route('/delivery-personnel-login')
def delivery_personnel_login():
    return render_template('DeliveryPersonnelLogin.html')

@app.route('/system-manager-login')
def system_manager_login():
    return render_template('SystemManagerLogin.html')

# Routes for registration pages
@app.route('/customer-registration')
def customer_registration():
    return render_template('CustomerRegistration.html')

def generate_registration_id(user_type):
    # Define prefixes for each user type
    prefixes = {'customer': '3', 'delivery_personnel': '2', 'vendor': '1'}
    
    # Generate random 3-digit number
    random_number = str(random.randint(0, 999)).zfill(3)
    
    # Construct RegistrationID with the appropriate prefix
    return prefixes.get(user_type, '3') + random_number

# Function to generate CustomerID
def generate_customer_id():
    # Query the last customer's ID from the database
    last_customer = Customer.query.order_by(Customer.CustomerID.desc()).first()

    if last_customer:
        # Extract the numeric part of the last CustomerID
        last_id_numeric = int(last_customer.CustomerID[4:]) + 1
    else:
        # If no customers exist yet, start with 21
        last_id_numeric = 21

    # Construct the new CustomerID
    return f'CUST{str(last_id_numeric).zfill(3)}'

# Route for handling customer registration
@app.route('/customer-registration-submit', methods=['POST'])
def customer_registration_submit():
    # Get form data
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    customer_password = request.form['customer_password']
    confirm_customer_password = request.form['confirm_customer_password']
    address = request.form['customer_address']
    phone_number = request.form['customer_phone']
    
    # Generate CustomerID
    customer_id = generate_customer_id()
    
    # Generate RegistrationID for customers
    registration_id = generate_registration_id('customer')
    
    # Create a new CustomerApproval object
    new_customer_approval = CustomerApproval(
        CustomerID=customer_id,
        RegistrationID=registration_id,
        CustomerName=customer_name,
        CustomerEmail=customer_email,
        CustomerPassword=customer_password,
        ConfirmCustomerPassword=confirm_customer_password,
        Address=address,
        PhoneNumber=phone_number
    )

    try:
        # Add the new customer approval entry to the database
        db.session.add(new_customer_approval)
        db.session.commit()
        # Redirect to the Customer Approval page
        return redirect(url_for('customer_approval'))
    except:
        # Handle any potential errors
        return 'Error processing registration'

# Route for rendering the Customer Approval page
@app.route('/customer-approval')
def customer_approval():
    return render_template('CustomerApproval.html')

@app.route('/vendor-registration')
def vendor_registration():
    return render_template('VendorRegistration1.html')

# Route for Vendor Registration Approval page
@app.route('/vendor-registration-approval')
def vendor_registration_approval():
    return render_template('VendorApproval.html')

# Route for handling vendor registration form submission
@app.route('/vendor-registration-submit', methods=['POST'])
def vendor_registration_submit():
    # Get form data
    vendor_name = request.form['vendor_name']
    vendor_email = request.form['vendor_email']
    phone_number = request.form['vendor_phone_number']
    address = request.form['vendor_address']
    password = request.form['vendor_password']
    confirm_password = request.form['confirm_vendor_password']
    
    # Generate RegistrationID for vendors (starts with 1xxx)
    registration_id = generate_registration_id('vendor')
    
    # Generate VendorID (starts with VENDxxx)
    vendor_id = generate_vendor_id()
    
    # Create a new VendorApproval object
    new_vendor_approval = VendorApproval(
        RegistrationID=registration_id,
        VendorID=vendor_id,
        VendorName=vendor_name,
        VendorEmail=vendor_email,
        PhoneNumber=phone_number,
        Address=address,
        VendorPassword=password,
        ConfirmVendorPassword=confirm_password
    )

    try:
        # Add the new vendor approval entry to the database
        db.session.add(new_vendor_approval)
        db.session.commit()
        # Redirect to the Vendor Approval page
        return redirect(url_for('vendor_registration_approval'))  # Changed 'vendor_approval' to 'vendor_registration_approval'
    except SQLAlchemyError as e:
        # Handle any potential errors
        return f'Error processing registration: {str(e)}'
    
def generate_vendor_id():
    # Query the last vendor's ID from the database
    last_vendor = Vendor.query.order_by(Vendor.VendorID.desc()).first()

    if last_vendor:
        # Extract the numeric part of the last VendorID
        last_id_numeric = int(last_vendor.VendorID[4:]) + 1
    else:
        # If no vendors exist yet, start with 1
        last_id_numeric = 21

    # Construct the new VendorID
    return f'VEND{str(last_id_numeric).zfill(3)}'

# Route for handling the redirection back to the homepage
@app.route('/')
def back_to_homepage():
    return redirect(url_for('main'))

@app.route('/delivery-personnel-registration')
def delivery_personnel_registration_page1():
    return render_template('DeliveryPersonnelRegistration.html')

@app.route('/delivery-personnel-registration-submit', methods=['POST'])
def delivery_personnel_registration_submit():
    # Get form data
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    phone = request.form['phone']
    license_no = request.form['license_no']
    previous_vehicles = request.form['previous_vehicles']
    
    # Generate RegistrationID for delivery personnel (starts with 2xxx)
    registration_id = generate_registration_id('delivery_personnel')
    
    # Generate PersonnelID (starts with DELxxx)
    personnel_id = generate_personnel_id()
    
    # Create a new DeliveryPersonnel object
    new_delivery_personnel = DeliveryPersonnel(
        PersonnelID=personnel_id,
        RegistrationID=registration_id,
        Name=name,
        Email=email,
        PhoneNumber=phone,
        Password=password,
        LicenseNumber=license_no,
        VehicleType=previous_vehicles,
        Status='Approved'
    )

    try:
        # Add the new delivery personnel entry to the database
        db.session.add(new_delivery_personnel)
        db.session.commit()
        # Redirect to the success page
        return redirect(url_for('registration_success'))
    except SQLAlchemyError as e:
        # Handle any potential errors
        return f'Error processing registration: {str(e)}'
    
def generate_registration_id(user_type):
    # Define prefixes for each user type
    prefixes = {'customer': '3', 'delivery_personnel': '2', 'vendor': '1'}
    
    # Generate random 3-digit number
    random_number = str(random.randint(0, 999)).zfill(3)
    
    # Construct RegistrationID with the appropriate prefix
    return prefixes.get(user_type, '3') + random_number

def generate_personnel_id():
    # Query the last personnel's ID from the database
    last_personnel = DeliveryPersonnel.query.order_by(DeliveryPersonnel.PersonnelID.desc()).first()

    if last_personnel:
        # Extract the numeric part of the last PersonnelID
        last_id_numeric = int(last_personnel.PersonnelID[3:]) + 1
    else:
        # If no personnel exist yet, start with 11
        last_id_numeric = 11

    # Construct the new PersonnelID
    return f'DEL{str(last_id_numeric).zfill(3)}'

@app.route('/registration-success')
def registration_success():
    return render_template('DeliveryPersonnelSuccess.html')
    
# Vendor
    
# Route for Vendor login
@app.route('/vendor-login', methods=['GET', 'POST'])
def vendor_login_page():
    if request.method == 'POST':
        vendor_id = request.form['vendor_id']
        password = request.form['password']
        
        # Query the Vendor table for the given ID
        vendor = Vendor.query.filter_by(VendorID=vendor_id).first()

        # Check if vendor exists and the password is correct
        if vendor and vendor.Password == password:
            # Set the user as logged in
            session['Vendor'] = vendor_id
            
            # Retrieve vendor's name and ID
            vendor_name = vendor.Name
            vendor_id = vendor.VendorID
            
            # Redirect to the vendor home route
            return redirect(url_for('vendor_home', name=vendor_name, id=vendor_id))  
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('VendorLoginPage.html', error=error)
    return render_template('VendorLoginPage.html')

# Route for Vendor logout
@app.route('/vendor-logout', methods=['GET', 'POST'])
def vendor_logout():
    session.pop('Vendor', None)
    return redirect(url_for('vendor_login_page'))  

# Route for Vendor home
@app.route('/vendor-home')
def vendor_home():
    if 'Vendor' in session:
        # Retrieve vendor's name and ID from the URL parameters
        vendor_name = request.args.get('name')
        vendor_id = request.args.get('id')
        return render_template('VendorHomePage.html', name=vendor_name, id=vendor_id)
    else:
        return redirect(url_for('vendor_login_page'))

# Customer

# Route for Customer login
@app.route('/customer-login', methods=['GET', 'POST'])
def customer_login_page():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        password = request.form['password']
        
        # Query the Customer table for the given ID
        customer = Customer.query.filter_by(CustomerID=customer_id).first()

        # Check if customer exists and the password is correct
        if customer and customer.Password == password:
            # Set the user as logged in
            session['Customer'] = customer_id
            
            # Retrieve customer's name and ID
            customer_name = customer.Name
            customer_id = customer.CustomerID
            
            # Redirect to the customer home route
            return redirect(url_for('customer_home', name=customer_name, id=customer_id))  
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('CustomerLogin.html', error=error)
    return render_template('CustomerLogin.html')

# Route for Customer logout
@app.route('/customer-logout', methods=['GET', 'POST'])
def customer_logout():
    session.pop('Customer', None)
    return redirect(url_for('customer_login_page'))  

# Route for Customer home
@app.route('/customer-home')
def customer_home():
    if 'Customer' in session:
        # Retrieve customer's name and ID from the URL parameters
        customer_name = request.args.get('name')
        customer_id = request.args.get('id')
        return render_template('CustomerHome.html', name=customer_name, id=customer_id)
    else:
        return redirect(url_for('customer_login_page')) 

@app.route("/customer-order")
def customer_order():
    # Fetch all registered vendors
    vendors = Vendor.query.all()

    # Fetch items associated with each vendor
    for vendor in vendors:
        vendor.items = Item.query.filter_by(VendorID=vendor.VendorID).all()

    # Pass vendors to the template
    return render_template('CustomerOrder.html', vendors=vendors)

@app.route("/customer-track")
def customer_track():
    return render_template('CustomerTrackOrder.html')

@app.route("/customer-feedback")
def customer_feedback():
    return render_template('CustomerFeedback.html')

@app.route("/customer-history")
def customer_history():
    return render_template('CustomerOrderHistory.html')

# Delivery Personnel

# Route for Delivery Personnel login
@app.route('/delivery-personnel-login', methods=['GET', 'POST'])
def delivery_personnel_login_page():
    if request.method == 'POST':
        personnel_id = request.form['personnel_id']
        password = request.form['password']
        
        # Query the DeliveryPersonnel table for the given ID
        personnel = DeliveryPersonnel.query.filter_by(PersonnelID=personnel_id).first()

        # Check if delivery personnel exists and the password is correct
        if personnel and personnel.Password == password:
            # Set the user as logged in
            session['DeliveryPersonnel'] = personnel_id
            
            # Retrieve delivery personnel's name and ID
            personnel_name = personnel.Name
            personnel_id = personnel.PersonnelID
            
            # Redirect to the delivery personnel home route
            return redirect(url_for('delivery_personnel_home', name=personnel_name, id=personnel_id))  
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('DeliveryPersonnelLogin.html', error=error)
    return render_template('DeliveryPersonnelLogin.html')

# Route for Delivery Personnel logout
@app.route('/delivery-personnel-logout', methods=['GET', 'POST'])
def delivery_personnel_logout():
    session.pop('DeliveryPersonnel', None)
    return redirect(url_for('delivery_personnel_login_page'))  

# Route for Delivery Personnel home
@app.route('/delivery-personnel-home')
def delivery_personnel_home():
    if 'DeliveryPersonnel' in session:
        # Retrieve delivery personnel's name and ID from the URL parameters
        personnel_name = request.args.get('name')
        personnel_id = request.args.get('id')
        return render_template('DeliveryPersonnelHomePage.html', name=personnel_name, id=personnel_id)
    else:
        return redirect(url_for('delivery_personnel_login_page'))

# System Manager

# Route for System Manager login
@app.route('/SystemManagerLogin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        system_manager_id = request.form['system_manager_id']
        password = request.form['password']
        
        # Query the SystemManager table for the given ID
        system_manager = SystemManager.query.filter_by(ManagerID=system_manager_id).first()

        # Check if system_manager exists and the password is correct
        if system_manager and system_manager.Password == password:
            # Set the user as logged in
            session['HomeCook'] = system_manager_id
            
            # Retrieve system manager's name and ID
            manager_name = system_manager.Name
            manager_id = system_manager.ManagerID
            
            # Redirect to the home route
            return redirect(url_for('home', name=manager_name, id=manager_id))  
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('SystemManagerLogin.html', error=error)
    return render_template('SystemManagerLogin.html')

# Route for System Manager home page
@app.route('/SystemManagerHome')
def home():
    if 'HomeCook' in session:
        # Retrieve system manager's name and ID from the URL parameters
        manager_name = request.args.get('name')
        manager_id = request.args.get('id')
        return render_template('SystemManagerHome.html', name=manager_name, id=manager_id)
    else:
        return redirect(url_for('login'))

# Route for logging out
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('HomeCook', None)
    return redirect(url_for('login'))

@app.route('/ViewVendor')
def view_vendor():
    # Query the Vendor table
    vendors = Vendor.query.all() 
    items = Item.query.all()
    return render_template('ViewVendor.html', vendors=vendors, items=items)

@app.route('/ViewCustomer')
def view_customer():
    # Query the Customers table
    customers = Customer.query.all() 
    return render_template('ViewCustomer.html', customers=customers)
    
# Route for the View Sales Report page
@app.route('/ViewSalesReport', methods=['GET', 'POST'])
def view_sales_report():
    if request.method == 'POST':
        # Get the selected date
        date = request.form.get('date')

        # Query the OrderItem table for items sold on the specified date
        order_items = OrderItem.query.filter_by(Date=date).all()

        # Create a dictionary to store total sales for each vendor
        vendor_sales = {}

        # Calculate total sales for each vendor
        for order_item in order_items:
            vendor_id = order_item.VendorID
            subtotal = float(order_item.Subtotal)
            if vendor_id in vendor_sales:
                vendor_sales[vendor_id] += subtotal
            else:
                vendor_sales[vendor_id] = subtotal

        # Sort vendor_sales dictionary by VendorID
        vendor_sales = dict(sorted(vendor_sales.items()))

        return render_template('ViewSalesReport.html', dates=get_dates_sales(), date=date, vendor_sales=vendor_sales)

    return render_template('ViewSalesReport.html', dates=get_dates_sales())

def get_dates_sales():
    # Fetch unique dates from the OrderItem table
    dates = db.session.query(OrderItem.Date).distinct().all()
    return [date[0] for date in dates]  # Extracting dates from tuples

@app.route('/ViewDeliveryReport', methods=['GET', 'POST'])
def view_delivery_report():
    if request.method == 'POST':
        # Get the selected date
        date = request.form.get('date')

        # Query the Order table for delivery information on the specified date
        delivery_info = Order.query.filter_by(Date=date).all()

        return render_template('ViewDeliveryReport.html', dates=get_dates(), delivery_info=delivery_info, selected_date=date)

    return render_template('ViewDeliveryReport.html', dates=get_dates())

def get_dates():
    # Fetch unique dates from the Order table
    dates = db.session.query(Order.Date).distinct().all()
    return [date[0] for date in dates] 

@app.route('/ApproveNewRegistration')
def approve_new_registration():
    # Query the Vendor Approval table for pending vendor registrations
    pending_vendor_registrations = VendorApproval.query.all()

    # Query the Customer Approval table for pending customer registrations
    pending_customer_registrations = CustomerApproval.query.all()

    return render_template('ApproveNewRegistration.html',
                           vendor_registrations=pending_vendor_registrations,
                           customer_registrations=pending_customer_registrations)

@app.route('/approve_customer/<registration_id>')
def approve_customer(registration_id):
    # Query the Customer Approval table for the customer registration to be approved
    customer_approval = CustomerApproval.query.filter_by(RegistrationID=registration_id).first()

    if customer_approval:
        # Create a new entry in the Customer table using the retrieved information
        new_customer = Customer(
            CustomerID=customer_approval.CustomerID,
            RegistrationID=customer_approval.RegistrationID,
            Name=customer_approval.CustomerName,
            Email=customer_approval.CustomerEmail,
            PhoneNumber=customer_approval.PhoneNumber,
            Address=customer_approval.Address,
            Password=customer_approval.CustomerPassword,
            Status='Approved'  # You can set the status as 'Approved' or any other status as needed
        )

        # Add the new customer entry to the database
        db.session.add(new_customer)

        try:
            # Commit the changes to the database
            db.session.commit()

            # Once the entry is successfully created, remove the corresponding entry from the Customer Approval table
            db.session.delete(customer_approval)
            db.session.commit()

            # Redirect to the "Approve New Registration" page after approval
            flash('Customer registration approved successfully', 'success')
            return redirect(url_for('approve_new_registration'))
        except Exception as e:
            # Handle any exceptions or errors
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('approve_new_registration'))

    else:
        # Handle the case where the registration ID is not found
        flash('Customer registration not found', 'error')
        return redirect(url_for('approve_new_registration'))
    
@app.route('/approve_vendor/<registration_id>')
def approve_vendor(registration_id):
    # Query the Vendor Approval table for the vendor registration to be approved
    vendor_approval = VendorApproval.query.filter_by(RegistrationID=registration_id).first()

    if vendor_approval:
        # Create a new entry in the Vendor table using the retrieved information
        new_vendor = Vendor(
            VendorID=vendor_approval.VendorID,
            RegistrationID=vendor_approval.RegistrationID,
            Name=vendor_approval.VendorName,
            Email=vendor_approval.VendorEmail,
            PhoneNumber=vendor_approval.PhoneNumber,
            Address=vendor_approval.Address,
            Password=vendor_approval.VendorPassword,
            Status='Approved'  # You can set the status as 'Approved' or any other status as needed
        )

        # Add the new vendor entry to the database
        db.session.add(new_vendor)

        try:
            # Commit the changes to the database
            db.session.commit()

            # Once the entry is successfully created, remove the corresponding entry from the Vendor Approval table
            db.session.delete(vendor_approval)
            db.session.commit()

            # Redirect to the "Approve New Registration" page after approval
            flash('Vendor registration approved successfully', 'success')
            return redirect(url_for('approve_new_registration'))
        except Exception as e:
            # Handle any exceptions or errors
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('approve_new_registration'))

    else:
        # Handle the case where the registration ID is not found
        flash('Vendor registration not found', 'error')
        return redirect(url_for('approve_new_registration'))

@app.route('/approve')
def approve():
    return render_template('Success.html')

@app.route('/decline')
def decline():
    return render_template('Decline.html')

@app.route('/dashboard')
def dashboard():
    return render_template('ApproveNewRegistration.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
