# **Legal Platform API**  

## **Overview**
The Legal Platform API is a Django-based application that connects clients with lawyers for consultations. It provides features for booking appointments, leaving reviews, rescheduling consultations, and sending notifications.

## **Project Progress So Far**  

### **1.  Project Setup & Configuration**  
- Initialized a Django project with a **virtual environment** and installed necessary dependencies.  
- Configured Django REST Framework (DRF) and **Simple JWT for authentication.**  
- Set up **Git and GitHub** for version control. 


## **2. Some inportatnt features include**
- User Authentication: Secure user registration and login.
- Lawyer Booking System: Clients can schedule consultations with lawyers.
- Consultation Management: Includes appointment status updates and rescheduling.
- Reviews & Ratings: Clients can leave reviews for lawyers.
- Notification System: Users receive notifications for booking updates.
- Admin Dashboard: Manage users, consultations, and reviews from Django Admin.

### **3.  User Authentication & Models**  
- Created **custom User model** with roles (`is_client`, `is_lawyer`).  
- Defined **ClientProfile** and **LawyerProfile** models (excluding profile pictures to avoid Pillow issues).  
- Implemented **registration, login, and authentication using JWT tokens.**  

### **4. API Endpoints & Permissions**  
- Built APIs for **registering, logging in, and updating user profiles.**  
- Restricted **access to lawyer and client lists** so that:  
  - Clients **can only see lawyers** (not other clients).  
  - Lawyers **can only see clients** (not other lawyers).  
  - Only **authenticated users** can access these lists.
  - Other APIs include:
- For Authentication
  - POST /api/auth/register/ - Register a new user.
  - POST /api/auth/login/ - Authenticate and get a token.

- For Consultations
  - POST /api/consultations/ - Schedule a consultation.
  - GET /api/consultations/ - List all consultations.
  - PUT /api/consultations/<id>/reschedule/ - Reschedule a consultation.
  - PUT /api/consultations/<id>/status/ - Update consultation status.

- For Reviews
  - POST /api/reviews/ - Submit a review.
  - GET /api/reviews/ - Get all reviews.
  - PUT /api/reviews/<id>/ - Edit a review.
  - DELETE /api/reviews/<id>/ - Delete a review.

- For Notifications
  - GET /api/notifications/ - List notifications.
  - PUT /api/notifications/<id>/read/ - Mark a notification as read.

### **5. Testing & Debugging**  
- Used **Postman** to test API endpoints.  
- Debugged issues like **missing migrations, token authentication errors, and profile creation problems.**  
- Manually created **ClientProfile and LawyerProfile** in the Django shell for existing users.  



### **6. Testing Key API Endpoints using Postman**
- For registration and login:
  To register a user -
  POST http://legal-platform.onrender.com/api/register/
For Client:
{
    "username": "john_jack",
    "email": "johnjack@example.com",
    "password": "password123",
    "is_client": true,
    "is_lawyer": false
}
For Lawyer:
{
    "username": "lawyer_duke",
    "email": "duke@example.com",
    "password": "password1234",
    "is_client": false,
    "is_lawyer": true
}

  To login a registered user -
  POST http://legal-platform.onrender.com/api/login/
{
    "email": "johnjack@example.com",
    "password": "password123"  
}

  To get a new token -
  POST http://legal-platform.onrender.com/api/auth/token/
{
    "username": "john_jack",
    "email": "johnjack@example.com",
    "password": "password123"  
}

  For token refresh -
  POST http://legal-platform.onrender.com/api/auth/token/refresh/
{
    "refresh": "your_refresh_token from logging-in"
}

  For updating a user (Clients/Lawyers) -
  PATCH http://legal-platform.onrender.com/api/profile/lawyer/update/
  PATCH http://legal-platform.onrender.com/api/profile/client/update/

  For Clients -
{
    "address": "New Address, USA"
}
  For Lawyers -
{
    "specialization": "Corporate Law",
    "address": "New Office, USA"
}


To create a booking by the client-
POST http://legal-platform.onrender.com/api/bookings/create/
{
  "lawyer": 3,
  "appointment_date": "2025-04-01T14:00:00Z"
}
{
  "lawyer": 2,  // ID of the lawyer being booked
  "date": "2025-03-27",
  "time": "14:00:00",
  "notes": "Need help with a contract dispute."
}
Retrieve All Bookings - GET /api/bookings/
Updating a Booking - PUT /api/bookings/update/<int:pk>/ - 
{
  "date": "2025-03-30",
  "time": "10:00:00",
  "status": "confirmed"
}

- For creating a consultation -
POST http://legal-platform.onrender.com/api//api/consultations/
{
  "lawyer": 1, 
  "client": 2,
  "date": "2025-04-01",
  "time": "14:00:00",
  "status": "pending",
  "notes": "Looking for advice on business contracts."
}
For updating a consultation -
PUT/PATCH http://legal-platform.onrender.com/api//api/consultations/<consultation_id>/
{
  "date": "2025-04-05",
  "time": "10:00:00",
  "status": "confirmed",
  "notes": "Rescheduled for a better time."
}



---

