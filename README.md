# VRChat Memory Keeper

A simple web application to record and share your VRChat memories with friends.

## Features

- 📝 **Event Tracking**: Records VRChat shared room events with friends
- 🏷️ **Tag System**: World tags and custom user tags for events
- 👍 **AJAX Likes**: Like events without page refresh
- 🔐 **User Authentication**: Secure login/register system
- 📱 **Responsive Design**: Works on all devices

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Bootstrap 5
- **Deployment**: PythonAnywhere

## Getting Started

### Local Development

1. **Clone or download the repository**

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### PythonAnywhere Deployment

1. **Create a PythonAnywhere account** at [pythonanywhere.com](https://www.pythonanywhere.com/)

2. **Upload your code** to PythonAnywhere:
   - Use git clone or the file uploader in the PythonAnywhere dashboard
   - Ensure your project structure matches:
     ```
     /home/your-username/VRChat-Memory-Keeper/
     ├── app.py
     ├── wsgi.py
     ├── requirements.txt
     ├── templates/
     ├── static/
     └── instance/
     ```

3. **Create a virtual environment on PythonAnywhere**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 venv
   ```

4. **Install dependencies**:
   ```bash
   workon venv
   pip install -r /home/your-username/VRChat-Memory-Keeper/requirements.txt
   ```

5. **Configure WSGI file**:
   - Go to the "Web" tab in PythonAnywhere dashboard
   - Set the "Source code" field to `/home/your-username/VRChat-Memory-Keeper`
   - Set the "Virtualenv" field to `/home/your-username/.virtualenvs/venv`
   - Edit the WSGI configuration file to match the content in `wsgi.py`
   - Ensure the username in the WSGI file matches your PythonAnywhere username

6. **Reload your web app**
   - Click the "Reload" button at the top of the Web tab
   - Your application should now be accessible at `https://your-username.pythonanywhere.com`

## Usage

### Login/Register
- Use the login page to access your account
- Register a new account if you don't have one

### Timeline
- View all your shared VRChat events in chronological order
- See world tags, custom tags, and event duration
- Like events with a simple click

### Event Details
- View detailed information about specific events
- Add custom tags to events
- See the exact start and end times

## Database Schema

The application uses a simple SQLite database with 4 tables:

1. **user**: Stores user information
2. **world**: Stores VRChat world details
3. **shared_event**: Records shared room events
4. **event_tag**: Many-to-many relationship between events and tags

## Demo Account

You can use the following demo account to test the application:
- **Username**: demo
- **Password**: demo

## Testing

Run the test suite with:
```bash
python -m pytest tests/test_app.py -v
```

## License

MIT License - feel free to use this project for learning and development purposes.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
