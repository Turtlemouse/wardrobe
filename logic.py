import pymysql
import getpass


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
        password = getpass.getpass("ENTER PASSWORD: ")
        self.conn = pymysql.connect(
            host=self.opts.DB_HOST,
            user=self.opts.DB_USER,
            password=password,
            database=self.opts.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    
# ==========================================================
#                     STUDENTS
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
#                     COUNSELORS
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
#                   COUNSELOR ASSIGNMENTS
# ==========================================================

    def get_counselor_assignments(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    ca.assignment_id,
                    ca.student_id,
                    s.name AS student_name,
                    s.email AS student_email,

                    ca.counselor_id,
                    c.name AS counselor_name,
                    c.email AS counselor_email,

                    ca.start_date,
                    ca.end_date,
                    ca.is_primary
                FROM Counselor_Assignments ca
                JOIN Students s ON ca.student_id = s.student_id
                JOIN Counselors c ON ca.counselor_id = c.counselor_id
                ORDER BY ca.start_date DESC;
            """)
            return cur.fetchall()


    def get_counselor_assignment_by_id(self, assignment_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM Counselor_Assignments
                WHERE assignment_id = %s
            """, (assignment_id,))
            return cur.fetchone()


    def insert_counselor_assignment(self, student_id, counselor_id, start_date, end_date, is_primary):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Counselor_Assignments
                (student_id, counselor_id, start_date, end_date, is_primary)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, counselor_id, start_date, end_date, is_primary))
            self.conn.commit()


    def update_counselor_assignment(self, assignment_id, student_id, counselor_id, start_date, end_date, is_primary):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE Counselor_Assignments
                SET student_id = %s,
                    counselor_id = %s,
                    start_date = %s,
                    end_date = %s,
                    is_primary = %s
                WHERE assignment_id = %s
            """, (student_id, counselor_id, start_date, end_date, is_primary, assignment_id))
            self.conn.commit()


    def delete_counselor_assignment(self, assignment_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM Counselor_Assignments
                WHERE assignment_id = %s
            """, (assignment_id,))
            self.conn.commit()

