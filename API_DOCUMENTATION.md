# Zzzuper PDF - API Documentation

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. GET /
**Description:** Load main application page

**Response:** HTML page with UI

**Example:**
```bash
curl http://localhost:5000
```

---

### 2. GET /api/files
**Description:** Get list of files in current session

**Response:**
```json
[
    {
        "id": 0,
        "name": "document.pdf",
        "path": "uploads/1234567890_document.pdf",
        "type": "pdf"
    },
    {
        "id": 1,
        "name": "image.jpg",
        "path": "uploads/1234567891_image.jpg",
        "type": "image"
    }
]
```

**Example:**
```bash
curl http://localhost:5000/api/files
```

---

### 3. POST /api/upload
**Description:** Upload one or multiple files

**Parameters:**
- `files` (FormData) - Multiple file input

**Response:**
```json
{
    "success": true,
    "added": [
        {"name": "file1.pdf", "type": "pdf"},
        {"name": "file2.jpg", "type": "image"}
    ],
    "total": 2
}
```

**Example:**
```bash
curl -X POST \
  -F "files=@file1.pdf" \
  -F "files=@file2.jpg" \
  http://localhost:5000/api/upload
```

---

### 4. GET /api/preview/<file_id>
**Description:** Get preview image of a file

**Parameters:**
- `file_id` (URL parameter) - Index of file in list (0-based)
- `page` (query parameter, optional) - Page number for PDF (1-based)

**Response for PDF:**
```json
{
    "type": "pdf",
    "page": 1,
    "total_pages": 5,
    "image": "data:image/png;base64,..."
}
```

**Response for Image:**
```json
{
    "type": "image",
    "width": 800,
    "height": 600,
    "image": "data:image/png;base64,..."
}
```

**Example:**
```bash
# Get preview of first file, page 2
curl "http://localhost:5000/api/preview/0?page=2"
```

---

### 5. POST /api/remove/<file_id>
**Description:** Remove a file from the list

**Parameters:**
- `file_id` (URL parameter) - Index of file to remove

**Response:**
```json
{
    "success": true
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/remove/0
```

---

### 6. POST /api/clear
**Description:** Clear all files from the list

**Response:**
```json
{
    "success": true
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/clear
```

---

### 7. POST /api/move
**Description:** Move a file up or down in the list

**Request Body:**
```json
{
    "file_id": 0,
    "direction": "up"
}
```

**Parameters:**
- `direction`: "up" or "down"

**Response:**
```json
{
    "success": true
}
```

**Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_id": 2, "direction": "up"}' \
  http://localhost:5000/api/move
```

---

### 8. POST /api/merge
**Description:** Merge all files into a single PDF and download

**Response:**
- Binary PDF file download

**Example:**
```bash
curl -X POST http://localhost:5000/api/merge > output.pdf
```

---

### 9. POST /api/rotate
**Description:** Store rotation preference for a file (client-side only)

**Request Body:**
```json
{
    "file_id": 0,
    "angle": 90
}
```

**Parameters:**
- `angle`: 0, 90, 180, or 270

**Response:**
```json
{
    "success": true
}
```

**Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_id": 0, "angle": 90}' \
  http://localhost:5000/api/rotate
```

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (missing parameters) |
| 500 | Server Error |

---

## Content Types

### Request
- `multipart/form-data` - For file uploads
- `application/json` - For JSON payloads

### Response
- `application/json` - JSON responses
- `application/pdf` - PDF file downloads
- `image/png` - Preview images

---

## Session Management

Files are stored in Flask session, which means:
- Each browser session has its own file list
- Files are lost when browser session ends
- Refresh page will clear the file list
- Actual file uploads are stored in `uploads/` folder

---

## Error Handling

All API errors return JSON response:

```json
{
    "error": "Error message description"
}
```

---

## File Size Limits

- **Per File**: 500MB
- **Total Server**: Unlimited (depends on disk space)

---

## Supported File Types

| Type | Extensions |
|------|-----------|
| PDF | .pdf |
| Image | .jpg, .jpeg, .png |

---

## Example: Complete Workflow

```bash
# 1. Upload files
curl -X POST \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  http://localhost:5000/api/upload

# 2. Get file list
curl http://localhost:5000/api/files

# 3. Preview first file
curl "http://localhost:5000/api/preview/0"

# 4. Move second file up
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_id": 1, "direction": "up"}' \
  http://localhost:5000/api/move

# 5. Merge all and download
curl -X POST http://localhost:5000/api/merge > result.pdf

# 6. Clear all files
curl -X POST http://localhost:5000/api/clear
```

---

## CORS & Security Notes

- Application uses Flask sessions (secure cookies)
- CSRF protection should be enabled in production
- All filenames are sanitized to prevent path traversal
- Files are stored with timestamp to avoid conflicts

---

## Development Notes

### Adding New Endpoints
1. Create function in `app.py`
2. Decorate with `@app.route('/api/endpoint', methods=['GET', 'POST'])`
3. Return JSON with `jsonify()`
4. Update this documentation

### Testing with curl
```bash
# Enable verbose output for debugging
curl -v http://localhost:5000/api/files

# Show response headers only
curl -i http://localhost:5000/api/files

# POST with data
curl -X POST -d "data=value" http://localhost:5000/api/endpoint
```

---

Last Updated: December 2024
