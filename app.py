from flask import Flask, render_template, request, redirect, url_for, session,send_file

import requests
from werkzeug.utils import secure_filename
import os
from flask import jsonify

import ibm_db


import ibm_boto3
from ibm_botocore.client import Config

from ibm_botocore.exceptions import ParamValidationError

app = Flask(__name__)
app.secret_key = 'kyadukey'  # Change this to a secure random key


# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



#conn = ibm_db.connect("DATABASE=bludb ;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=cdd46291;PWD=PRXIWbfPAOOEGBiM;", '', '')
conn = ibm_db.connect("DATABASE=bludb ;HOSTNAME=764264db-9824-4b7c-82df-40d1b13897c2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32536;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ngz04813;PWD=8W4gMq4vriIXheuX;", '', '')

print(conn)



# IBM Cloud Object Storage credentials
cos_credentials = {
    'IAM_SERVICE_ID': 'crn:v1:bluemix:public:cloud-object-storage:global:a/4e3c3ad0de00416e8412e8f5da74e639:bc3b6e8b-49c8-4394-9cfa-8d13e5827b91:bucket:dibmbuck',
    'IBM_API_KEY_ID': 'znuPiGM8IN6v88CA8zsyzw4WWdUymlS-xc9ByJiX2kuI',
    'ENDPOINT': 'https://s3.eu-de.cloud-object-storage.appdomain.cloud',
    'IBM_AUTH_ENDPOINT': 'https://iam.cloud.ibm.com/identity/token',
    'BUCKET_NAME': 'dibmbuck',
}


# Create an IBM Cloud Object Storage client
cos_client = ibm_boto3.client('s3',
    ibm_api_key_id=cos_credentials['IBM_API_KEY_ID'],
    ibm_service_instance_id=cos_credentials['IAM_SERVICE_ID'],
    ibm_auth_endpoint=cos_credentials['IBM_AUTH_ENDPOINT'],
    config=Config(signature_version='oauth'),
    endpoint_url=cos_credentials['ENDPOINT']
)



@app.route('/')
def landing():

    return render_template("landing.html",imagurl="https://dibmbuck.s3.eu-de.cloud-object-storage.appdomain.cloud/co2car.jpg")

@app.route('/home')
def home():
    userid = session.get('userid')

    if userid:
        return render_template("home.html")
    else:
        return redirect(url_for('login'))
    

@app.route('/pickride')
def pickride():
    # Check if the user is logged in
    if 'userid' not in session:
        return redirect(url_for('login'))

    return render_template("pickride.html")



@app.route('/fetch_rides', methods=['POST'])
def fetch_rides():
    leaving_from = request.form.get('leavingFrom')
    going_to = request.form.get('goingTo')
    date = request.form.get('date')


    try:

        # Prepare and execute the SQL query
        sql = """
            SELECT "FULLNAME", "PHONENUMBER", "LOCATION", "DESTINATION", "NUMBEROFPEOPLE", "USERPROFILE"
            FROM "RIDEPUBLISH"
            WHERE "LOCATION" = ? AND "DESTINATION" = ?
        """

        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, leaving_from)
        ibm_db.bind_param(stmt, 2, going_to)
        #ibm_db.bind_param(stmt, 3, date)
        #print(stmt)
        ibm_db.execute(stmt)

        # Fetch results
        rides_list = []
        result = ibm_db.fetch_assoc(stmt)
        while result:
            rides_list.append(result)
            result = ibm_db.fetch_assoc(stmt)
        return jsonify(rides_list)

    except Exception as e:
        return jsonify({"error": str(e)})

    