# ==========================================================
#                     HEALTHCARE_PROVIDERS
# ==========================================================

    def get_providers(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Healthcare_Providers ORDER BY name;")
        return cur.fetchall()


    def get_provider_by_id(self, provider_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Healthcare_Providers WHERE provider_id = %s;", (provider_id,))
        return cur.fetchone()


    def insert_provider(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Healthcare_Providers
            (name, email, address, specialization, active)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['email'],
            data['address'],
            data.get('specialization'),
            data.get('active', 1)
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_provider(self, provider_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Healthcare_Providers
            SET name=%s, email=%s, address=%s, specialization=%s, active=%s
            WHERE provider_id = %s
        """

        values = (
            data['name'],
            data['email'],
            data['address'],
            data.get('specialization'),
            data.get('active', 1),
            provider_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_provider(self, provider_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Healthcare_Providers WHERE provider_id=%s;", (provider_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     SYMPTOMS
# ==========================================================

    def get_symptoms(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Symptoms ORDER BY symptom;")
        return cur.fetchall()


    def get_symptom_by_id(self, symptom_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Symptoms WHERE symptom_id = %s;", (symptom_id,))
        return cur.fetchone()


    def insert_symptom(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Symptoms (symptom)
            VALUES (%s)
        """

        values = (data['symptom'],)

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_symptom(self, symptom_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Symptoms
            SET symptom=%s
            WHERE symptom_id = %s
        """

        values = (
            data['symptom'],
            symptom_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_symptom(self, symptom_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Symptoms WHERE symptom_id=%s;", (symptom_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     DIAGNOSES
# ==========================================================

    def get_diagnoses(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Diagnoses ORDER BY diagnosis;")
        return cur.fetchall()


    def get_diagnosis_by_id(self, diagnosis_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Diagnoses WHERE diagnosis_id = %s;", (diagnosis_id,))
        return cur.fetchone()


    def insert_diagnosis(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Diagnoses (diagnosis)
            VALUES (%s)
        """

        values = (data['diagnosis'],)

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_diagnosis(self, diagnosis_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Diagnoses
            SET diagnosis=%s
            WHERE diagnosis_id = %s
        """

        values = (
            data['diagnosis'],
            diagnosis_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_diagnosis(self, diagnosis_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Diagnoses WHERE diagnosis_id=%s;", (diagnosis_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     CATEGORIES
# ==========================================================

    def get_categories(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Categories ORDER BY category;")
        return cur.fetchall()


    def get_category_by_id(self, category_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Categories WHERE category_id = %s;", (category_id,))
        return cur.fetchone()


    def insert_category(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Categories (category)
            VALUES (%s)
        """

        values = (data['category'],)

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_category(self, category_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Categories
            SET category=%s
            WHERE category_id = %s
        """

        values = (
            data['category'],
            category_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_category(self, category_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Categories WHERE category_id=%s;", (category_id,))
        self.conn.commit()
        return True


# ==========================================================
#                     ISSUES
# ==========================================================

    def get_issues(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                i.issue_id,
                i.diagnosis_id,
                d.diagnosis AS diagnosis_name,
                i.date,
                i.student_id,
                s.name AS student_name,
                i.provider_id,
                hp.name AS provider_name,
                i.counselor_id,
                c.name AS counselor_name,
                i.visit_id,
                i.comments
            FROM Issues i
            LEFT JOIN Diagnoses d ON i.diagnosis_id = d.diagnosis_id
            LEFT JOIN Students s ON i.student_id = s.student_id
            LEFT JOIN Healthcare_Providers hp ON i.provider_id = hp.provider_id
            LEFT JOIN Counselors c ON i.counselor_id = c.counselor_id
            ORDER BY i.date DESC;
        """)
        return cur.fetchall()


    def get_issue_by_id(self, issue_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Issues WHERE issue_id = %s;", (issue_id,))
        return cur.fetchone()


    def get_visits_for_dropdown(self):
        """Get visits with student names for dropdown display"""
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                v.visit_id,
                v.date,
                v.student_id,
                s.name AS student_name
            FROM Visits v
            JOIN Students s ON v.student_id = s.student_id
            ORDER BY v.date DESC;
        """)
        return cur.fetchall()


    def insert_issue(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Issues
            (diagnosis_id, date, student_id, provider_id, counselor_id, visit_id, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['diagnosis_id'],
            data['date'],
            data['student_id'],
            data.get('provider_id'),
            data.get('counselor_id'),
            data.get('visit_id'),
            data.get('comments')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_issue(self, issue_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Issues
            SET diagnosis_id=%s, date=%s, student_id=%s, 
                provider_id=%s, counselor_id=%s, visit_id=%s, comments=%s
            WHERE issue_id = %s
        """

        values = (
            data['diagnosis_id'],
            data['date'],
            data['student_id'],
            data.get('provider_id'),
            data.get('counselor_id'),
            data.get('visit_id'),
            data.get('comments'),
            issue_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_issue(self, issue_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Issues WHERE issue_id=%s;", (issue_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     REPORTED_SYMPTOMS
# ==========================================================

    def get_reported_symptoms(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                rs.reported_symptom_id,
                rs.student_id,
                s.name AS student_name,
                s.email AS student_email,
                rs.date,
                rs.symptom_id,
                sy.symptom AS symptom_name
            FROM Reported_Symptoms rs
            LEFT JOIN Students s ON rs.student_id = s.student_id
            LEFT JOIN Symptoms sy ON rs.symptom_id = sy.symptom_id
            ORDER BY rs.date DESC;
        """)
        return cur.fetchall()


    def get_reported_symptom_by_id(self, reported_symptom_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Reported_Symptoms WHERE reported_symptom_id = %s;", (reported_symptom_id,))
        return cur.fetchone()


    def insert_reported_symptom(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Reported_Symptoms
            (student_id, date, symptom_id)
            VALUES (%s, %s, %s)
        """

        values = (
            data['student_id'],
            data['date'],
            data['symptom_id']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_reported_symptom(self, reported_symptom_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Reported_Symptoms
            SET student_id=%s, date=%s, symptom_id=%s
            WHERE reported_symptom_id = %s
        """

        values = (
            data['student_id'],
            data['date'],
            data['symptom_id'],
            reported_symptom_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_reported_symptom(self, reported_symptom_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Reported_Symptoms WHERE reported_symptom_id=%s;", (reported_symptom_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     DIAGNOSIS_CATEGORIZATION
# ==========================================================

    def get_diagnosis_categorizations(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                dc.diagnosis_categorization_id,
                dc.diagnosis_id,
                d.diagnosis AS diagnosis_name,
                dc.category_id,
                c.category AS category_name
            FROM Diagnosis_Categorization dc
            LEFT JOIN Diagnoses d ON dc.diagnosis_id = d.diagnosis_id
            LEFT JOIN Categories c ON dc.category_id = c.category_id
            ORDER BY d.diagnosis, c.category;
        """)
        return cur.fetchall()


    def get_diagnosis_categorization_by_id(self, diagnosis_categorization_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Diagnosis_Categorization WHERE diagnosis_categorization_id = %s;", 
                   (diagnosis_categorization_id,))
        return cur.fetchone()


    def insert_diagnosis_categorization(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Diagnosis_Categorization
            (diagnosis_id, category_id)
            VALUES (%s, %s)
        """

        values = (
            data['diagnosis_id'],
            data['category_id']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_diagnosis_categorization(self, diagnosis_categorization_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Diagnosis_Categorization
            SET diagnosis_id=%s, category_id=%s
            WHERE diagnosis_categorization_id = %s
        """

        values = (
            data['diagnosis_id'],
            data['category_id'],
            diagnosis_categorization_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_diagnosis_categorization(self, diagnosis_categorization_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Diagnosis_Categorization WHERE diagnosis_categorization_id=%s;", 
                   (diagnosis_categorization_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     SYMPTOM_CATEGORIZATION
# ==========================================================

    def get_symptom_categorizations(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                sc.symptom_categorization_id,
                sc.symptom_id,
                s.symptom AS symptom_name,
                sc.category_id,
                c.category AS category_name
            FROM Symptom_Categorization sc
            LEFT JOIN Symptoms s ON sc.symptom_id = s.symptom_id
            LEFT JOIN Categories c ON sc.category_id = c.category_id
            ORDER BY s.symptom, c.category;
        """)
        return cur.fetchall()


    def get_symptom_categorization_by_id(self, symptom_categorization_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Symptom_Categorization WHERE symptom_categorization_id = %s;", 
                   (symptom_categorization_id,))
        return cur.fetchone()


    def insert_symptom_categorization(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Symptom_Categorization
            (symptom_id, category_id)
            VALUES (%s, %s)
        """

        values = (
            data['symptom_id'],
            data['category_id']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_symptom_categorization(self, symptom_categorization_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Symptom_Categorization
            SET symptom_id=%s, category_id=%s
            WHERE symptom_categorization_id = %s
        """

        values = (
            data['symptom_id'],
            data['category_id'],
            symptom_categorization_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_symptom_categorization(self, symptom_categorization_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Symptom_Categorization WHERE symptom_categorization_id=%s;", 
                   (symptom_categorization_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     VISITS
# ==========================================================

    def get_visits(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                v.visit_id,
                v.date,
                v.student_id,
                s.name AS student_name,
                s.email AS student_email,
                v.in_person
            FROM Visits v
            LEFT JOIN Students s ON v.student_id = s.student_id
            ORDER BY v.date DESC;
        """)
        return cur.fetchall()


    def get_visit_by_id(self, visit_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Visits WHERE visit_id = %s;", (visit_id,))
        return cur.fetchone()


    def insert_visit(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Visits
            (date, student_id, in_person)
            VALUES (%s, %s, %s)
        """

        values = (
            data['date'],
            data['student_id'],
            data.get('in_person', 1)
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_visit(self, visit_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Visits
            SET date=%s, student_id=%s, in_person=%s
            WHERE visit_id = %s
        """

        values = (
            data['date'],
            data['student_id'],
            data.get('in_person', 1),
            visit_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_visit(self, visit_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Visits WHERE visit_id=%s;", (visit_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     VISITS_COUNSELORS
# ==========================================================

    def get_visit_counselors(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                vc.visit_counselor_id,
                vc.visit_id,
                v.date AS visit_date,
                s.name AS student_name,
                vc.counselor_id,
                c.name AS counselor_name,
                c.specialization AS counselor_specialization
            FROM Visit_Counselors vc
            LEFT JOIN Visits v ON vc.visit_id = v.visit_id
            LEFT JOIN Students s ON v.student_id = s.student_id
            LEFT JOIN Counselors c ON vc.counselor_id = c.counselor_id
            ORDER BY v.date DESC;
        """)
        return cur.fetchall()


    def get_visit_counselor_by_id(self, visit_counselor_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Visit_Counselors WHERE visit_counselor_id = %s;", 
                   (visit_counselor_id,))
        return cur.fetchone()


    def insert_visit_counselor(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Visit_Counselors
            (visit_id, counselor_id)
            VALUES (%s, %s)
        """

        values = (
            data['visit_id'],
            data['counselor_id']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_visit_counselor(self, visit_counselor_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Visit_Counselors
            SET visit_id=%s, counselor_id=%s
            WHERE visit_counselor_id = %s
        """

        values = (
            data['visit_id'],
            data['counselor_id'],
            visit_counselor_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_visit_counselor(self, visit_counselor_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Visit_Counselors WHERE visit_counselor_id=%s;", 
                   (visit_counselor_id,))
        self.conn.commit()
        return True


# ==========================================================
#                     VISITS_COMMENTS
# ==========================================================

    def get_visit_comments(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                vc.comment_id,
                vc.visit_id,
                v.date AS visit_date,
                s.name AS student_name,
                vc.counselor_id,
                c.name AS counselor_name,
                c.specialization AS counselor_specialization,
                vc.comment
            FROM Visit_Comments vc
            LEFT JOIN Visits v ON vc.visit_id = v.visit_id
            LEFT JOIN Students s ON v.student_id = s.student_id
            LEFT JOIN Counselors c ON vc.counselor_id = c.counselor_id
            ORDER BY v.date DESC;
        """)
        return cur.fetchall()


    def get_visit_comment_by_id(self, comment_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Visit_Comments WHERE comment_id = %s;", 
                   (comment_id,))
        return cur.fetchone()


    def insert_visit_comment(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Visit_Comments
            (visit_id, counselor_id, comment)
            VALUES (%s, %s, %s)
        """

        values = (
            data['visit_id'],
            data['counselor_id'],
            data['comment']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_visit_comment(self, comment_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Visit_Comments
            SET visit_id=%s, counselor_id=%s, comment=%s
            WHERE comment_id = %s
        """

        values = (
            data['visit_id'],
            data['counselor_id'],
            data['comment'],
            comment_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_visit_comment(self, comment_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Visit_Comments WHERE comment_id=%s;", 
                   (comment_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     CRITICAL_SITUATIONS
# ==========================================================

    def get_critical_situations(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                cs.situation_id,
                cs.student_id,
                s.name AS student_name,
                s.email AS student_email,
                cs.start_date,
                cs.end_date
            FROM Critical_Situations cs
            LEFT JOIN Students s ON cs.student_id = s.student_id
            ORDER BY cs.start_date DESC;
        """)
        return cur.fetchall()


    def get_critical_situation_by_id(self, situation_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Critical_Situations WHERE situation_id = %s;", 
                   (situation_id,))
        return cur.fetchone()


    def insert_critical_situation(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Critical_Situations
            (student_id, start_date, end_date)
            VALUES (%s, %s, %s)
        """

        values = (
            data['student_id'],
            data['start_date'],
            data.get('end_date')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_critical_situation(self, situation_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Critical_Situations
            SET student_id=%s, start_date=%s, end_date=%s
            WHERE situation_id = %s
        """

        values = (
            data['student_id'],
            data['start_date'],
            data.get('end_date'),
            situation_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_critical_situation(self, situation_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Critical_Situations WHERE situation_id=%s;", 
                   (situation_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     FOLLOW_UPS
# ==========================================================

    def get_followups(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                f.follow_up_id,
                f.student_id,
                s.name AS student_name,
                s.email AS student_email,
                f.counselor_id,
                c.name AS counselor_name,
                c.specialization AS counselor_specialization,
                f.date,
                f.completed
            FROM Follow_Ups f
            LEFT JOIN Students s ON f.student_id = s.student_id
            LEFT JOIN Counselors c ON f.counselor_id = c.counselor_id
            ORDER BY f.date DESC;
        """)
        return cur.fetchall()


    def get_followup_by_id(self, follow_up_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Follow_Ups WHERE follow_up_id = %s;", 
                   (follow_up_id,))
        return cur.fetchone()


    def insert_followup(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Follow_Ups
            (student_id, counselor_id, date, completed)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['student_id'],
            data['counselor_id'],
            data['date'],
            data.get('completed', 0)
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_followup(self, follow_up_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Follow_Ups
            SET student_id=%s, counselor_id=%s, date=%s, completed=%s
            WHERE follow_up_id = %s
        """

        values = (
            data['student_id'],
            data['counselor_id'],
            data['date'],
            data.get('completed', 0),
            follow_up_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_followup(self, follow_up_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Follow_Ups WHERE follow_up_id=%s;", 
                   (follow_up_id,))
        self.conn.commit()
        return True

# ==========================================================
#                         DEANS
# ==========================================================
    def get_deans(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Deans ORDER BY name;")
        return cur.fetchall()


    def get_dean_by_id(self, dean_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Deans WHERE dean_id = %s;", (dean_id,))
        return cur.fetchone()


    def insert_dean(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Deans (name, email, school, title)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['email'],
            data['school'],
            data['title']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_dean(self, dean_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Deans
            SET name=%s, email=%s, school=%s, title=%s
            WHERE dean_id = %s
        """

        values = (
            data['name'],
            data['email'],
            data['school'],
            data['title'],
            dean_id
        )

        cur.execute(sql, values)
        self.conn.commit()


    def delete_dean(self, dean_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Deans WHERE dean_id = %s;", (dean_id,))
        self.conn.commit()

# ==========================================================
#                     TUTORS
# ==========================================================

    def get_tutors(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Tutors ORDER BY name;")
        return cur.fetchall()


    def get_tutor_by_id(self, tutor_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Tutors WHERE tutor_id = %s;", (tutor_id,))
        return cur.fetchone()


    def insert_tutor(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Tutors
            (name, email, specialty, age, active)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['email'],
            data.get('specialty'),
            data.get('age'),
            data.get('active', 1)
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_tutor(self, tutor_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Tutors
            SET name=%s, email=%s, specialty=%s, age=%s, active=%s
            WHERE tutor_id = %s
        """

        values = (
            data['name'],
            data['email'],
            data.get('specialty'),
            data.get('age'),
            data.get('active', 1),
            tutor_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_tutor(self, tutor_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Tutors WHERE tutor_id=%s;", (tutor_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     EMPLOYMENT_EVENTS
# ==========================================================

    def get_employment_events(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Employment_Events ORDER BY date DESC;")
        return cur.fetchall()


    def get_employment_event_by_id(self, event_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Employment_Events WHERE event_id = %s;", (event_id,))
        return cur.fetchone()


    def insert_employment_event(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Employment_Events
            (name, date, type, location)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['name'],
            data['date'],
            data.get('type'),
            data['location']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_employment_event(self, event_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Employment_Events
            SET name=%s, date=%s, type=%s, location=%s
            WHERE event_id = %s
        """

        values = (
            data['name'],
            data['date'],
            data.get('type'),
            data['location'],
            event_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_employment_event(self, event_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Employment_Events WHERE event_id=%s;", (event_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     HEALTHCARE_REFERRALS
# ==========================================================

    def get_healthcare_referrals(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                hr.referral_id,
                hr.student_id,
                s.name AS student_name,
                s.email AS student_email,
                hr.date,
                hr.provider_id,
                hp.name AS provider_name,
                hp.specialization AS provider_specialization,
                hr.resolution_details
            FROM Healthcare_Referrals hr
            LEFT JOIN Students s ON hr.student_id = s.student_id
            LEFT JOIN Healthcare_Providers hp ON hr.provider_id = hp.provider_id
            ORDER BY hr.date DESC;
        """)
        return cur.fetchall()


    def get_healthcare_referral_by_id(self, referral_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Healthcare_Referrals WHERE referral_id = %s;", 
                   (referral_id,))
        return cur.fetchone()


    def insert_healthcare_referral(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Healthcare_Referrals
            (student_id, date, provider_id, resolution_details)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['student_id'],
            data['date'],
            data['provider_id'],
            data.get('resolution_details')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_healthcare_referral(self, referral_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Healthcare_Referrals
            SET student_id=%s, date=%s, provider_id=%s, resolution_details=%s
            WHERE referral_id = %s
        """

        values = (
            data['student_id'],
            data['date'],
            data['provider_id'],
            data.get('resolution_details'),
            referral_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_healthcare_referral(self, referral_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Healthcare_Referrals WHERE referral_id=%s;", 
                   (referral_id,))
        self.conn.commit()
        return True

# ==========================================================
#                     DEAN_REFERRALS
# ==========================================================

    def get_dean_referrals(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                dr.referral_id,
                dr.student_id,
                s.name AS student_name,
                s.email AS student_email,
                dr.date,
                dr.dean_id,
                d.name AS dean_name,
                d.school AS dean_school,
                dr.resolution_details
            FROM Dean_Referrals dr
            LEFT JOIN Students s ON dr.student_id = s.student_id
            LEFT JOIN Deans d ON dr.dean_id = d.dean_id
            ORDER BY dr.date DESC;
        """)
        return cur.fetchall()


    def get_dean_referral_by_id(self, referral_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Dean_Referrals WHERE referral_id = %s;", 
                   (referral_id,))
        return cur.fetchone()


    def insert_dean_referral(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Dean_Referrals
            (student_id, date, dean_id, resolution_details)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['student_id'],
            data['date'],
            data['dean_id'],
            data.get('resolution_details')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_dean_referral(self, referral_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Dean_Referrals
            SET student_id=%s, date=%s, dean_id=%s, resolution_details=%s
            WHERE referral_id = %s
        """

        values = (
            data['student_id'],
            data['date'],
            data['dean_id'],
            data.get('resolution_details'),
            referral_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_dean_referral(self, referral_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Dean_Referrals WHERE referral_id=%s;", 
                   (referral_id,))
        self.conn.commit()
        return True

#==========================================================
#                   TUTOR_REFFERALS
#==========================================================
    def get_tutor_referrals(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                tr.referral_id,
                tr.student_id,
                s.name AS student_name,
                s.email AS student_email,
                tr.date,
                tr.tutor_id,
                t.name AS tutor_name,
                t.specialty AS tutor_specialty,
                tr.resolution_details
            FROM Tutor_Referrals tr
            LEFT JOIN Students s ON tr.student_id = s.student_id
            LEFT JOIN Tutors t ON tr.tutor_id = t.tutor_id
            ORDER BY tr.date DESC;
        """)
        return cur.fetchall()


    def get_tutor_referral_by_id(self, referral_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Tutor_Referrals WHERE referral_id = %s;", 
                (referral_id,))
        return cur.fetchone()


    def insert_tutor_referral(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Tutor_Referrals
            (student_id, date, tutor_id, resolution_details)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['student_id'],
            data['date'],
            data['tutor_id'],
            data.get('resolution_details')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_tutor_referral(self, referral_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Tutor_Referrals
            SET student_id=%s, date=%s, tutor_id=%s, resolution_details=%s
            WHERE referral_id = %s
        """

        values = (
            data['student_id'],
            data['date'],
            data['tutor_id'],
            data.get('resolution_details'),
            referral_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_tutor_referral(self, referral_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Tutor_Referrals WHERE referral_id=%s;", 
                (referral_id,))
        self.conn.commit()
        return True
#==========================================================
#                     JOB_REFERRALS
#==========================================================
    def get_job_referrals(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                jr.referral_id,
                jr.student_id,
                s.name AS student_name,
                s.email AS student_email,
                jr.date,
                jr.event_id,
                ee.name AS event_name,
                ee.date AS event_date,
                ee.type AS event_type,
                jr.resolution_details
            FROM Job_Referrals jr
            LEFT JOIN Students s ON jr.student_id = s.student_id
            LEFT JOIN Employment_Events ee ON jr.event_id = ee.event_id
            ORDER BY jr.date DESC;
        """)
        return cur.fetchall()


    def get_job_referral_by_id(self, referral_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Job_Referrals WHERE referral_id = %s;", 
                (referral_id,))
        return cur.fetchone()


    def insert_job_referral(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Job_Referrals
            (student_id, date, event_id, resolution_details)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            data['student_id'],
            data['date'],
            data['event_id'],
            data.get('resolution_details')
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_job_referral(self, referral_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Job_Referrals
            SET student_id=%s, date=%s, event_id=%s, resolution_details=%s
            WHERE referral_id = %s
        """

        values = (
            data['student_id'],
            data['date'],
            data['event_id'],
            data.get('resolution_details'),
            referral_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_job_referral(self, referral_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Job_Referrals WHERE referral_id=%s;", 
                (referral_id,))
        self.conn.commit()
        return True
#==========================================================
#                      STRUGGLE_COURSES
#==========================================================
    def get_struggle_courses(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("""
            SELECT 
                sc.struggle_id,
                sc.student_id,
                s.name AS student_name,
                s.email AS student_email,
                sc.course_number
            FROM Struggle_Courses sc
            LEFT JOIN Students s ON sc.student_id = s.student_id
            ORDER BY s.name, sc.course_number;
        """)
        return cur.fetchall()


    def get_struggle_course_by_id(self, struggle_id):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM Struggle_Courses WHERE struggle_id = %s;", 
                (struggle_id,))
        return cur.fetchone()


    def insert_struggle_course(self, data):
        cur = self.conn.cursor()

        sql = """
            INSERT INTO Struggle_Courses
            (student_id, course_number)
            VALUES (%s, %s)
        """

        values = (
            data['student_id'],
            data['course_number']
        )

        cur.execute(sql, values)
        self.conn.commit()
        return cur.lastrowid


    def update_struggle_course(self, struggle_id, data):
        cur = self.conn.cursor()

        sql = """
            UPDATE Struggle_Courses
            SET student_id=%s, course_number=%s
            WHERE struggle_id = %s
        """

        values = (
            data['student_id'],
            data['course_number'],
            struggle_id
        )

        cur.execute(sql, values)
        self.conn.commit()
        return True


    def delete_struggle_course(self, struggle_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM Struggle_Courses WHERE struggle_id=%s;", 
                (struggle_id,))
        self.conn.commit()
        return True
    

    def row_exists(self, table_name, column_names, values, id=-1):
        
        if len(column_names) != len(values):
            raise ValueError("column_names and values must be the same length")

        # Get the correct primary key column name
        id_column = TABLE_PRIMARY_KEYS.get(table_name, 'id')

        # Build the WHERE clause for candidate key comparison
        where_clause = " AND ".join(f"{col}=%s" for col in column_names)

        # Exclude the current row if id is provided
        if id != -1:
            where_clause += f" AND {id_column} != %s"
            values = list(values) + [id]

        query = f"""
            SELECT 1
            FROM {table_name}
            WHERE {where_clause}
            LIMIT 1
        """
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query, tuple(values))
        result = cur.fetchone()
        return result is not None
