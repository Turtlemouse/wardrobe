## "Building a Dating Site Database Application"

---

## Pre-Class Setup (Do This Before Class)

1. **Test MySQL connection** - Ensure MySQL server is running
2. **Have the shared folder** with all project files 
3. **Have the schema.sql ready** to run

---

### **SECTION 1: Setup**

**Point:** "We'll build a simple dating queue application called 'FindPeople.com' where people can join a line and select their interests."

---

#### 1.1 Create Virtual Environment
```bash
# Python 3.12
python3 -m venv demo

# Activate it
# On Mac/Linux:
source demo/bin/activate
# On Windows:
demo\Scripts\activate
```

**Common Pitfall Alert:** "Notice your terminal prompt changes with `(demo)`. If you don't see this, your environment isn't active!"

**Why Virtual Environment?** "Keeps project dependencies isolated. Different projects might need different package versions."

---

#### 1.2 Install Required Packages
```bash
pip install pymysql Flask
```

**Show `pip list`** to verify installation.

**Point:** "PyMySQL is our database connector. Flask is a lightweight web framework. We could use Django, but Flask is simpler for learning."

---

#### 1.3 Create Database Schema
```bash
# Open MySQL
mysql -u root -p
```

**In MySQL console:**
```sql
-- Show the schema.sql file in VS Code first
source schema.sql

-- Verify tables were created
SHOW TABLES;
DESC People;
DESC Interests;
DESC PersonInterests;

-- Check sample data
SELECT * FROM Interests;
```

**Exit MySQL:** `exit;`

---

### **SECTION 2: Database Connection Layer**

#### 2.1 Create `config.py`
**Type live or show pre-made:**
```python
# Database credentials
DB_USER = 'root'
DB_NAME = 'project3510'
DB_PASSWORD = 'Aa@12345678'
DB_HOST = 'localhost'

# Flask app settings
APP_HOST = '127.0.0.1'
APP_PORT = 5001
APP_DEBUG = True
```

**Point:** "In production, NEVER hardcode passwords. Use environment variables. But for learning, this is fine."

---

#### 2.2 Create `logic.py` - The Database Layer

**Start with the Database class structure:**
```python
import pymysql

class Database(object):
    """Database object to handle all DB operations"""

    def __init__(self, opts):
        """Initialize and connect to database"""
        self.opts = opts
        self.__connect()

    def __connect(self):
        """Establish MySQL connection"""
        self.conn = pymysql.connect(
            host=self.opts.DB_HOST,
            user=self.opts.DB_USER,
            password=self.opts.DB_PASSWORD,
            database=self.opts.DB_NAME
        )
```

**Point:** "We encapsulate all database logic in one class. This is called the **Data Access Layer** pattern."

---

#### 2.3 Add Query Methods

**Method 1: Get All People (Read Operation)**
```python
def get_people(self):
    """Fetch all people ordered by when they joined"""
    cur = self.conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('SELECT first_name, last_name FROM People ORDER BY time_added;')
    results = cur.fetchall()
    cur.close()
    return results
```

**Points:**
- "DictCursor returns rows as dictionaries instead of tuples"
- "Always ORDER BY time_added to show the queue correctly"
- "fetchall() loads all results into memory - fine for small datasets"

---

**Method 2: Insert Person (Write Operation)**
```python
def insert_person(self, firstname, lastname, phone, age):
    """Add a new person to the database"""
    cur = self.conn.cursor(pymysql.cursors.DictCursor)
    
    # CRITICAL: Use parameterized queries to prevent SQL injection!
    sql = '''INSERT INTO People (first_name, last_name, phone, age, time_added) 
             VALUES (%s, %s, %s, %s, NOW())'''
    
    result = cur.execute(sql, (firstname, lastname, phone, age))
    self.conn.commit()  # MUST COMMIT for changes to persist!
    cur.close()
    return result
```

```python
# BAD - Vulnerable to SQL Injection:
sql = f"INSERT INTO People VALUES ('{firstname}', '{lastname}')"

# GOOD - Parameterized query:
sql = "INSERT INTO People VALUES (%s, %s)"
cur.execute(sql, (firstname, lastname))
```

