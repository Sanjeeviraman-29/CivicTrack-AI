# Image Verification Feature Implementation Guide

## Overview
This document explains the complete image verification workflow for the CivicTrack AI system. The feature allows resolvers to upload work completion photos, citizens to verify the quality of work, and admins to track verification status.

---

## Workflow Overview

### 1. Resolver Completes Work
- Resolver logs in to resolver.html
- Opens "Mark Done" in their assigned work
- **NEW**: Uploads a photo of completed work (required)
- Adds optional comments
- Submits completion with image
- Issue status changes to: **"Awaiting Verification"**
- System creates record in `issue_resolutions` table with image path

### 2. Citizen Verifies Work
- Citizen logs in to citizen.html
- Switches to "Verify Completions" tab
- Views pending verifications with:
  - Issue details
  - Completion photo from resolver
  - Resolver's comments
- **Can either:**
  - **Approve**: Issue marked as "Verified" and status becomes "Resolved"
  - **Reject**: Issue sent back to "In Progress" for resolver to redo

### 3. Admin Tracks Progress
- Admin views "Resolutions" tab in dashboard.html
- Sees all completed work with verification status:
  - **Pending**: Awaiting citizen approval
  - **Verified**: Citizen approved the work ✓
  - **Rejected**: Citizen rejected, resolver reworking
- Can view uploaded images by clicking "View" button

---

## Database Schema Changes

### New Columns Added to `issues` Table:
```sql
ALTER TABLE issues ADD COLUMN verification_status VARCHAR(50) DEFAULT 'Pending' AFTER resolved_at;
ALTER TABLE issues ADD COLUMN verified_by INT AFTER verification_status;
```

**Values for verification_status:**
- `Pending` - Waiting for citizen verification
- `Verified` - Citizen approved
- `Rejected` - Citizen rejected, needs rework

### New Columns Added to `issue_resolutions` Table:
```sql
ALTER TABLE issue_resolutions ADD COLUMN image_path VARCHAR(255) AFTER comments;
ALTER TABLE issue_resolutions ADD COLUMN verification_date TIMESTAMP AFTER image_path;
```

### New Table: `verification_history`
```sql
CREATE TABLE verification_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    verified_by INT NOT NULL,
    action VARCHAR(20) NOT NULL,  -- 'Approved' or 'Rejected'
    reason VARCHAR(255),
    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id),
    FOREIGN KEY (verified_by) REFERENCES users(id)
);
```

---

## Backend Endpoints

### 1. Upload Completion with Image
**Endpoint:** `POST /complete-issue-with-image`

**Required Authorization:** Resolver token

**Request Format:**
```
FormData:
- issue_id: integer
- image: binary file (JPG, PNG, GIF, WebP - max 5MB)
- comments: string (optional)
```

**Response:**
```json
{
    "message": "Issue completion uploaded. Awaiting citizen verification.",
    "image_path": "uploads/issue_1_20260302_125430_photo.jpg"
}
```

**What it does:**
- Saves image to `uploads/` folder with timestamp
- Updates issue status to "Awaiting Verification"
- Creates record in `issue_resolutions` table
- Records image path in database

---

### 2. Get Pending Verifications
**Endpoint:** `GET /pending-verifications`

**Required Authorization:** Citizen token

**Response:**
```json
[
    {
        "id": 1,
        "title": "Pothole on Main Street",
        "description": "Large pothole needs filling",
        "category": "Infrastructure",
        "severity": "High",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "status": "Awaiting Verification",
        "resolver_name": "John Resolver",
        "comments": "Pothole filled with asphalt",
        "image_path": "http://127.0.0.1:5000/uploads/issue_1_20260302_125430_photo.jpg",
        "resolution_date": "2026-03-02 12:54:30"
    }
]
```

---

### 3. Verify Issue (Approve)
**Endpoint:** `POST /verify-issue`

**Required Authorization:** Citizen token

**Request:**
```json
{
    "issue_id": 1
}
```

**Response:**
```json
{
    "message": "Issue verified successfully. Status updated to Resolved."
}
```

