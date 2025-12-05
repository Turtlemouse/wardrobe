import pymysql


# At the top of your logic.py file or in a config
TABLE_PRIMARY_KEYS = {
    'Students': 'student_id',
    'Counselors': 'counselor_id',
    'Deans': 'dean_id',
    # Add other tables as needed
}

class CursorIterator(object):
    """Iterator for the cursor object."""

    def __init__(self, cursor):
        """ Instantiate a cursor object"""
        self.__cursor = cursor

    def __iter__(self):
        elem = self.__cursor.fetchone()
        while elem:
            yield elem
            elem = self.__cursor.fetchone()
        self.__cursor.close()


class Database(object):
    """Database object"""

    def __init__(self, opts):
        """Initalize database object"""
        super(Database, self).__init__()
        self.opts = opts
        self.__connect()

    def __connect(self):
        """Connect to the database"""
        password = self.opts.DB_PASSWORD
        self.conn = pymysql.connect(
            host=self.opts.DB_HOST,
            user=self.opts.DB_USER,
            password=password,
            database=self.opts.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    
# ==========================================================
#                     ITEMS --> need to just kinda update this
# ==========================================================

    def get_students(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Students ORDER BY name;")
        return cur.fetchall()


    def get_student_by_id(self, student_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Students WHERE student_id = %s;", (student_id,))
        return cur.fetchone()

    def insert_student(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Students
            (name, ssn, email, date_of_birth, country_of_birth, gender, grad_year,
            insurance_provider, race, zip, street, academic_difficulty, dean_id, consent_scope)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['ssn'],
            data['email'],
            data['date_of_birth'],
            data['country_of_birth'],
            data['gender'],
            data['grad_year'],
            data['insurance_provider'],
            data['race'],
            data['zip'],
            data['street'],
            data['academic_difficulty'],
            data['dean_id'],
            data['consent_scope']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid

    def update_student(self, student_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Students
            SET name=%s, ssn=%s, email=%s, date_of_birth=%s,
                country_of_birth=%s, gender=%s, grad_year=%s,
                insurance_provider=%s, race=%s, zip=%s, street=%s,
                academic_difficulty=%s, dean_id=%s, consent_scope=%s
            WHERE student_id = %s
        """

        values = (
            data['name'],
            data['ssn'],
            data['email'],
            data['date_of_birth'],
            data['country_of_birth'],
            data['gender'],
            data['grad_year'],
            data['insurance_provider'],
            data['race'],
            data['zip'],
            data['street'],
            data['academic_difficulty'],
            data['dean_id'],
            data['consent_scope'],
            student_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True

    def delete_student(self, student_id):
        """Delete student"""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Students WHERE student_id=%s;", (student_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     RULES --> need to make logic here
# ==========================================================

    def get_counselors(self):
        """Return all counselors"""
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Counselors ORDER BY counselor_id;")
        return cur.fetchall()

    def get_counselor_by_id(self, counselor_id):
        """Fetch a single counselor"""
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Counselors WHERE counselor_id = %s;", (counselor_id,))
        return cur.fetchone()
    
    def insert_counselor(self, data):
        """Insert a new counselor"""
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Counselors
            (name, ssn, email, salary, highest_degree, highest_degree_school,
             yrs_experience, yrs_here, specialization, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['ssn'],
            data['email'],
            data.get('salary', 0),
            data['highest_degree'],
            data['highest_degree_school'],
            data['yrs_experience'],
            data['yrs_here'],
            data['specialization'],
            data.get('active', 1)
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid

    def update_counselor(self, counselor_id, data):
        """Update an existing counselor"""
        cur = self.conn.cursor()

        sql = """
            UPDATE Counselors
            SET name=%s, ssn=%s, email=%s, salary=%s, highest_degree=%s,
                highest_degree_school=%s, yrs_experience=%s, yrs_here=%s, 
                specialization=%s, active=%s
            WHERE counselor_id = %s
        """

        values = (
            data['name'],
            data['ssn'],
            data['email'],
            data.get('salary', 0),
            data['highest_degree'],
            data['highest_degree_school'],
            data['yrs_experience'],
            data['yrs_here'],
            data['specialization'],
            data.get('active', 1),
            counselor_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True

    def delete_counselor(self, counselor_id):
        """Delete counselor"""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Counselors WHERE counselor_id=%s;", (counselor_id,))
        self.conn.commit()
        return True
    
# ==========================================================
#                     OUTFIT GENERATION STUFF
# ==========================================================
