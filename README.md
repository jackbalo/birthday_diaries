# Birthday Diaries

A web application to help you keep track of your friends' birthdays and manage your personal profile ao you don't miss a loved one's birthday. Your homepage will list friends whose birthdays are that day. Built using Python (Flask), SQLite, and Bootstrap with html,css and js for the frontend and jinja for templating.

---

## Features

- **User Authentication**: Secure login and registration system.
- **Profile Management**: Update user details, reset passwords, or delete accounts.
- **Search Functionality**: Quickly find friends' birthdays using the search bar.
- **Audit Logs**: Tracks user actions like account creation and deletions.
- **Responsive Design**: Built with Bootstrap for seamless use on any device.
---

## Technologies Used


- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite
- **Authentication**: Password hashing using `werkzeug.security` and session management
- **Additional Libraries**: 
  - `Flask-Login` for user authentication
  - `Flatpickr` for date inputs
---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```bash
   cd <repository-folder>
   ```

3. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set the `FLASK_APP` environment variable:
   ```bash
   export FLASK_APP=app.py  # On Windows use `set FLASK_APP=app.py`
   ```

6. Initialize the database:
   ```bash
   flask run
   ```

---

## Usage

1. Open the app in your web browser (default: `http://127.0.0.1:5000`). 
2. **Register**: Create a new account.
3. **Login**: Access your dashboard.
4. **Manage Birthdays**:
   - Add a friend's birthday.
   - Edit or delete entries as needed.
4. **Update Profile**: Edit your personal details.
5. **Search**: Quickly find a friend's birthday using the search bar.
6. **Delete Account**: Permanently remove your account if needed.

---

## Database Schema

### Users Table
| Field      | Type    |
|------------|---------|
| id         | INTEGER |
| name       | TEXT    |
| username   | TEXT    |
| hash       | TEXT    |
| dob        | TEXT    |
| email      | TEXT    |
| phone      | TEXT    |

### Birthdays Table
| Field      | Type    |
|------------|---------|
| id         | INTEGER |
| user_id    | INTEGER |
| name       | TEXT    |
| birthdate  | TEXT    |
| phone      | TEXT    |
| email      | TEXT    |

### Audit Logs Table
| Field      | Type    |
|------------|---------|
| id         | INTEGER |
| user_id    | INTEGER |
| action     | TEXT    |
| timestamp  | TEXT    |

---

## Audit Logs

The app includes a feature to log significant user actions, such as:
- Account creation
- Profile updates
- birthday Additions
- Birthday deletions
- Account deletions

These logs are stored in the `audit_logs` table in the database.

## Folder Structure

```
birthday-tracker/
│
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
├── app.py                # Main application file
├── database/             # Database initialization scripts
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Contributing

We welcome contributions! Feel free to fork the repository and submit a pull request.
Any enhancements are welcome.


## Future Enhancements

1. Add emailand phone push notifications for upcoming birthdays.
2. Integrate a calendar view for better visualization.
3. Improve search functionality with advanced filters.
4. Add email and phone number otp verification.
5. Create a mobile app.
6. Make the website more lively.

---