**What it does:**
- Updates `verification_status` to "Verified"
- Records who verified it in `verified_by`
- Issue officially marked as "Resolved"
- Creates audit trail in `verification_history`

---

### 4. Reject Issue
**Endpoint:** `POST /reject-issue`

**Required Authorization:** Citizen token

**Request:**
```json
{
    "issue_id": 1,
    "reason": "Work not completed properly, still visible damage"
}
```

**Response:**
```json
{
    "message": "Issue rejected. Resolver has been notified to re-do the work."
}
```

**What it does:**
- Reverts issue status back to "In Progress"
- Sets `verification_status` to "Rejected"
- Records rejection reason in `verification_history`
- Resolver can rework and resubmit

---

### 5. Get Resolved Issues (Admin)
**Endpoint:** `GET /resolved-issues`

**Required Authorization:** Admin token

**Response includes verification_status and image_path:**
```json
[
    {
        "id": 1,
        "title": "Pothole on Main Street",
        "category": "Infrastructure",
        "severity": "High",
        "resolved_by": "John Resolver",
        "resolution_date": "2026-03-02 12:54:30",
        "verification_status": "Verified",
        "image_path": "http://127.0.0.1:5000/uploads/issue_1_20260302_125430_photo.jpg"
    }
]
```

---

### 6. Serve Uploaded Images
**Endpoint:** `GET /uploads/<filename>`

**Purpose:** Allows serving images to frontend

**Usage in HTML:**
```html
<img src="http://127.0.0.1:5000/uploads/issue_1_20260302_125430_photo.jpg">
```

---

## Frontend Components

### Resolver Dashboard (resolver.html)

**New Features:**
- Image upload field in completion modal
- Image preview functionality
- File validation (size, type)
- Required field indicator

**Key Changes:**
```html
<input id="completionImage" type="file" accept="image/*">
<img id="imagePreview" src="" alt="Preview">
```

**JavaScript Functions:**
- `previewImage()` - Shows image preview
- `confirmCompletion()` - Uploads with FormData

---

### Citizen Dashboard (citizen.html)

**New Tab: "Verify Completions"**
- Lists issues awaiting verification
- Shows completion photo
- Shows resolver's notes
- Displays issue details

**Verification Modal Features:**
- Full-size image view
- Reason for rejection input (if rejecting)
- Approve/Reject buttons
- Issue details display

**New JavaScript Functions:**
- `switchTab()` - Tab navigation
- `loadPendingVerifications()` - Fetch pending items
- `openVerificationModal()` - Show verification dialog
- `approveVerification()` - Submit approval
- `rejectVerification()` - Submit rejection

---

### Admin Dashboard (dashboard.html)

**Resolutions Tab Updates:**
- Added "Verification Status" column
- Added "Image" column with view button
- status colors:
  - Blue: Pending verification
  - Green: Verified ✓
  - Red: Rejected ✗

**Updated columns:**
1. Title
2. Category
3. Severity
4. Resolved By
5. Date
6. **Verification Status** (NEW)
7. **Image** (NEW)

---

## Setup Instructions

