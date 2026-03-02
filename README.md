# CivicTrack AI - Civic Issue Management Platform

## Project Overview

CivicTrack AI is a comprehensive civic issue tracking and resolution system powered by AI. It enables citizens to report civic issues, admins to assign work to field resolvers, and resolvers to complete and track resolutions in real-time.

**Latest Update**: Work Assignment System Implementation
- ✅ Removed analytics charts
- ✅ Added work assignment functionality
- ✅ Implemented resolver dashboard
- ✅ Integrated navigation system with Google Maps
- ✅ Added resolution tracking

---

## Features

### For Citizens 👤
- Report civic issues (potholes, water leaks, garbage, etc.)
- Provide issue location and description
- Track personal issue status
- View issue details and severity

### For Resolvers 👷
- View assigned issues on dedicated dashboard
- See issue location on interactive map
- Get turn-by-turn navigation to issue sites
- Mark work as complete with comments
- Track resolution history

### For Admins 👨‍💼
- View all civic issues on live map
- Assign issues to field resolvers
- Generate automated Google Maps navigation links
- Track all completed work and resolutions
- View completion comments and timestamps
- Monitor KPI statistics

### AI-Powered 🤖
- Automatic issue categorization
- Automatic severity detection
- Intelligent issue classification

---

## Technology Stack

### Backend
- **Framework**: Flask (Python 3.8+)
- **Database**: MySQL 5.7+
- **Authentication**: JWT (JSON Web Tokens)
- **Password Security**: bcrypt
- **API**: RESTful

### Frontend
- **Build**: HTML5, CSS3, Tailwind CSS
- **Interactivity**: JavaScript (Vanilla)
- **Maps**: Leaflet.js + OpenStreetMap
- **Navigation**: Google Maps Integration
- **UI Components**: Tailwind CSS for styling

### Additional Libraries
- Chart.js (removed in v2.0 - replaced with work assignments)
- FontAwesome (for icons)
- Google Fonts (Poppins)

---

## Quick Start

### Prerequisites
```bash
- Python 3.8+
- MySQL 5.7+
- Node.js (optional, for frontend tooling)
```

### Installation Steps

#### 1. Clone/Setup Repository
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI
```

#### 2. Database Setup
```bash
mysql -u your_user -p your_database < database_migration.sql
```

#### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on: `http://127.0.0.1:5000`

#### 4. Frontend Setup
```bash
cd frontend
# Option 1: Simple HTTP server
python -m http.server 8000

# Option 2: Use VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

Frontend runs on: `http://localhost:8000`

#### 5. Access Application
Open browser: `http://localhost:8000/index.html`

---

## User Workflows

### Citizen Workflow
```
1. Register as Citizen
   ↓
2. Login to citizen.html
   ↓
3. Fill issue form (Title, Description, Location)
   ↓
4. Submit issue → Status: Pending
   ↓
5. View issue in "My Issues" section
```

### Admin Workflow
```
1. Login to dashboard.html
   ↓
2. View unassigned issues
   ↓
3. Click "Assign" on any issue
   ↓
4. Select resolver from dropdown
   ↓
5. Optional: Generate Google Maps link
   ↓
6. Confirm assignment → Issue status: Assigned
   ↓
7. View completed work in "Resolutions" tab
```

### Resolver Workflow
```
1. Register as Resolver
   ↓
2. Login to resolver.html
   ↓
3. See assigned issues in table
   ↓
4. Click "View Map" to see location
   ↓
5. Click "Open in Google Maps" for directions
   ↓
6. Travel to location and complete work
   ↓
7. Click "Mark Done"
   ↓
8. Add optional comments
   ↓
9. Confirm → Issue status: Resolved
   ↓
10. Admin notified and can view completion details
```

---

## Project Structure