@app.route('/publishride', methods=['GET', 'POST'])
def publishride():
    # Check if the user is logged in
    if 'userid' not in session:
        return redirect(url_for('login'))

    error = None
    
    if request.method == 'POST':
        # Retrieve user information from the session


        sql = "SELECT * FROM USERS WHERE USERID = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['userid'])
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        email = account['EMAIL']

        # Retrieve ride details from the form
        full_name = request.form['fullName']
        phone_no = request.form['phoneNo']
        leaving_from = request.form['leavingFrom']
        going_to = request.form['goingTo']
        date_time = request.form['dateTime']
        no_of_people = request.form['noOfPeople']
        trip_password = request.form['password']


        file = request.files['profilePicInput']


        # Check if the file has an allowed extension
        if file and allowed_file(file.filename):
            # Securely save the file to the upload folder
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            cos_client.upload_file(filepath, "dibmbuck", filename)

            # Optionally, you can store the filename in a database or use it in your application

        else:
            error =  'Invalid file type. Allowed extensions are: png, jpg, jpeg, gif'



        # Insert the ride details into the database
        insert_sql = """
            INSERT INTO RIDEPUBLISH (FULLNAME,PHONENUMBER,EMAIL,PASSWORD,LOCATION,DESTINATION,DATETIME,NUMBEROFPEOPLE,USERID,USERPROFILE)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        insert_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(insert_stmt, 1, full_name)
        ibm_db.bind_param(insert_stmt, 2, phone_no)
        ibm_db.bind_param(insert_stmt, 3, email)
        ibm_db.bind_param(insert_stmt, 4, trip_password)
        ibm_db.bind_param(insert_stmt, 5, leaving_from)
        ibm_db.bind_param(insert_stmt, 6, going_to)
        ibm_db.bind_param(insert_stmt, 7, date_time)
        ibm_db.bind_param(insert_stmt, 8, no_of_people)
        ibm_db.bind_param(insert_stmt, 9, session['userid'])
        ibm_db.bind_param(insert_stmt, 10, filename)
        ibm_db.execute(insert_stmt)


        # Redirect to a confirmation page or any other page as needed
        return redirect(url_for('pickride'))

    return render_template('publishride.html', error=error if 'error' in locals() else None)




class CO2EmissionCalculator:
    def __init__(self, vehicle_type, fuel_type, distance_km, num_people):
        self.vehicle_type = vehicle_type
        self.fuel_type = fuel_type
        self.distance_km = distance_km
        self.num_people = num_people

    def calculate_emission(self):
        # Emission factors (g CO2 per km) for different vehicle types and fuel types
        emission_factors = {
            'car': {'petrol': 120, 'diesel': 100, 'electric': 0},
            'bike': {'petrol': 50, 'electric': 0},  # Added for bike
            'bus': {'diesel': 180, 'electric': 0},  # Added for bus
            'mini_bus': {'diesel': 160, 'electric': 0}
            # Add more vehicle types and fuel types as needed
        }

        # Check if the vehicle type and fuel type are valid
        if self.vehicle_type not in emission_factors or self.fuel_type not in emission_factors[self.vehicle_type]:
            return "Invalid vehicle type or fuel type"

        # Calculate total CO2 emissions
        emission_factor = emission_factors[self.vehicle_type][self.fuel_type]
        total_emission = emission_factor * self.distance_km
        # Adjust emissions based on the number of people in the vehicle
        if int(self.num_people) > 1:
            total_emission /= int(self.num_people)

        return total_emission







@app.route('/co2check')
def co2check():
    if 'userid' not in session:
        return redirect(url_for('login'))
    return render_template("co2cal.html")


@app.route('/co2calculate', methods=['GET', 'POST'])
def co2calculate():
    if 'userid' not in session:
        return redirect(url_for('login'))
    error=None
    result = None
    if request.method == 'POST':
        vehicle_type = request.form['vehicletype']
        vehicle_fuel_type = request.form['vehiclefueltype']
        distance = int(request.form['distance'])
        no_of_people = int(request.form['noofpeople'])

        # Create an instance of CO2EmissionCalculator
        calculator = CO2EmissionCalculator(vehicle_type, vehicle_fuel_type, distance, no_of_people)

        # Calculate and print CO2 emissions
        result = "For "+str(vehicle_type)+" with fuel type "+ str(vehicle_fuel_type)+ " having travel distance " +str(distance)+\
        " and no of perople "+str(no_of_people)+" the co2 emssion count is "+str(calculator.calculate_emission())



        insert_sql = """
            INSERT INTO VEHICLES ("VEHICLETYPE", "VEHICLEFUELTYPE", "DISTANCE", "NOOFPEOPLE", "CO2EPP", "CO2E")
            VALUES (?, ?, ?, ?, ?, ?)
        """

        insert_stmt = ibm_db.prepare(conn, insert_sql)

        ibm_db.bind_param(insert_stmt, 1, vehicle_type)
        ibm_db.bind_param(insert_stmt, 2, vehicle_fuel_type)
        ibm_db.bind_param(insert_stmt, 3, distance)
        ibm_db.bind_param(insert_stmt, 4, no_of_people)
        ibm_db.bind_param(insert_stmt, 5, str(calculator.calculate_emission()))
        ibm_db.bind_param(insert_stmt, 6, "")
        ibm_db.execute(insert_stmt)



    return render_template('co2calculate.html', error=error if 'error' in locals() else None, result=result)





# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        userid = request.form['username']
        password = request.form['password']

        # Prepare and execute the SQL statement to fetch the user
        sql = "SELECT * FROM USERS WHERE USERID = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, userid)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        # Close the database connection
        #ibm_db.close(conn)

        if account and account['PASSWORD'] == password:
            # Successful login, you may redirect to a dashboard or another page
            session['userid'] = userid
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'

    return render_template('login.html', error=error if 'error' in locals() else None)




@app.route('/logout')
def logout():
    # Clear the userid from the session
    session.pop('userid', None)
    
    # Redirect to the login page
    return redirect(url_for('login'))





# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if the user is already logged in
    if 'userid' in session:
        return redirect(url_for('home'))

    error = None

    if request.method == 'POST':
        userid = request.form['userid']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']


        # Check if the userid or email already exists
        check_sql = "SELECT * FROM USERS WHERE UserID = ? OR Email = ?"
        check_stmt = ibm_db.prepare(conn, check_sql)
        ibm_db.bind_param(check_stmt, 1, userid)
        ibm_db.bind_param(check_stmt, 2, email)
        ibm_db.execute(check_stmt)
        existing_user = ibm_db.fetch_assoc(check_stmt)

        if existing_user:
            error = 'User ID or email already exists. Please choose a different one.'
        else:
            # Insert the new user into the database
            insert_sql = "INSERT INTO USERS (UserID, USERNAME, Email, Password) VALUES (?, ?, ?, ?)"
            insert_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(insert_stmt, 1, userid)
            ibm_db.bind_param(insert_stmt, 2, name)
            ibm_db.bind_param(insert_stmt, 3, email)
            ibm_db.bind_param(insert_stmt, 4, password)
            ibm_db.execute(insert_stmt)

            # Close the database connection
            #ibm_db.close(conn)

            # Redirect to the login page after successful registration
            return redirect(url_for('login'))

    return render_template('register.html', error=error if 'error' in locals() else None)






if __name__ == "__main__":
    app.run(debug = True,port = 5000)



#try@try.com try