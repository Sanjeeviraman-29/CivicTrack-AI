# CivicTrack AI - Image Verification Feature Setup & Testing

## Feature Summary

The image verification system allows:
1. **Resolvers** to upload photos of completed work
2. **Citizens** to review and approve/reject the work
3. **Admins** to track verification status of all completions

---

## Complete Workflow

### System Architecture
```
Resolver completes work + uploads image
    ↓
[Issue Status: "Awaiting Verification"]
    ↓
Citizen reviews photo and verification details
    ↓
    ├─→ APPROVE: Status → "Resolved" & Verification Status → "Verified" ✓
    └─→ REJECT: Status → "In Progress" & Verification Status → "Rejected" ✗
    
Admin Dashboard shows all completions with verification status
```

---

## Database Setup (IMPORTANT - DO THIS FIRST)

### Option 1: Use MySQL Workbench (Recommended)
1. Open MySQL Workbench
2. Connect to your database
3. Open `image_verification_migration.sql` file
4. Execute the SQL script (Ctrl+Shift+Enter)
5. Verify: Check that new columns exist in `issues` and `issue_resolutions` tables

### Option 2: Command Line
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI
mysql -u root -p civictrack_ai < image_verification_migration.sql
# When prompted, enter password: San@29805
```

### Option 3: Python Script (If MySQL available)
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI
python add_image_verification.py
```

### Verify Migration Succeeded
Run this query in MySQL:
```sql
SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'issues' AND COLUMN_NAME IN ('verification_status', 'verified_by');
```

Should return 2 rows confirming columns were added.

---

## Starting the System

### 1. Start Backend Server
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI\backend
python app.py
```
✓ Should see: "Database connected successfully" and "Running on: http://localhost:5000"

### 2. Start Frontend Server (in another terminal)
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI\frontend
python -m http.server 8000
```
✓ Should see: "Serving HTTP on 0.0.0.0 port 8000"

### 3. Access in Browser
- **Citizen**: http://localhost:8000/citizen.html
- **Resolver**: http://localhost:8000/resolver.html
- **Admin**: http://localhost:8000/dashboard.html

---

## Testing the Complete Workflow

### Test Users (Already Created)
| Email | Password | Role |
|-------|----------|------|
| user@gmail.com | user123 | Citizen |
| resolver@example.com | resolver123 | Resolver |
| admin@gmail.com | admin123 | Admin |

### Step-by-Step Test

#### Step 1: Create an Issue (as Citizen)
1. Open http://localhost:8000/citizen.html
2. Login: `user@gmail.com` / `user123`
3. Submit an issue:
   - Title: "Test Pothole"
   - Description: "Pothole on Main St"
   - Latitude: 13.0827
   - Longitude: 80.2707
