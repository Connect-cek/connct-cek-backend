# Connect-CEK Backend API Documentation

This is a comprehensive API documentation for the Connect-CEK platform backend.

## Base URL
- Development: `http://localhost:8000`
- Production: [To be determined]

## Authentication

### OTP Authentication Flow
1. Request OTP via email
2. Validate OTP to get access token
3. Use access token for subsequent API calls

### Endpoints

#### Request OTP
```
POST /auth/send-otp
```
**Request Body:**
```json
{
  "email": "user@example.com"
}
```
**Response:**
```json
{
  "message": "OTP sent successfully",
  "expires_at": "2025-03-11T23:10:00"
}
```

#### Verify OTP
```
POST /auth/verify-otp
```
**Request Body:**
```json
{
  "email": "user@example.com",
  "otp_code": "123456"
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_exists": true,
  "user_status": "active"
}
```

## User Management

### Registration

#### Register New User
```
POST /users/register
```
**Form Data:**
- `name`: String (required)
- `email`: String (required)
- `role`: String (required) - One of: student, alumni, mentor, admin
- `institution_id`: Integer (required)
- `year_of_study`: String (optional)
- `course`: String (optional)
- `fields_of_interest`: String (optional, JSON array or comma-separated string)
- `profile_photo`: File (optional)
- `resume`: File (optional)

**Response:**
```json
{
  "message": "User registered successfully and awaiting approval",
  "user_id": 123
}
```

### Profile Management

#### Get Current User Profile
```
GET /users/profile
```
**Headers:** Authorization: Bearer {token}

**Response:**
```json
{
  "profile_id": 1,
  "user_id": 123,
  "year_of_study": "3rd Year",
  "course": "Computer Science",
  "fields_of_interest": ["AI", "Web Development"],
  "profile_photo_url": "/uploads/photos/abc123.jpg",
  "resume_url": "/uploads/resumes/def456.pdf"
}
```

#### Update Profile
```
PUT /users/profile
```
**Headers:** Authorization: Bearer {token}

**Request Body:**
```json
{
  "year_of_study": "4th Year",
  "course": "Computer Science",
  "fields_of_interest": ["AI", "Machine Learning", "Web Development"],
  "profile_photo_url": "/uploads/photos/abc123.jpg",
  "resume_url": "/uploads/resumes/def456.pdf"
}
```
**Response:** Updated profile object

#### Get Users from Same Institution
```
GET /users/institution-users?role=alumni
```
**Headers:** Authorization: Bearer {token}

**Query Parameters:**
- `role`: Filter by user role (optional)

**Response:**
```json
[
  {
    "user_id": 124,
    "email": "alumni@example.com",
    "name": "John Doe",
    "role": "alumni",
    "status": "active",
    "institution_id": 1,
    "created_at": "2025-01-15T10:00:00"
  },
  {
    "user_id": 125,
    "email": "mentor@example.com",
    "name": "Jane Smith",
    "role": "mentor",
    "status": "active",
    "institution_id": 1,
    "created_at": "2025-01-20T11:30:00"
  }
]
```

## Messaging System

#### Send Message
```
POST /messages/
```
**Headers:** Authorization: Bearer {token}

**Request Body:**
```json
{
  "recipient_id": 124,
  "content": "Hello, I'd like to discuss a project idea.",
  "is_request": false
}
```

**Response:** Message object with details

#### Get Conversations
```
GET /messages/conversations
```
**Headers:** Authorization: Bearer {token}

**Response:**
```json
{
  "conversation-uuid-1": [
    {
      "message_id": 1,
      "sender_id": 123,
      "recipient_id": 124,
      "content": "Hello, I'd like to discuss a project idea.",
      "conversation_id": "conversation-uuid-1",
      "is_request": false,
      "timestamp": "2025-03-10T14:30:00",
      "sender_name": "Current User",
      "recipient_name": "John Doe"
    },
    {
      "message_id": 2,
      "sender_id": 124,
      "recipient_id": 123,
      "content": "Sure, I'd be happy to discuss. What's your idea?",
      "conversation_id": "conversation-uuid-1",
      "is_request": false,
      "timestamp": "2025-03-10T14:35:00",
      "sender_name": "John Doe",
      "recipient_name": "Current User"
    }
  ],
  "conversation-uuid-2": [
    /* Messages from another conversation */
  ]
}
```

## Posts

#### Create Post
```
POST /posts/
```
**Headers:** Authorization: Bearer {token}

**Request Body:**
```json
{
  "content": "Looking for collaborators on a machine learning project.",
  "tags": ["Machine Learning", "Project", "Collaboration"]
}
```

**Response:** Post object with details

#### Get Posts
```
GET /posts/?keyword=project&field=Machine Learning
```
**Headers:** Authorization: Bearer {token}

**Query Parameters:**
- `keyword`: Search posts by keyword (optional)
- `field`: Filter by field/tag (optional)

