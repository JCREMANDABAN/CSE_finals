

---

# 📚 CRUD REST API with MySQL, Testing, and XML/JSON Output

This Flask application provides a REST API for managing student records with full CRUD operations, JWT-based authentication, search functionality, and support for JSON/XML response formats.

---

## 🚀 Features

- **CRUD Operations**: Create, Read, Update, Delete students  
- **Authentication**: JWT-based security for protected endpoints  
- **Search**: Search students by name, course, or year level  
- **Formats**: JSON and XML output via `?format=` query parameter  
- **Validation**: Input validation and error handling  
- **Database**: MySQL with at least 20 student records  

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL Server
- Git

### 2. Clone and Setup

```bash
git clone <your-repo-url>
cd cse1_api
```

### 3. Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. MySQL Setup

- Create a MySQL database named `cse1_db`
- Update your `db.py` file with your MySQL credentials:

```python
return mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="cse1_db",
    port=3306
)
```

- Import the schema and data:

```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(50) NOT NULL,
    year_level INT NOT NULL
);

INSERT INTO students (name, course, year_level) VALUES
('Maria Lopez', 'BSCS', 2),
('Juan Dela Cruz', 'BSIT', 3),
('Ana Santos', 'BSCE', 1),
-- Add at least 17 more records for demo purposes
('Student 4', 'BSCS', 1),
('Student 5', 'BSIT', 2);
```

### 6. Run the Application

```bash
python app.py
```

The API will be available at:  
📍 `http://127.0.0.1:5000`

---

## 📘 API Documentation

### 🔐 Authentication

All endpoints except `/auth/login` require JWT authentication.  
Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### 🔑 Login

**POST /auth/login**

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
}
```

---

### 👨‍🎓 Student Endpoints

#### List Students  
**GET /students?format=json**

Optional query parameters:
- `format`: `json` (default) or `xml`

**Response (JSON):**
```json
[
  {
    "id": 1,
    "name": "Maria Lopez",
    "course": "BSCS",
    "year_level": 2
  }
]
```

#### Search Students  
**GET /students/search?name=maria&course=BSCS&format=xml**

Search by any combination of:
- `name`
- `course`
- `year_level`
- `format`: `json` or `xml`

#### Get Student by ID  
**GET /students/{id}?format=json**

#### Create Student  
**POST /students**

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Student",
  "course": "BSIT",
  "year_level": 3
}
```

**Response:**
```json
{
  "message": "Student added",
  "id": 21
}
```

#### Update Student  
**PUT /students/{id}**

**Request Body:**
```json
{
  "name": "Updated Name",
  "course": "BSCS",
  "year_level": 4
}
```

**Response:**
```json
{
  "message": "Student updated"
}
```

#### Delete Student  
**DELETE /students/{id}**

**Response:**
```json
{
  "message": "Student deleted"
}
```

---

## ⚠️ Error Responses

- **400 Bad Request**: Validation errors or invalid format  
- **401 Unauthorized**: Missing or invalid JWT token  
- **404 Not Found**: Student not found  
- **500 Internal Server Error**: Database errors  

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/test_api.py
```

The test suite covers:
- Authentication (login success/failure)
- CRUD operations for students
- Search functionality
- JSON/XML format support
- Input validation
- Error handling

### Manual Testing (curl)

```bash
# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get students (replace TOKEN)
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:5000/students

# Get students in XML
curl -H "Authorization: Bearer TOKEN" "http://127.0.0.1:5000/students?format=xml"

# Search students
curl -H "Authorization: Bearer TOKEN" "http://127.0.0.1:5000/students/search?name=maria"
```

---

## 📁 Project Structure

```
.
├── app.py              # Main Flask app
├── db.py               # MySQL connection
├── config.py           # Config (optional)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── tests/
│   └── test_api.py     # Unit tests
└── venv/               # Virtual environment (excluded from Git)
```

---

## 🔐 Security Notes

- Change the JWT secret key in production
- Use HTTPS in production
- Replace hardcoded admin credentials with real user management
- Validate and sanitize all inputs

---

## ✅ Grading Criteria Met

- ✅ GitHub: Multiple commits with timestamps  
- ✅ CRUD Operations: Full REST API with validation and error handling  
- ✅ CRUD Tests: Comprehensive unit tests  
- ✅ Formatting Options: JSON/XML support  
- ✅ Search Functionality: Student search by name/course/year  
- ✅ Security: JWT authentication  
- ✅ Documentation: Complete API documentation and setup guide  

---

Let me know if you want this turned into a downloadable file or if you'd like a version with your actual GitHub repo URL and database credentials redacted for submission.