4. Click "Submit Complaint"
5. Note the issue details (you'll need to identify it)

#### Step 2: Assign Issue (as Admin)
1. Open http://localhost:8000/dashboard.html
2. Login: `admin@gmail.com` / `admin123`
3. Click "Assign Work" tab
4. Find "Test Pothole" in the table
5. Click "Assign" button
6. Select "John Resolver" from dropdown
7. Click "Assign"
8. Issue now shows as "In Progress" (status updated)

#### Step 3: Complete with Image (as Resolver)
1. Open http://localhost:8000/resolver.html
2. Login: `resolver@example.com` / `resolver123`
3. Find "Test Pothole" in "My Work Assignments"
4. Click "Mark Done" button
5. **NEW FEATURE**: Upload an image:
   - Click "Choose Image"
   - Select a JPG/PNG file from your computer
   - See preview of image
6. Add comments: "Pothole filled with asphalt"
7. Click "Submit for Verification"
8. ✓ Should see: "Work completion uploaded. Awaiting citizen verification..."

#### Step 4: Verify Completion (as Citizen)
1. Open http://localhost:8000/citizen.html
2. Login: `user@gmail.com` / `user123` (issue creator)
3. Click "Verify Completions" tab
4. See "Test Pothole" card with:
   - Work photo (uploaded by resolver)
   - Resolver's comments
5. Click "Review & Verify" button
6. Modal opens showing:
   - Full-size image
   - Issue details
   - Resolver's notes
   - You can:
     - ✓ "Approve & Mark Resolved" → Work accepted
     - ✗ "Reject & Ask to Redo" → Return to resolver (requires reason)
7. Click "Approve & Mark Resolved"
8. ✓ Should see: "✓ Work approved! Issue marked as Resolved."

#### Step 5: Check Admin Dashboard
1. Open http://localhost:8000/dashboard.html
2. Login: `admin@gmail.com` / `admin123`
3. Click "Resolutions" tab
4. See "Test Pothole" with:
   - **Verification Status**: "Verified" (green badge)
   - **Image** column with "View" button
5. Click "View" to see the resolution photo

#### Step 6: Test Rejection Workflow (Optional)
1. Create another issue and repeat steps 1-3
2. In Step 4, instead of approving:
3. Enter rejection reason: "Work not visible in photo"
4. Click "Reject & Ask to Redo"
5. ✓ Issue returns to "In Progress" status
6. Verification Status shows "Rejected"
7. Resolver can see it again and resubmit

---

## New Endpoints Created

### POST /complete-issue-with-image
**Upload work completion with image**
- **Body**: FormData with issue_id, image file, comments
- **Auth**: Resolver token required
- **Response**: Success message + image path

### GET /pending-verifications
**Get all issues awaiting citizen verification**
- **Auth**: Citizen token required
- **Response**: Array of issues awaiting verification

### POST /verify-issue
**Citizen approves completed work**
- **Body**: `{issue_id: number}`
- **Auth**: Citizen token required
- **Response**: Success message

### POST /reject-issue
**Citizen rejects completed work**
- **Body**: `{issue_id: number, reason: string}`
- **Auth**: Citizen token required
- **Response**: Success message

### GET /resolved-issues (Updated)
**Get all resolved issues with verification status**
- **Auth**: Admin token required
- **Response**: Includes verification_status and image_path

### GET /uploads/<filename>
**Serve uploaded images**
- **Auth**: Not required
- **Response**: Image file binary

---

## File Upload Specifications

### Constraints
- **Max File Size**: 5 MB
- **Allowed Formats**: PNG, JPG, JPEG, GIF, WebP
- **Storage Location**: `./uploads/` folder in backend directory
- **File Naming**: `issue_{id}_{timestamp}_{original_name}`

### Example
```
Original upload: IMG_1234.jpg
Saved as: uploads/issue_1_20260302_133452_IMG_1234.jpg
Served at: http://127.0.0.1:5000/uploads/issue_1_20260302_133452_IMG_1234.jpg
```

---

## Files Modified/Created

### Backend
- ✅ `backend/app.py` - Added 5 new endpoints
  - `POST /complete-issue-with-image` - Upload with image
  - `GET /pending-verifications` - Citizen pending list
  - `POST /verify-issue` - Approve work
  - `POST /reject-issue` - Reject work
  - `GET /resolved-issues` (updated) - Include verification status
  - `GET /uploads/<filename>` - Serve images

### Frontend
- ✅ `frontend/resolver.html` - Added image upload to modal
  - File input with preview
  - Drag-and-drop support ready
  - Required field indicator

- ✅ `frontend/js/resolver.js` - Image upload logic
  - `previewImage()` - Show preview
  - Updated `confirmCompletion()` - Use FormData for upload

- ✅ `frontend/citizen.html` - Added verification tab
  - "Verify Completions" tab
  - Verification modal with image display
  - Approve/Reject buttons

- ✅ `frontend/js/citizen.js` - Verification logic
  - `switchTab()` - Tab navigation
  - `loadPendingVerifications()` - Get pending items
  - `openVerificationModal()` - Show modal
  - `approveVerification()` - Submit approval
  - `rejectVerification()` - Submit rejection

- ✅ `frontend/dashboard.html` - Updated resolutions table
  - Added "Verification Status" column
  - Added "Image" column

- ✅ `frontend/js/dashboard.js` - Updated resolution display
  - Show verification status with color badges
  - View button for images
  - Updated column count (now 7 columns)

### Database
- ✅ `image_verification_migration.sql` - Create tables/columns
- ✅ `add_image_verification.py` - Python migration script

### Documentation
- ✅ `IMAGE_VERIFICATION_GUIDE.md` - Complete feature documentation
- ✅ `IMAGE_VERIFICATION_SETUP.md` - This file

---

## Troubleshooting

### Issue: "No image selected" error
**Solution**: Image upload field is required. Click "Choose Image" and select a file.

### Issue: "File type not allowed"
**Solution**: Only PNG, JPG, JPEG, GIF, WebP allowed. Ensure file has correct extension.

### Issue: "File size exceeds 5MB limit"
**Solution**: Image file is too large. Compress the image to under 5MB.

### Issue: Image won't display in verification modal
**Troubleshooting**:
1. Check backend is running on port 5000
2. Check browser console for 404 errors
3. Verify image path in database starts with "http://127.0.0.1:5000/"
4. Check `uploads/` folder exists in backend directory

### Issue: "Unauthorized" when verifying
**Solution**: Must login as the original issue creator (citizen). Other citizens cannot verify issues they didn't report.

### Issue: Pending verifications doesn't show issues
**Solution**:
1. Ensure resolver has uploaded image (check database)
2. Verify issue status is "Awaiting Verification"
3. Check you're logged in as issue creator
4. Try refreshing page (auto-refresh every 30 seconds)

### Issue: Backend won't start with image endpoints
**Solution**:
1. Check Python version (3.8+ required)
2. Ensure `werkzeug` is installed: `pip install werkzeug`
3. Check for syntax errors: `python -m py_compile app.py`

---

## Testing All Features

### Feature Checklist
- [ ] Image upload from resolver (with preview)
- [ ] Image storage in uploads folder
- [ ] Image path saved to database
- [ ] Citizen sees pending verification
- [ ] Citizen can view image
- [ ] Citizen can approve (issue marked Resolved/Verified)
- [ ] Citizen can reject (issue back to In Progress/Rejected)
- [ ] Admin sees verification status
- [ ] Admin can view images
- [ ] Rejection reason stored in database
- [ ] Audit trail created in verification_history

### API Test Endpoint
For testing API endpoints, you can use:
- Browser Developer Tools → Network tab
- Postman application
- curl commands
- The `tester.html` file if available

Example curl test (after login):
```bash
# 1. Get token from login
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@gmail.com","password":"user123"}'

# 2. Get pending verifications
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:5000/pending-verifications
```

---

## Database Verification

### Check Schema Changes
```sql
-- Show new columns in issues table
DESCRIBE issues;
-- Should show: verification_status, verified_by

-- Show new columns in issue_resolutions table
DESCRIBE issue_resolutions;
-- Should show: image_path, verification_date

-- Check verification_history table exists
DESCRIBE verification_history;
-- Should show: id, issue_id, verified_by, action, reason, verification_date
```

### Check Data
```sql
-- View a resolution with image
SELECT i.title, ir.image_path, i.verification_status, i.verified_by
FROM issues i
LEFT JOIN issue_resolutions ir ON i.id = ir.issue_id
WHERE ir.image_path IS NOT NULL;

-- View verification history
SELECT * FROM verification_history;
```

---

## Performance Notes

1. **Image Storage**: 
   - Images stored in `uploads/` folder
   - For production, consider AWS S3 or similar
   - Implement cleanup for old images

2. **Database**:
   - Indexes added on `verification_status` and `verified_by`
   - Consider archiving old records regularly
   - Query optimization for large datasets

3. **Frontend**:
   - Images preview generated client-side
   - 30-second auto-refresh for real-time updates
   - Lazy load images in tables for better performance

---

## Next Steps (Optional Enhancements)

1. **Multiple Images**: Allow uploading 2-3 photos per completion
2. **Image Annotations**: Citizens can mark issues on photos
3. **Auto-Rotate**: Fix EXIF rotation automatically
4. **Image Compression**: Compress on upload to reduce storage
5. **Cloud Storage**: Move to AWS S3 or Google Cloud Storage
6. **Email Notifications**: Notify citizens of new verifications
7. **Mobile App**: Native apps for resolvers and citizens
8. **Video Support**: Allow short video clips of work
9. **OCR**: Extract text from images (before/after signs, dates, etc.)
10. **Analytics**: Dashboard showing rejection rates, popular issues, etc.

---

## Support & Documentation

For complete documentation, see:
- `IMAGE_VERIFICATION_GUIDE.md` - Full technical documentation
- `backend/app.py` - Source code with comments
- Browser console (F12) for debugging errors

---

## Quick Start Summary

1. **Setup Database**: Run `image_verification_migration.sql`
2. **Start Backend**: `python app.py` (from backend folder)
3. **Start Frontend**: `python -m http.server 8000` (from frontend folder)
4. **Test Flow**:
   - Create issue (citizen)
   - Assign work (admin)
   - Upload photo (resolver)
   - Verify photo (citizen)
   - Check status (admin)
5. **Done!** ✓

---

*Last Updated: March 2, 2026*
*CivicTrack AI - Image Verification Feature v1.0*
