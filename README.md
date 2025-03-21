# **Legal Platform API**  

This project is a **Django REST Framework (DRF)-based API** that connects **clients with lawyers** based on their legal needs. Clients can find and communicate with lawyers without needing to visit a law office physically.  

## **Project Progress So Far**  

### **1.  Project Setup & Configuration**  
- Initialized a Django project with a **virtual environment** and installed necessary dependencies.  
- Configured Django REST Framework (DRF) and **Simple JWT for authentication.**  
- Set up **Git and GitHub** for version control.  

### **2.  User Authentication & Models**  
- Created **custom User model** with roles (`is_client`, `is_lawyer`).  
- Defined **ClientProfile** and **LawyerProfile** models (excluding profile pictures to avoid Pillow issues).  
- Implemented **registration, login, and authentication using JWT tokens.**  

### **3. API Endpoints & Permissions**  
- Built APIs for **registering, logging in, and updating user profiles.**  
- Restricted **access to lawyer and client lists** so that:  
  - Clients **can only see lawyers** (not other clients).  
  - Lawyers **can only see clients** (not other lawyers).  
  - Only **authenticated users** can access these lists.  

### **4. Testing & Debugging**  
- Used **Postman** to test API endpoints.  
- Debugged issues like **missing migrations, token authentication errors, and profile creation problems.**  
- Manually created **ClientProfile and LawyerProfile** in the Django shell for existing users.  

---

## **Next Steps**  
- Implement **lawyer verification system** (lawyers upload credentials).  
- Add **filtering and searching** for lawyers based on specialization.  
- Improve error handling and API documentation.  