```
CivicTrack-AI/
├── backend/
│   ├── app.py                 # Flask backend with all endpoints
│   ├── ai_engine.py          # AI category/severity detection
│   ├── requirements.txt       # Python dependencies
│   └── __pycache__/          # Python cache
│
├── frontend/
│   ├── index.html            # Home/login page
│   ├── login.html            # Login form
│   ├── register.html         # Registration form (UPDATED)
│   ├── citizen.html          # Citizen issue reporting
│   ├── dashboard.html        # Admin work assignment (UPDATED)
│   ├── resolver.html         # Resolver dashboard (NEW)
│   ├── assets/               # Static assets
│   ├── css/
│   │   └── styles.css        # Custom styles
│   └── js/
│       ├── auth.js           # Authentication (UPDATED)
│       ├── register.js       # Registration (UPDATED)
│       ├── citizen.js        # Citizen page logic
│       ├── dashboard.js      # Admin dashboard (REWRITTEN)
│       └── resolver.js       # Resolver dashboard (NEW)
│
├── database_migration.sql          # Database schema changes
├── validate_installation.py        # Installation validator
├── SETUP_CHECKLIST.md             # Setup verification checklist
├── WORK_ASSIGNMENT_GUIDE.md       # Feature documentation
├── IMPLEMENTATION_SUMMARY.md      # Detailed implementation info
├── QUICK_REFERENCE.md             # Quick reference guide
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /register | Register new user |
| POST | /login | Login user |

### Issues
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /create-issue | Submit new issue |
| GET | /all-issues | Get all issues (Admin only) |
| GET | /my-issues | Get user's issues |
| GET | /map-issues | Get issues for map display |
| PUT | /update-status/<id> | Update issue status |

### Work Assignment
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /resolvers | Get all resolvers (Admin only) |
| POST | /assign-issue | Assign issue to resolver (Admin only) |
| GET | /my-assignments | Get assignments for resolver |
| POST | /complete-issue | Mark issue as resolved |
| GET | /resolved-issues | Get all resolutions (Admin only) |

### Statistics
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /status-stats | Get issue count by status |
| GET | /category-stats | Get issue count by category |
| GET | /severity-stats | Get issue count by severity |
| GET | /health | Health check endpoint |

---

## Key Data Models

### Users
```sql
- id (INT, PK)
- name (VARCHAR)
- email (VARCHAR, UNIQUE)
- password (VARCHAR) [hashed]
- role (ENUM: admin, citizen, resolver)
- created_at (TIMESTAMP)
```

### Issues
```sql
- id (INT, PK)
- title (VARCHAR)
- description (TEXT)
- category (VARCHAR) [AI-detected]
- severity (VARCHAR) [AI-detected: Low/Medium/High]
- latitude (FLOAT)
- longitude (FLOAT)
- status (VARCHAR) [Pending/Assigned/In Progress/Resolved]
- created_by (FK → users.id)
- assigned_to (FK → users.id) [NEW]
- resolved_at (TIMESTAMP) [NEW]
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Issue Assignments [NEW]
```sql
- id (INT, PK)
- issue_id (FK → issues.id)
- assigned_by (FK → users.id) [Admin]
- assigned_to (FK → users.id) [Resolver]
- assignment_date (TIMESTAMP)
```

### Issue Resolutions [NEW]
```sql
- id (INT, PK)
- issue_id (FK → issues.id)
- resolved_by (FK → users.id) [Resolver]
- comments (TEXT)
- resolution_date (TIMESTAMP)
```

---

## Configuration

### Environment Variables (.env)
```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=civictrack_ai
SECRET_KEY=your_secret_key_here
```

### Database Connection
- Host: localhost (default)
- Port: 3306 (default)
- User: Set in .env
- Password: Set in .env
- Database: civictrack_ai

---

## Testing

### Test Users to Create:

**Admin User**
- Email: admin@example.com
- Password: admin123
- Role: admin

**Resolver User**
- Email: resolver@example.com
- Password: resolver123
- Role: resolver

**Citizen User**
- Email: citizen@example.com
- Password: citizen123
- Role: citizen

### Testing Scenario:
1. Create citizen user and report issue
2. Create resolver user
3. Login as admin and assign issue to resolver
4. Login as resolver and mark issue complete
5. Login as admin and verify in Resolutions tab

