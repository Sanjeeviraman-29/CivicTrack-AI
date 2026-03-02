import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt
import datetime
from ai_engine import detect_category, detect_severity
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Database connection with error handling
try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = db.cursor(buffered=True)
    print("✓ Database connected successfully")
except mysql.connector.Error as err:
    print(f"✗ Database connection error: {err}")
    print("Make sure MySQL is running and the database 'civictrack_ai' exists")
    raise

@app.route('/')
def home():
    return jsonify({'message': 'Backend is running!', 'status': 'ok'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        cursor.execute("SELECT 1")
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({"message": "Name, email, and password are required"}), 400
        
        name = data['name']
        email = data['email']
        password = data['password']
        role = data.get('role', 'citizen')

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({"message": "Email already exists"}), 400

        # Hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Convert bytes to string for database storage
        hashed_pw_str = hashed_pw.decode('utf-8')

        query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, hashed_pw_str, role))
        db.commit()

        return jsonify({"message": "User Registered Successfully"}), 201
    
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"message": f"Registration error: {str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({"message": "Email and password are required"}), 400
        
        email = data['email']
        password = data['password']

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            # Get the hashed password from database (index 3)
            stored_hash = user[3]
            
            # Ensure stored_hash is in the right format (bytes)
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                token = jwt.encode({
                    'user_id': user[0],
                    'role': user[4],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)
                }, app.config['SECRET_KEY'], algorithm="HS256")

                return jsonify({"token": token}), 200

        return jsonify({"message": "Invalid Credentials"}), 401
    
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"message": f"Login error: {str(e)}"}), 500

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Token should come in headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            token = token.split(" ")[1]  # Remove "Bearer"
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/create-issue", methods=["POST"])
@token_required
def create_issue(current_user):
    data = request.json
    title = data['title']
    description = data['description']
    lat = data['latitude']
    lng = data['longitude']
    user_id = current_user['user_id']

    category = detect_category(description)
    severity = detect_severity(description)

    query = """INSERT INTO issues 
    (title, description, category, severity, latitude, longitude, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(query, (title, description, category, severity, lat, lng, user_id))
    db.commit()

    return jsonify({"message": "Issue Created"})

@app.route("/all-issues", methods=["GET"])
@token_required
@admin_required
def get_all_issues(current_user):

    cursor.execute("SELECT * FROM issues")
    issues = cursor.fetchall()

    return jsonify(issues)

@app.route("/update-status/<int:issue_id>", methods=["PUT"])
@token_required
@admin_required
def update_status(current_user, issue_id):

    data = request.json
    new_status = data['status']

    cursor.execute("UPDATE issues SET status=%s WHERE id=%s", (new_status, issue_id))
    db.commit()

    cursor.execute("INSERT INTO issue_history (issue_id, status) VALUES (%s, %s)", (issue_id, new_status))
    db.commit()

    return jsonify({"message": "Status Updated"})

@app.route("/category-stats", methods=["GET"])
@token_required
@admin_required
def category_stats(current_user):
    try:
        query = """
        SELECT category, COUNT(*) 
        FROM issues 
        GROUP BY category
        """

        cursor.execute(query)
        result = cursor.fetchall()

        data = []
        for row in result:
            data.append({
                "category": row[0],
                "count": row[1]
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/severity-stats", methods=["GET"])
@token_required
@admin_required
def severity_stats(current_user):
    try:
        query = """
        SELECT severity, COUNT(*) 
        FROM issues 
        GROUP BY severity
        """

        cursor.execute(query)
        result = cursor.fetchall()

        data = []
        for row in result:
            data.append({
                "severity": row[0],
                "count": row[1]
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/status-stats", methods=["GET"])
@token_required
@admin_required
def status_stats(current_user):

    query = """
    SELECT status, COUNT(*) 
    FROM issues 
    GROUP BY status
    """

    cursor.execute(query)
    result = cursor.fetchall()

    data = []
    for row in result:
        data.append({
            "status": row[0],
            "count": row[1]
        })

    return jsonify(data)

@app.route("/resolution-time", methods=["GET"])
@token_required
@admin_required
def resolution_time(current_user):

    query = """
    SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, 
        (SELECT updated_at FROM issue_history 
         WHERE issue_id = issues.id 
         ORDER BY updated_at DESC LIMIT 1)))
    FROM issues
    WHERE status = 'Resolved'
    """

    cursor.execute(query)
    result = cursor.fetchone()

    avg_hours = result[0] if result[0] else 0

    return jsonify({"average_resolution_hours": avg_hours})

@app.route("/map-issues", methods=["GET"])
@token_required
@admin_required
def map_issues(current_user):

    query = """
    SELECT id, title, latitude, longitude, severity, status
    FROM issues
    """

    cursor.execute(query)
    result = cursor.fetchall()

    data = []
    for row in result:
        data.append({
            "id": row[0],
            "title": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "severity": row[4],
            "status": row[5]
        })

    return jsonify(data)

@app.route("/my-issues", methods=["GET"])
@token_required
def my_issues(current_user):

    user_id = current_user['user_id']

    query = "SELECT * FROM issues WHERE created_by=%s"
    cursor.execute(query, (user_id,))
    issues = cursor.fetchall()

    return jsonify(issues)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("CivicTrack AI Backend Starting...")
    print("="*50)
    print(f"Database: {os.getenv('DB_HOST')} - {os.getenv('DB_NAME')}")
    print(f"Running on: http://localhost:5000")
    print(f"Health Check: http://localhost:5000/health")
    print("="*50 + "\n")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        raise