# CivicTrack AI - Setup Checklist for Work Assignment Feature

## Prerequisites ✓
- Python 3.8+
- MySQL 5.7+
- Node.js (for frontend if needed)
- Flask and dependencies installed

## Database Setup

### 1. Run Migration
```bash
# Connect to your MySQL database and run:
mysql -u your_username -p your_database < database_migration.sql
```

Alternatively, run in MySQL Client:
```sql
-- Execute all commands from database_migration.sql
```

### 2. Verify Tables
```sql
SHOW TABLES; -- Should see: users, issues, issue_assignments, issue_resolutions, issue_history

DESCRIBE issues; -- Verify assigned_to and resolved_at columns exist

DESCRIBE issue_assignments; -- Verify table structure

DESCRIBE issue_resolutions; -- Verify table structure
```

## Backend Setup

### 1. Verify Endpoints Added
Check `backend/app.py` contains these endpoints:
- [ ] GET /resolvers
- [ ] POST /assign-issue
- [ ] GET /my-assignments
- [ ] POST /complete-issue
- [ ] GET /resolved-issues

### 2. Dependencies
All required packages should be in `backend/requirements.txt`:
```
Flask
Flask-CORS
mysql-connector-python
bcrypt
PyJWT
python-dotenv
```

Install with:
```bash
pip install -r backend/requirements.txt
```

### 3. Environment Variables
Verify `.env` file has:
- [ ] DB_HOST
- [ ] DB_USER
- [ ] DB_PASSWORD
- [ ] DB_NAME
- [ ] SECRET_KEY

### 4. Start Backend
```bash
cd backend
python app.py
```

Should show:
```
✓ Database connected successfully
CivicTrack AI Backend Starting...
Running on: http://localhost:5000
```

## Frontend Setup

### 1. Verify New Files Exist
- [ ] frontend/resolver.html - Resolver dashboard
- [ ] frontend/js/resolver.js - Resolver JavaScript
- [ ] frontend/dashboard.html - Updated admin dashboard (no charts)
- [ ] frontend/js/dashboard.js - Updated admin JavaScript
- [ ] frontend/register.html - Has role selector

### 2. Verify Modified Files
- [ ] frontend/js/auth.js - Has resolver role handling
- [ ] frontend/js/register.js - Submits role to backend

### 3. Open Frontend
Simple HTTP server:
```bash
cd frontend
# Python 3
python -m http.server 8000
# Then visit: http://localhost:8000/index.html
```

Or use VS Code Live Server extension

## User Testing

### Create Test Users

#### 1. Admin User (if not exists)
- Register or create manually in database
- Email: admin@example.com
- Role: admin

```sql
-- Manual creation if needed
INSERT INTO users (name, email, password, role) 
VALUES ('Admin User', 'admin@example.com', 'hashed_password', 'admin');
```

#### 2. Resolver User
- Go to http://localhost:8000/register.html
- Name: John Resolver
- Email: resolver@example.com
- Password: test123
- Role: Resolver

#### 3. Citizen User
- Go to http://localhost:8000/register.html
- Name: Jane Citizen
- Email: citizen@example.com
- Password: test123
- Role: Citizen

## End-to-End Testing

### Test 1: Report an Issue (Citizen Flow)
1. [ ] Open http://localhost:8000/index.html
2. [ ] Click Register (if needed)
3. [ ] Go to http://localhost:8000/login.html
4. [ ] Login as citizen@example.com
5. [ ] You should be redirected to citizen.html
6. [ ] Fill in issue form (Title, Description, Coordinates)
7. [ ] Submit issue
8. [ ] Verify success message

### Test 2: Assign Issue (Admin Flow)
1. [ ] Login as admin@example.com
2. [ ] You should go to dashboard.html
3. [ ] Go to "Assign Work" tab
4. [ ] See the map with issue markers
5. [ ] See unassigned issue in table
6. [ ] Click "Assign" button
7. [ ] Select resolver from dropdown
8. [ ] Optionally check "Generate Google Maps Link"
9. [ ] Click "Assign"
10. [ ] Verify "Issue assigned successfully" message

### Test 3: Resolve Issue (Resolver Flow)
1. [ ] Login as resolver@example.com
2. [ ] You should go to resolver.html
3. [ ] See assigned issue in table
4. [ ] Click "View Map" to see location
5. [ ] See minimap with markers
6. [ ] Click "Open in Google Maps"
7. [ ] Google Maps should open in new tab with destination
8. [ ] Go back to resolver dashboard
9. [ ] Click "Mark Done" button
10. [ ] Add optional comments
11. [ ] Click "Mark Resolved"
12. [ ] Verify success message

### Test 4: Check Resolutions (Admin Flow)
1. [ ] Stay logged in as admin or login again
2. [ ] Go to "Resolutions" tab
3. [ ] Should see completed issue
4. [ ] Verify resolver name shows
5. [ ] Verify completion date shows
6. [ ] Verify comments display

## Troubleshooting

### Backend Won't Start
```
Error: Database connection error

Solution:
1. Verify MySQL is running
2. Check .env credentials
3. Ensure database exists: CREATE DATABASE civictrack_ai;
```

### Pages Not Loading
```
Error: Mixed Content (http/https conflict)

Solution:
1. Make sure backend runs on http://127.0.0.1:5000
2. Frontend can run on any localhost address
3. Check browser console for CORS errors
```

### Modifier Can't Be Assigned
```
Error: Resolver dropdown empty

Solution:
1. Verify resolver user exists in database
2. Check role is exactly "resolver" (case-sensitive)
3. Verify admin JWT token is valid
```

### Navigation Link Not Working
```
Error: Google Maps won't open

Solution:
1. Verify coordinates are valid (latitude -90 to 90, longitude -180 to 180)
2. Check internet connection
3. Try copying URL manually to browser
```

## Production Checklist

Before deploying to production:

- [ ] Migrate database on production server
- [ ] Update backend to use environment variables
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up proper CORS rules (not * for all)
- [ ] Implement rate limiting on API endpoints
- [ ] Add email notifications for assignments
- [ ] Set up monitoring and logging
- [ ] Test with production database
- [ ] Create backup strategy
- [ ] Document deployment process

## Quick Verification Commands

```bash
# 1. Test backend is running
curl http://127.0.0.1:5000/health

# 2. Test resolver endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:5000/resolvers

# 3. Check database connection
mysql -u user -p database -e "SELECT COUNT(*) FROM issues;"

# 4. Verify tables exist
mysql -u user -p database -e "SHOW TABLES LIKE 'issue_%';"
```

## Support & Documentation

For more details:
- Read WORK_ASSIGNMENT_GUIDE.md for feature overview
- Check backend/app.py for endpoint details
- Review database_migration.sql for schema changes
- Check frontend JavaScript files for implementation details

---
✓ Setup complete! Your CivicTrack AI Work Assignment system is ready to use.