**Live Demo SQL Injection:**
"If someone enters `'; DROP TABLE People; --` as their first name, what happens?"
- Show BAD approach would execute DROP TABLE
- Show GOOD approach treats it as literal text

---

**Method 3: Get Interests**
```python
def get_interests(self):
    """Fetch all interests for the checkboxes"""
    cur = self.conn.cursor(pymysql.cursors.DictCursor)
    cur.execute('SELECT id, name FROM Interests ORDER BY sort_order;')
    results = cur.fetchall()
    cur.close()
    return results
```

---

### **SECTION 3: Flask Web Application**

#### 3.1 Create Project Structure
```bash
mkdir templates
mkdir resources

# Move HTML files to templates/
# Move CSS and images to resources/
```

**Show final structure:**
```
dating_app_demo/
├── demo/
├── config.py
├── logic.py
├── view.py
├── templates/
│   ├── index.html
│   ├── login.html
│   └── home.html
└── resources/
    ├── style.css
    └── looking_forward.jpg
```

---

#### 3.2 Create `view.py` - The Web Layer

**Initialize Flask App:**
```python
from flask import Flask, render_template, request, redirect, send_from_directory
import config
from logic import Database

# Create Flask app and database connection
app = Flask(__name__)
db = Database(config)

# Configure the app
app.host = config.APP_HOST
app.port = config.APP_PORT
app.debug = config.APP_DEBUG
```

**Point:** "Flask uses the `@app.route()` decorator to map URLs to functions."

---

#### 3.3 Main Page Route (GET Request)

```python
@app.route('/', methods=['GET'])
def index():
    """Display the main page with form and current queue"""
    people = db.get_people()
    interests = db.get_interests()
    return render_template('index.html', people=people, interests=interests)
```

**Show `index.html` in VS Code:**
```html
<!-- Point out Jinja2 templating -->
{% for person in people %}
  <li>{{person['first_name']}} {{person['last_name']}}</li>
{% endfor %}
```

**Point:** "Flask uses Jinja2 templates. The `{{ }}` syntax injects Python variables into HTML."

---

#### 3.4 Form Submission Route (POST Request)

```python
@app.route('/insert', methods=['POST'])
def insert():
    """Handle form submission to add a new person"""
    # Extract form data
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    phone = request.form['phone']
    age = request.form['age']
    
    # Validate data
    if not firstname or not lastname:
        return "First and last name are required!", 400
    
    if not phone.isdigit() or len(phone) != 10:
        return "Phone must be 10 digits!", 400
    
    try:
        age = int(age)
        if age < 18 or age > 99:
            return "Age must be between 18 and 99!", 400
    except ValueError:
        return "Invalid age!", 400
    
    # Insert into database
    if db.insert_person(firstname, lastname, phone, age):
        return redirect('/')  # Redirect back to main page
    
    return "Error adding to database", 500
```

**CRITICAL POINTS:**

1. **Always Validate Input:**
   - "Never trust user input!"
   - "Check data types, lengths, ranges"
   
2. **POST-Redirect-GET Pattern:**
   - "After POST, always redirect"
   - "Prevents duplicate submissions if user refreshes"

3. **HTTP Status Codes:**
   - 200: Success
   - 400: Bad Request (client error)
   - 500: Server Error

---

#### 3.5 Static Files Route

```python
@app.route('/resources/<path:path>')
def send_resources(path):
    """Serve CSS, images, etc."""
    return send_from_directory('resources', path)
```

---

#### 3.6 Run the Application

```python
if __name__ == '__main__':
    app.run()
```

**Start the server:**
```bash
python view.py
```

**Expected output:**
```
* Running on http://127.0.0.1:5001/
* Debug mode: on
```

---

### **SECTION 4: Live Testing & Debugging**

#### 4.1 Test the Application

**Open browser to `http://127.0.0.1:5001/`**