**Response:**
```json
[
  {
    "post_id": 1,
    "user_id": 124,
    "content": "Looking for collaborators on a machine learning project.",
    "tags": ["Machine Learning", "Project", "Collaboration"],
    "created_at": "2025-03-10T15:00:00",
    "user_name": "John Doe",
    "user_role": "alumni"
  },
  {
    "post_id": 2,
    "user_id": 125,
    "content": "Hosting a workshop on deep learning projects next week.",
    "tags": ["Deep Learning", "Machine Learning", "Workshop"],
    "created_at": "2025-03-09T10:00:00",
    "user_name": "Jane Smith",
    "user_role": "mentor"
  }
]
```

#### Delete Post
```
DELETE /posts/{post_id}
```
**Headers:** Authorization: Bearer {token}

**Response:**
```json
{
  "message": "Post deleted successfully"
}
```

## Resume Management

#### Upload Resume
```
POST /resume/upload
```
**Headers:** Authorization: Bearer {token}

**Form Data:**
- `file`: PDF file (required)

**Response:**
```json
{
  "resume_id": 1,
  "user_id": 123,
  "file_path": "/uploads/resumes/abc123.pdf",
  "extracted_text": "Resume text content...",
  "fields_extracted": {
    "skills": ["Python", "SQL", "FastAPI"],
    "education": ["Bachelor's in Computer Science"],
    "experience": ["Software Developer at XYZ Company"],
    "interests": ["Machine Learning", "Web Development"]
  },
  "processed_at": "2025-03-11T15:30:00"
}
```

## Institution Management

#### Get Institutions
```
GET /institutions/
```
**Headers:** Authorization: Bearer {token}

**Response:** List of institutions

#### Get Institution by ID
```
GET /institutions/{institution_id}
```
**Headers:** Authorization: Bearer {token}

**Response:** Institution details

## Admin Endpoints

### Normal Admin (Institution Level)

#### Get Pending Registrations
```
GET /admin/pending-registrations
```
**Headers:** Authorization: Bearer {token}

**Response:** List of pending users

#### Approve User
```
PUT /admin/approve-user/{user_id}
```
**Headers:** Authorization: Bearer {token}

**Response:** Updated user object

#### Delete User
```
DELETE /admin/user/{user_id}
```
**Headers:** Authorization: Bearer {token}

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

#### Send Admin Message
```
POST /admin/message
```
**Headers:** Authorization: Bearer {token}

**Request Body:**
```json
{
  "recipient_id": 123,
  "content": "Your account has been approved."
}
```

**Response:** Message object

### Super Admin (Platform Level)

#### Get All Institutions with Pending Status
```
GET /super-admin/institutions/pending
```
**Headers:** Authorization: Bearer {token}

**Response:** List of pending institutions

#### Approve Institution
```
PUT /super-admin/institutions/{institution_id}/approve
```
**Headers:** Authorization: Bearer {token}

**Response:** Updated institution object

#### Get System Stats
```
GET /super-admin/stats
```
**Headers:** Authorization: Bearer {token}

**Response:**
```json
{
  "total_institutions": 10,
  "total_users": 500,
  "user_status": {
    "pending": 20,
    "active": 480
  },
  "user_roles": {
    "students": 350,
    "alumni": 100,
    "mentors": 40,
    "admins": 10
  },
  "institution_types": {
    "private": 6,
    "government": 4
  }
}
```

#### Get All Users (with filtering)
```
GET /super-admin/users?status=active&role=student&institution_id=1
```
**Headers:** Authorization: Bearer {token}

**Query Parameters:**
- `status`: Filter by user status (optional)
- `role`: Filter by user role (optional)
- `institution_id`: Filter by institution (optional)
- `skip`: Pagination offset (default: 0)
- `limit`: Pagination limit (default: 100)

**Response:** List of users matching criteria

## Data Models

### User
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "name": "User Name",
  "role": "student|alumni|mentor|admin",
  "status": "pending|active|suspended",
  "institution_id": 1,
  "created_at": "2025-01-15T10:00:00"
}
```

### Profile
```json
{
  "profile_id": 1,
  "user_id": 123,
  "year_of_study": "3rd Year",
  "course": "Computer Science",
  "fields_of_interest": ["AI", "Web Development"],
  "profile_photo_url": "/uploads/photos/abc123.jpg",
  "resume_url": "/uploads/resumes/def456.pdf"
}
```

### Message
```json
{
  "message_id": 1,
  "sender_id": 123,
  "recipient_id": 124,
  "content": "Message content",
  "conversation_id": "uuid-conversation-id",
  "is_request": false,
  "timestamp": "2025-03-10T14:30:00"
}
```

### Post
```json
{
  "post_id": 1,
  "user_id": 123,
  "content": "Post content",
  "tags": ["Tag1", "Tag2"],
  "created_at": "2025-03-10T15:00:00"
}
```

### Institution
```json
{
  "institution_id": 1,
  "name": "College of Engineering",
  "institution_type": "private|government",
  "location": "City, State",
  "founded_year": 1990,
  "head_name": "Dr. John Smith",
  "head_designation": "Principal",
  "registration_email": "admin@college.edu",
  "status": "pending|approved|rejected",
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-10T10:00:00"
}
```

## Error Responses

All API errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```