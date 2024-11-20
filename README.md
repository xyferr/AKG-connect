# **AKGconnect**
### **Overview**
**AKGconnect** is a Django-based web application that allows students of **AKGEC** to seamlessly fetch and view their attendance data from the college ERP system, **Edumarshal**. The platform ensures a user-friendly interface, secure authentication, and real-time access to attendance records.

![Login Page](https://i.imgur.com/yYpAVa1.png "Login Page of AKGconnect")

![Attendance Page](https://i.imgur.com/v6tGvG4.png "Attenace Page of AKGconnect")






---

## **Features**
- **User Authentication**: 
  - Login with credentials validated via the Edumarshal API.
  - Persistent login using authentication tokens.

- **Attendance Dashboard**:
  - View overall attendance percentage, present days, and lectures.
  - Subject-wise attendance breakdown with visual indicators for present, absent, and remedial classes.

- **Session Management**:
  - Auth tokens and session data are securely stored to enable persistent logins.
  - Automatic token refresh for seamless attendance data fetching.

- **Error Handling**:
  - Detailed error messages for failed logins or API issues.
  - User-friendly notifications for unexpected errors.

---

## **Technologies Used**
- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript (Bootstrap for styling)
- **Database**: SQLite (default) or PostgreSQL
- **API Integration**: Edumarshal API for user authentication and attendance data
- **Other Tools**: Requests library for API calls

---

## **Setup Instructions**

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL (optional for production)
- Pip for managing dependencies

## Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/AKGconnect.git
   cd AKGconnect
   ```
2. **Set Up Virtual Environment**:
    ```bash
    python -m venv myenv
    source myenv/bin/activate  # On Windows: myenv\Scripts\activate
    ```
3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Set Up Environment Variables**: Create a .env file in the project root with the following keys:
    ```bash
    DJANGO_SECRET_KEY=your-secret-key
    DATABASE_URL=postgresql://user:password@localhost/dbname
    ```
5. **Run Migrations**:
    ```bash
    python manage.py migrate
    ```
6. **Start the Server**:
    ```bash
    python manage.py runserver
    ```
7. **Access the Application**: Open your browser and navigate to http://127.0.0.1:8000/.

---
## Usage
1. **Login**:
    - Enter your Edumarshal credentials on the login page.
    - If validated, you will be redirected to the attendance dashboard.
2. **View Attendance**:
    - Check your overall attendance percentage and subject-wise breakdown.
    - Detailed daily attendance records are also available.
3. **Stay Logged In**:
    - The application will automatically use stored tokens for subsequent logins.
---

## Project Structure
```bash
   AKGconnect/
│
├── Authentication/
│   ├── models.py         # UserModel, TokenModel, UserCred
│   ├── views.py          # Login, session handling
│   └── ...
│
├── Attendance/
│   ├── views.py          # Attendance fetching and rendering
│   └── templates/        # Frontend templates
│
├── manage.py             # Django project manager
├── requirements.txt      # Dependencies
└── README.md             # Documentation

   ```


## Contributing
Contributions are welcome! If you have ideas for new features or improvements, feel free to:

- Fork the repository
- Create a new branch for your feature
- Submit a pull request

## Contact
For queries or feedback, feel free to reach out:

- Author: Rohit Yadav
- Email: rohityadav.sde@example.com
- College: AKGEC
