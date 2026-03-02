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
from werkzeug.utils import secure_filename
from datetime import datetime as dt

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Get all resolvers
@app.route("/resolvers", methods=["GET"])
@token_required
@admin_required
def get_resolvers(current_user):
    try:
        query = "SELECT id, name, email FROM users WHERE role=%s"
        cursor.execute(query, ('resolver',))
        resolvers = cursor.fetchall()
        
        data = []
        for resolver in resolvers:
            data.append({
                "id": resolver[0],
                "name": resolver[1],
                "email": resolver[2]
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Assign issue to resolver
@app.route("/assign-issue", methods=["POST"])
@token_required
@admin_required
def assign_issue(current_user):
    try:
        data = request.json
        issue_id = data['issue_id']
        resolver_id = data['resolver_id']
        
        query = "UPDATE issues SET assigned_to=%s, status=%s WHERE id=%s"
        cursor.execute(query, (resolver_id, 'In Progress', issue_id))
        db.commit()
        
        # Log assignment
        query_log = "INSERT INTO issue_assignments (issue_id, assigned_by, assigned_to, assignment_date) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query_log, (issue_id, current_user['user_id'], resolver_id))
        db.commit()
        
        return jsonify({"message": "Issue Assigned Successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get assigned issues for resolver
@app.route("/my-assignments", methods=["GET"])
@token_required
def get_my_assignments(current_user):
    try:
        user_id = current_user['user_id']
        
        query = """
        SELECT i.id, i.title, i.description, i.category, i.severity, 
               i.latitude, i.longitude, i.status, u.name, i.created_at
        FROM issues i
        LEFT JOIN users u ON i.created_by = u.id
        WHERE i.assigned_to=%s
        ORDER BY i.created_at DESC
        """
        
        cursor.execute(query, (user_id,))
        assignments = cursor.fetchall()
        
        data = []
        for assignment in assignments:
            data.append({
                "id": assignment[0],
                "title": assignment[1],
                "description": assignment[2],
                "category": assignment[3],
                "severity": assignment[4],
                "latitude": assignment[5],
                "longitude": assignment[6],
                "status": assignment[7],
                "reported_by": assignment[8],
                "created_at": str(assignment[9])
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Complete issue - resolver notifies completion
@app.route("/complete-issue", methods=["POST"])
@token_required
def complete_issue(current_user):
    try:
        data = request.json
        issue_id = data['issue_id']
        comments = data.get('comments', '')
        
        # Update issue status to Resolved
        query = "UPDATE issues SET status=%s, resolved_at=NOW() WHERE id=%s"
        cursor.execute(query, ('Resolved', issue_id))
        db.commit()
        
        # Log completion
        query_log = "INSERT INTO issue_resolutions (issue_id, resolved_by, comments, resolution_date) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query_log, (issue_id, current_user['user_id'], comments))
        db.commit()
        
        return jsonify({"message": "Issue Marked as Resolved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get resolved issues with resolver details
@app.route("/resolved-issues", methods=["GET"])
@token_required
@admin_required
def get_resolved_issues(current_user):
    try:
        # Try with verification_status column first, fall back if it doesn't exist
        try:
            query = """
            SELECT i.id, i.title, i.category, i.severity, 
                   u.name as resolved_by, ir.resolution_date, ir.comments, 
                   i.verification_status, ir.image_path
            FROM issues i
            LEFT JOIN users u ON i.assigned_to = u.id
            LEFT JOIN issue_resolutions ir ON i.id = ir.issue_id
            WHERE i.status IN ('Resolved', 'Awaiting Verification')
            ORDER BY ir.resolution_date DESC
            """
            
            cursor.execute(query)
            resolved = cursor.fetchall()
        except mysql.connector.Error:
            # Column doesn't exist, use default values
            query = """
            SELECT i.id, i.title, i.category, i.severity, 
                   u.name as resolved_by, ir.resolution_date, ir.comments, 
                   NULL, ir.image_path
            FROM issues i
            LEFT JOIN users u ON i.assigned_to = u.id
            LEFT JOIN issue_resolutions ir ON i.id = ir.issue_id
            WHERE i.status IN ('Resolved', 'Awaiting Verification')
            ORDER BY ir.resolution_date DESC
            """
            
            cursor.execute(query)
            resolved = cursor.fetchall()
        
        data = []
        for item in resolved:
            image_path = item[8] if item[8] else None
            if image_path and image_path.startswith('uploads'):
                image_path = f"http://127.0.0.1:5000/{image_path}"
            
            data.append({
                "id": item[0],
                "title": item[1],
                "category": item[2],
                "severity": item[3],
                "resolved_by": item[4],
                "resolution_date": str(item[5]),
                "comments": item[6],
                "verification_status": item[7] or "Pending",
                "image_path": image_path
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Complete issue with image upload - resolver uploads work completion photo
@app.route("/complete-issue-with-image", methods=["POST"])
@token_required
def complete_issue_with_image(current_user):
    try:
        # Check if image is provided
        if 'image' not in request.files:
            return jsonify({"message": "No image provided"}), 400
        
        file = request.files['image']
        issue_id = request.form.get('issue_id')
        comments = request.form.get('comments', '')
        
        if not issue_id:
            return jsonify({"message": "Issue ID is required"}), 400
        
        if not file or file.filename == '':
            return jsonify({"message": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"message": "File type not allowed. Use: png, jpg, jpeg, gif, webp"}), 400
        
        # Generate unique filename
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"issue_{issue_id}_{timestamp}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Update issue status to "Awaiting Verification"
        # Try with verification_status first, fall back if column doesn't exist
        try:
            query = "UPDATE issues SET status=%s, verification_status=%s, resolved_at=NOW() WHERE id=%s"
            cursor.execute(query, ('Awaiting Verification', 'Pending', issue_id))
            db.commit()
        except mysql.connector.Error as e:
            if "Unknown column" in str(e) and "verification_status" in str(e):
                # Column doesn't exist yet, just update status
                query = "UPDATE issues SET status=%s, resolved_at=NOW() WHERE id=%s"
                cursor.execute(query, ('Awaiting Verification', issue_id))
                db.commit()
            else:
                raise
        
        # Log completion with image
        query_log = "INSERT INTO issue_resolutions (issue_id, resolved_by, comments, image_path, resolution_date) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(query_log, (issue_id, current_user['user_id'], comments, filepath))
        db.commit()
        
        return jsonify({"message": "Issue completion uploaded. Awaiting citizen verification.", "image_path": filepath})
    except Exception as e:
        print(f"Complete issue error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Get pending verifications for citizen
@app.route("/pending-verifications", methods=["GET"])
@token_required
def get_pending_verifications(current_user):
    try:
        user_id = current_user['user_id']
        
        # Try with verification_status column
        try:
            query = """
            SELECT i.id, i.title, i.description, i.category, i.severity, 
                   i.latitude, i.longitude, i.status, u.name, i.created_at,
                   ir.comments, ir.image_path, ir.resolution_date
            FROM issues i
            LEFT JOIN users u ON i.assigned_to = u.id
            LEFT JOIN issue_resolutions ir ON i.id = ir.issue_id
            WHERE i.created_by=%s AND i.verification_status='Pending'
            ORDER BY i.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            verifications = cursor.fetchall()
        except mysql.connector.Error:
            # Column doesn't exist, return all unresolved issues
            query = """
            SELECT i.id, i.title, i.description, i.category, i.severity, 
                   i.latitude, i.longitude, i.status, u.name, i.created_at,
                   ir.comments, ir.image_path, ir.resolution_date
            FROM issues i
            LEFT JOIN users u ON i.assigned_to = u.id
            LEFT JOIN issue_resolutions ir ON i.id = ir.issue_id
            WHERE i.created_by=%s AND i.status IN ('Awaiting Verification', 'Resolved')
            ORDER BY i.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            verifications = cursor.fetchall()
        
        data = []
        for v in verifications:
            # Make image path relative for frontend
            image_path = v[11] if v[11] else None
            if image_path and image_path.startswith('uploads'):
                image_path = f"http://127.0.0.1:5000/{image_path}"
            
            data.append({
                "id": v[0],
                "title": v[1],
                "description": v[2],
                "category": v[3],
                "severity": v[4],
                "latitude": v[5],
                "longitude": v[6],
                "status": v[7],
                "resolver_name": v[8],
                "created_at": str(v[9]),
                "comments": v[10],
                "image_path": image_path,
                "resolution_date": str(v[12]) if v[12] else None
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Verify issue completion - citizen approves the work
@app.route("/verify-issue", methods=["POST"])
@token_required
def verify_issue(current_user):
    try:
        data = request.json
        issue_id = data.get('issue_id')
        
        if not issue_id:
            return jsonify({"message": "Issue ID is required"}), 400
        
        # Verify that current user is the issue creator
        query = "SELECT created_by FROM issues WHERE id=%s"
        cursor.execute(query, (issue_id,))
        issue = cursor.fetchone()
        
        if not issue or issue[0] != current_user['user_id']:
            return jsonify({"message": "Unauthorized"}), 403
        
        # Update issue to verified
        try:
            query = "UPDATE issues SET verification_status=%s, verified_by=%s WHERE id=%s"
            cursor.execute(query, ('Verified', current_user['user_id'], issue_id))
            db.commit()
        except mysql.connector.Error as e:
            if "Unknown column" in str(e):
                # Columns don't exist yet, skip this step
                pass
            else:
                raise
        
        # Log verification
        query_log = "INSERT INTO verification_history (issue_id, verified_by, action, verification_date) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query_log, (issue_id, current_user['user_id'], 'Approved'))
        db.commit()
        
        return jsonify({"message": "Issue verified successfully. Status updated to Resolved."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reject issue completion - citizen rejects the work
@app.route("/reject-issue", methods=["POST"])
@token_required
def reject_issue(current_user):
    try:
        data = request.json
        issue_id = data.get('issue_id')
        reason = data.get('reason', '')
        
        if not issue_id:
            return jsonify({"message": "Issue ID is required"}), 400
        
        # Verify that current user is the issue creator
        query = "SELECT created_by FROM issues WHERE id=%s"
        cursor.execute(query, (issue_id,))
        issue = cursor.fetchone()
        
        if not issue or issue[0] != current_user['user_id']:
            return jsonify({"message": "Unauthorized"}), 403
        
        # Revert issue back to "In Progress" for resolver to redo
        try:
            query = "UPDATE issues SET status=%s, verification_status=%s WHERE id=%s"
            cursor.execute(query, ('In Progress', 'Rejected', issue_id))
            db.commit()
        except mysql.connector.Error as e:
            if "Unknown column" in str(e):
                # Column doesn't exist yet, just update status
                query = "UPDATE issues SET status=%s WHERE id=%s"
                cursor.execute(query, ('In Progress', issue_id))
                db.commit()
            else:
                raise
        
        # Log rejection
        query_log = "INSERT INTO verification_history (issue_id, verified_by, action, reason, verification_date) VALUES (%s, %s, %s, %s, NOW())"
        cursor.execute(query_log, (issue_id, current_user['user_id'], 'Rejected', reason))
        db.commit()
        
        return jsonify({"message": "Issue rejected. Resolver has been notified to re-do the work."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve uploaded images
@app.route('/uploads/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            from flask import send_file
            return send_file(file_path, mimetype='image/*')
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Search and filter issues
@app.route("/search-issues", methods=["POST"])
@token_required
def search_issues(current_user):
    try:
        data = request.json
        status_filter = data.get('status')
        severity_filter = data.get('severity')
        category_filter = data.get('category')
        search_text = data.get('search', '')
        
        query = "SELECT * FROM issues WHERE 1=1"
        params = []
        
        # Search by title or description
        if search_text:
            query += " AND (title LIKE %s OR description LIKE %s)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param])
        
        # Filter by status
        if status_filter and status_filter != 'All':
            query += " AND status=%s"
            params.append(status_filter)
        
        # Filter by severity
        if severity_filter and severity_filter != 'All':
            query += " AND severity=%s"
            params.append(severity_filter)
        
        # Filter by category
        if category_filter and category_filter != 'All':
            query += " AND category=%s"
            params.append(category_filter)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        issues = cursor.fetchall()
        
        data_list = []
        for issue in issues:
            data_list.append({
                "id": issue[0],
                "title": issue[1],
                "description": issue[2],
                "category": issue[3],
                "severity": issue[4],
                "latitude": issue[5],
                "longitude": issue[6],
                "created_by": issue[7],
                "status": issue[8],
                "created_at": str(issue[9]),
                "updated_at": str(issue[10]),
                "assigned_to": issue[11],
                "resolved_at": str(issue[12]) if issue[12] else None
            })
        
        return jsonify(data_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dashboard statistics
@app.route("/dashboard-stats", methods=["GET"])
@token_required
@admin_required
def dashboard_stats(current_user):
    try:
        stats = {}
        
        # Total issues
        cursor.execute("SELECT COUNT(*) FROM issues")
        stats['total_issues'] = cursor.fetchone()[0]
        
        # Issues by status
        cursor.execute("SELECT status, COUNT(*) FROM issues GROUP BY status")
        status_stats = cursor.fetchall()
        stats['by_status'] = {status: count for status, count in status_stats}
        
        # Issues by severity
        cursor.execute("SELECT severity, COUNT(*) FROM issues GROUP BY severity")
        severity_stats = cursor.fetchall()
        stats['by_severity'] = {severity: count for severity, count in severity_stats}
        
        # Issues by category
        cursor.execute("SELECT category, COUNT(*) FROM issues GROUP BY category")
        category_stats = cursor.fetchall()
        stats['by_category'] = {category: count for category, count in category_stats}
        
        # Resolvers count
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='resolver'")
        stats['total_resolvers'] = cursor.fetchone()[0]
        
        # Citizens count
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='citizen'")
        stats['total_citizens'] = cursor.fetchone()[0]
        
        # Average resolution time
        cursor.execute("""
            SELECT AVG(TIMESTAMPDIFF(HOUR, created_at, resolved_at)) 
            FROM issues 
            WHERE resolved_at IS NOT NULL
        """)
        result = cursor.fetchone()[0]
        stats['avg_resolution_hours'] = round(result, 2) if result else 0
        
        # Verification success rate
        try:
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN verification_status = 'Verified' THEN 1 END) as verified,
                    COUNT(CASE WHEN verification_status IN ('Verified', 'Rejected') THEN 1 END) as total
                FROM issues
                WHERE verification_status IS NOT NULL
            """)
            verified, total = cursor.fetchone()
            stats['verification_success_rate'] = round((verified / total * 100), 2) if total > 0 else 0
        except mysql.connector.Error:
            # Column doesn't exist yet
            stats['verification_success_rate'] = 0
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Issue timeline/history
@app.route("/issue-timeline/<int:issue_id>", methods=["GET"])
@token_required
def issue_timeline(current_user, issue_id):
    try:
        timeline = []
        
        # Get issue basic info
        try:
            cursor.execute("SELECT id, title, created_by, created_at, assigned_to, resolved_at, verification_status FROM issues WHERE id=%s", (issue_id,))
        except mysql.connector.Error:
            # Columns might include verification_status which doesn't exist
            cursor.execute("SELECT id, title, created_by, created_at, assigned_to, resolved_at FROM issues WHERE id=%s", (issue_id,))
            issue_data = cursor.fetchone()
            if issue_data:
                issue = (*issue_data, None)  # Add None for verification_status
            else:
                issue = None
        else:
            issue = cursor.fetchone()
        
        if not issue:
            return jsonify({"error": "Issue not found"}), 404
        
        # Event 1: Issue reported
        cursor.execute("SELECT name FROM users WHERE id=%s", (issue[2],))
        reporter = cursor.fetchone()
        timeline.append({
            "event": "Issue Reported",
            "timestamp": str(issue[3]),
            "by": reporter[0] if reporter else "Unknown",
            "details": f"Issue '{issue[1]}' reported"
        })
        
        # Event 2: Issue assigned
        if issue[4]:
            cursor.execute("""
                SELECT ia.assignment_date, u.name 
                FROM issue_assignments ia 
                JOIN users u ON ia.assigned_to = u.id 
                WHERE ia.issue_id=%s 
                LIMIT 1
            """, (issue_id,))
            assignment = cursor.fetchone()
            if assignment:
                timeline.append({
                    "event": "Assigned to Resolver",
                    "timestamp": str(assignment[0]),
                    "by": assignment[1],
                    "details": f"Issue assigned to {assignment[1]}"
                })
        
        # Event 3: Work completed
        if issue[5]:
            cursor.execute("""
                SELECT ir.resolution_date, u.name, ir.comments 
                FROM issue_resolutions ir 
                JOIN users u ON ir.resolved_by = u.id 
                WHERE ir.issue_id=%s 
                LIMIT 1
            """, (issue_id,))
            resolution = cursor.fetchone()
            if resolution:
                timeline.append({
                    "event": "Work Completed",
                    "timestamp": str(resolution[0]),
                    "by": resolution[1],
                    "details": resolution[2] or "Work completed"
                })
        
        # Event 4: Work verified/rejected
        if issue[6]:
            cursor.execute("""
                SELECT vh.verification_date, u.name, vh.action, vh.reason 
                FROM verification_history vh 
                JOIN users u ON vh.verified_by = u.id 
                WHERE vh.issue_id=%s 
                ORDER BY vh.verification_date DESC 
                LIMIT 1
            """, (issue_id,))
            verification = cursor.fetchone()
            if verification:
                timeline.append({
                    "event": "Work " + verification[2],
                    "timestamp": str(verification[0]),
                    "by": verification[1],
                    "details": verification[3] or f"Work {verification[2]}"
                })
        
        return jsonify(timeline)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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