**Live Actions:**
1. **Add a valid person:**
   - First: John
   - Last: D 
   - Phone: 5551234567
   - Age: 25
   - Check some interests
   - Submit → Show they appear in "The line"

2. **Check database:**
```bash
mysql -u root -p project3510
SELECT * FROM People;
```

**Point:** "See the AUTO_INCREMENT ID and TIMESTAMP automatically filled in!"

---

#### 4.2 Demonstrate Common Errors

**Error 1: Missing Required Field**
- Leave first name blank
- Submit → Show validation error

**Error 2: Invalid Phone**
- Enter "abc123" as phone
- Show error message

**Error 3: SQL Injection Attempt**
- Enter `'; DROP TABLE People; --` as first name
- Show it's safely stored as text

**Error 4: Forgot to Commit**
```python
# Temporarily comment out db.conn.commit()
# Show data doesn't persist
# Re-add it and explain
```

---

#### 4.3 Check Flask Debug Mode

**Intentionally cause an error:**
```python
# In insert() function, add:
x = 1 / 0  # Division by zero
```

**Show the debug page with:**
- Stack trace
- Variable values
- Interactive debugger

**Point:** "Debug mode is AMAZING for learning but NEVER use in production - it exposes your code!"

---

### **SECTION 5: Wrap-Up & Extensions**

#### Key Takeaways (Review These):

1. **Three-Layer Architecture:**
   - Database Layer (logic.py)
   - Application Layer (view.py)
   - Presentation Layer (templates/)

2. **Security Best Practices:**
   - ✅ Parameterized queries (prevent SQL injection)
   - ✅ Input validation (check data before DB)
   - ✅ Never trust user input
   - ❌ Don't hardcode passwords in production

3. **Database Operations:**
   - SELECT: Read data
   - INSERT: Write data  
   - Always COMMIT writes!
   - Use ORDER BY for consistent results

4. **Web Development Patterns:**
   - GET: Retrieve pages/data
   - POST: Submit forms
   - POST-Redirect-GET: Prevent duplicate submissions
   - Template rendering: Separate logic from HTML

---

#### Common Questions:

**Q: Why not just use raw SQL in the routes?**
**A:** Separation of concerns. If you change databases (MySQL → PostgreSQL), you only update logic.py.

**Q: What if 1000 people submit at once?**
**A:** Connection pooling, async operations, caching. Topics for advanced courses!

**Q: Is this production-ready?**
**A:** NO! Missing: password hashing, CSRF protection, rate limiting, proper error handling, logging, etc.

**Q: Why Flask instead of Django?**
**A:** Flask is minimal and explicit - great for learning. Django is better for large projects.

---

## Troubleshooting Guide

### Issue: "Module not found: pymysql"
**Solution:** Virtual environment not activated or package not installed
```bash
source demo/bin/activate  # Activate first!
pip install pymysql Flask
```

### Issue: "Can't connect to MySQL server"
**Solution:** Check MySQL is running
```bash
mysql -u root -p
# If this fails, MySQL isn't running
```

### Issue: "Table doesn't exist"
**Solution:** Schema not created
```bash
mysql -u root -p < schema.sql
```

### Issue: "Data not showing up in database"
**Solution:** Forgot `commit()`
```python
self.conn.commit()  # Add this after INSERT/UPDATE/DELETE!
```

### Issue: "Form data is None"
**Solution:** Check form field names match
```html
<input name="firstname" />  <!-- Must match -->
```
```python
request.form['firstname']  # Exact match!
```

---

## Files Checklist

Before class, ensure you have:
- ✅ config.py
- ✅ logic.py
- ✅ view.py
- ✅ schema.sql
- ✅ templates/index.html
- ✅ templates/login.html
- ✅ templates/home.html
- ✅ resources/style.css
- ✅ resources/looking_forward.jpg

---

## Additional Resources for Students

- Flask Documentation: https://flask.palletsprojects.com/
- PyMySQL Documentation: https://pymysql.readthedocs.io/
- SQL Injection Prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
---

**Good luck with your demo! 🎓**
