from flask import Flask, render_template, request, redirect, url_for, session, jsonify,Response
import pymongo
import csv
from io import StringIO
from datetime import datetime
from config import MONGO_CONFIG

app = Flask(__name__)
app.secret_key = "your_secret_key"

# User credentials for login
USERS = {
    "admin": "password123",
}

# Connect to MongoDB
try:
    mongo_client = pymongo.MongoClient(MONGO_CONFIG["host"], MONGO_CONFIG["port"])
    mongo_db = mongo_client[MONGO_CONFIG["database"]]
    logs_collection = mongo_db.logs
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

# Insert logs into MongoDB
def insert_log(log_message, message, log_level="INFO"):
    log_entry = {
        "log_level": log_level,
        "log_message": log_message,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    logs_collection.insert_one(log_entry)

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('secure_logs'))
        else:
            return render_template('login.html', error="Invalid credentials!")

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# Secure Logs (Requires Login)
@app.route('/secure-logs')
def secure_logs():
    if 'user' not in session:
        return redirect(url_for('login'))

    logs = list(logs_collection.find({}, {"_id": 0}))
    return render_template('secure_logs.html', logs=logs)

# Add log (form-based submission)
@app.route('/add_log', methods=['GET', 'POST'])
def add_log():
    if request.method == 'POST':
        log_message = request.form.get('log_message', 'No message provided')
        message = request.form.get('message', 'No details')
        log_level = request.form.get('log_level', 'INFO')
        
        insert_log(log_message, message, log_level)
        return redirect('/logs')
    return render_template('add_log.html')


# Public Logs (No Authentication)
# Public Logs (Display in HTML Table)
@app.route('/logs', methods=['GET'])
def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}))
    return render_template('logs.html', logs=logs)

# Ensure initial logs exist
if logs_collection.count_documents({}) == 0:
    insert_log("System initialized", "Initialization complete", "INFO")
    insert_log("User login success", "User logged in", "INFO")
    insert_log("Input validation error", "Invalid input detected", "ERROR")

@app.route('/search_logs')
def search_logs():
    query = request.args.get('query', '')

    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    # Perform case-insensitive search on all relevant fields
    search_filter = {
        "$or": [
            {"log_message": {"$regex": query, "$options": "i"}},
            {"message": {"$regex": query, "$options": "i"}},
            {"log_level": {"$regex": query, "$options": "i"}}
        ]
    }

    # Fetch matching logs from MongoDB
    matching_logs = list(logs_collection.find(search_filter, {"_id": 0}))
    return jsonify(matching_logs)



@app.route('/download_logs')
def download_logs():
    logs = list(logs_collection.find({}, {"_id": 0}))

    # Prepare CSV
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Header
    csv_writer.writerow(["Log Level", "Log Message", "Message Details", "Timestamp"])

    # Data Rows
    for log in logs:
        csv_writer.writerow([
            log.get("log_level", ""),
            log.get("log_message", ""),
            log.get("message", ""),
            log.get("timestamp", "")
        ])

    # Serve CSV as a downloadable file
    response = Response(csv_buffer.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=public_logs.csv"
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)