### Step 1: Run Database Migration
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI
python add_image_verification.py
```

This script will:
- Add columns to `issues` and `issue_resolutions` tables
- Create `verification_history` table
- Create `uploads/` directory for image storage

### Step 2: Note Constraints
- **Max file size:** 5MB (set in app.py)
- **Allowed formats:** PNG, JPG, JPEG, GIF, WebP
- **Storage:** `uploads/` folder in backend directory
- **Filename format:** `issue_{id}_{timestamp}_{original_filename}`

### Step 3: Restart Backend
```bash
cd c:\Users\raman\Desktop\CivicTrack-AI\backend
python app.py
```

The backend will create the `uploads/` folder automatically if it doesn't exist.

### Step 4: Access the Features
- **Resolver:** Reports/resolver.html → "Mark Done" button
- **Citizen:** Reports/citizen.html → "Verify Completions" tab
- **Admin:** Reports/dashboard.html → "Resolutions" tab

---

## Test Workflow

### 1. Create Test Issue
- Login as citizen
- Report a new issue
- Note the issue ID

### 2. Admin Assign Work
- Login as admin
- View "Assign Work" tab
- Assign issue to resolver
- Click "Assign"

### 3. Resolver Complete with Image
- Login as resolver
- See assigned issue
- Click "Mark Done"
- Select image file
- Add comments
- Click "Submit for Verification"

### 4. Citizen Verify
- Login as citizen (issue creator)
- Go to "Verify Completions" tab
- See pending verification
- Review photo
- Click "Approve & Mark Resolved"

### 5. Admin Confirmation
- Login as admin
- Go to "Resolutions" tab
- See issue with "Verified" status
- Click "View" to see image

---

## Files Modified

### Backend
- `backend/app.py` - Added 5 new endpoints + file upload config

### Frontend
- `frontend/resolver.html` - Added image upload to completion modal
- `frontend/js/resolver.js` - Added image preview and upload logic
- `frontend/citizen.html` - Added verification tab and modal
- `frontend/js/citizen.js` - Added verification logic and tab switching
- `frontend/dashboard.html` - Updated resolutions table with verification column
- `frontend/js/dashboard.js` - Updated resolution display with verification status

### Database Setup
- `add_image_verification.py` - Migration script

---

## Error Handling

### Common Issues

**Image Upload Fails:**
- Check file size (max 5MB)
- Verify file format (PNG, JPG, GIF, WebP only)
- Ensure `uploads/` folder exists and is writable

**Cannot See Uploaded Image:**
- Backend must be running on port 5000
- Image path must start with "http://127.0.0.1:5000/uploads/"
- Check browser console for 404 errors

**Verification Fails:**
- Ensure user is the issue creator
- Check token is valid
- Verify database connection

**Image Path Null:**
- Resolver must upload image (required field)
- Check database `issue_resolutions.image_path` column exists

---

## Database Schema Summary

### Updated Issues Table
```
id (PK)
title
description
category
severity
latitude
longitude
created_by (FK)
status (ENUM)
created_at
updated_at
assigned_to (FK)
resolved_at
verification_status (NEW) ← Pending/Verified/Rejected
verified_by (NEW) ← User ID who verified
```

### Issue Resolutions Table
```
id (PK)
issue_id (FK)
resolved_by (FK)
comments
image_path (NEW) ← Path to uploaded image
verification_date (NEW) ← When verified
```

### Verification History Table (NEW)
```
id (PK)
issue_id (FK)
verified_by (FK)
action → Approved/Rejected
reason
verification_date
```

---

## Security Notes

1. **File Upload Security:**
   - Files validated by extension and mime type
   - Filenames sanitized with `secure_filename()`
   - Timestamp added to prevent filename conflicts
   - Max file size enforced (5MB)

2. **Authorization:**
   - Image upload restricted to assigned resolver
   - Verification restricted to issue creator (citizen)
   - Admin endpoints protected with @admin_required decorator

3. **Data Privacy:**
   - Images stored on server filesystem
   - File paths included in API responses
   - Browser can access via HTTP endpoint

---

## Performance Considerations

1. **Image Storage:**
   - Images stored in `uploads/` folder
   - Consider cleanup strategy for old images
   - Use CDN/object storage for production

2. **Database:**
   - Added indexes on frequently queried columns
   - `verification_history` table for audit trail
   - Consider archiving old resolutions

3. **Frontend:**
   - Image preview generated client-side
   - Auto-refresh every 30 seconds
   - Lazy load images in tables for better performance

---

## Future Enhancements

1. **Multiple Images:** Allow resolver to upload multiple photos
2. **Image Markup:** Citizens can mark issues on images
3. **Analytics:** Track verification rates and rejection reasons
4. **Notifications:** Email notifications for pending verifications
5. **Mobile App:** Native mobile apps for resolvers and citizens
6. **Cloud Storage:** Move images to AWS S3 or similar
7. **Image Processing:** Auto-rotate, compress, and validate images

---

## Support

For issues or questions:
1. Check browser console for errors
2. Review server logs: `python app.py` output
3. Verify database connection
4. Ensure CORS settings allow image requests
5. Check file permissions in `uploads/` folder