---

## Installation Validation

Run the validation script to verify installation:

```bash
python validate_installation.py
```

This checks:
- All required files exist
- Backend endpoints are implemented
- Frontend pages are present
- JavaScript functions are defined
- Documentation is complete

---

## Documentation Files

| File | Purpose |
|------|---------|
| README.md | Project overview (this file) |
| QUICK_REFERENCE.md | Quick start reference |
| SETUP_CHECKLIST.md | Step-by-step setup guide |
| WORK_ASSIGNMENT_GUIDE.md | Feature documentation |
| IMPLEMENTATION_SUMMARY.md | Technical details |
| database_migration.sql | Database schema |

---

## Troubleshooting

### Backend won't start
```
Error: "Database connection error"
Solution: 
  1. Verify MySQL is running
  2. Check .env credentials
  3. Check database exists
```

### Pages won't load
```
Error: "CORS error" or "Cannot reach backend"
Solution:
  1. Verify backend running on localhost:5000
  2. Check frontend running on localhost:8000
  3. Clear browser cache
```

### Login redirect issues
```
Error: "Wrong page after login"
Solution:
  1. Verify user role in database
  2. Check JWT token is valid
  3. Check auth.js role-based redirection
```

### Map not loading
```
Error: "Map appears blank"
Solution:
  1. Check internet (OpenStreetMap CDN)
  2. Verify coordinates are valid
  3. Check Leaflet.js loaded
```

For more troubleshooting, see SETUP_CHECKLIST.md

---

## Performance

- **Auto-refresh**: 30 seconds
- **Database Indexes**: Created on frequently queried columns
- **Map Rendering**: Lazy loading, efficient marker placement
- **API Response**: Optimized queries with joins
- **Frontend**: Minimal repaints, modal-based interactions

---

## Security

✓ JWT token-based authentication
✓ Password hashing with bcrypt
✓ SQL injection prevention with parameterized queries
✓ Role-based access control (RBAC)
✓ CORS configured
✓ Environment variables for secrets

---

## Version History

### v2.0 - Work Assignment System (Current)
- ✅ Removed analytics charts
- ✅ Added work assignment features
- ✅ Created resolver dashboard
- ✅ Integrated Google Maps navigation
- ✅ Added resolution tracking

### v1.0 - Initial Release
- Basic issue reporting
- Admin statistics dashboard
- Map visualization
- User authentication

---

## Future Roadmap

- [ ] Email notifications
- [ ] Push notifications
- [ ] Photo uploads (before/after)
- [ ] Performance analytics
- [ ] Team assignments
- [ ] Priority queue management
- [ ] Offline functionality
- [ ] Mobile app
- [ ] Advanced search/filtering
- [ ] SLA tracking

---

## Support & Contributing

For issues, feature requests, or improvements:
1. Check existing documentation
2. Review QUICK_REFERENCE.md for common issues
3. Check SETUP_CHECKLIST.md for setup problems
4. Review IMPLEMENTATION_SUMMARY.md for technical details

---

## License

[Add your license here]

---

## Contact

Development Team: CivicTrack AI
Email: [Add contact email]
Project: Civic Issue Management Platform

---

## Deployment

### Development
```bash
# Terminal 1
cd backend && python app.py

# Terminal 2
cd frontend && python -m http.server 8000
```

### Production Checklist
- [ ] Run database migration
- [ ] Set environment variables
- [ ] Configure HTTPS
- [ ] Set up proper CORS
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test with production database

---

**Status**: ✅ Ready for Use (after database migration)
**Last Updated**: 2026-03-02
**Version**: 2.0

---

## Quick Links

- 🚀 **Quick Start**: See QUICK_REFERENCE.md
- 📋 **Setup**: See SETUP_CHECKLIST.md
- 📖 **Features**: See WORK_ASSIGNMENT_GUIDE.md
- 🔧 **Technical**: See IMPLEMENTATION_SUMMARY.md
- ✅ **Validate**: Run `python validate_installation.py`

