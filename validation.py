from flask import Flask, render_template, request, redirect, flash
from logic import Database


def validate_string(val):
    errorMessage = ""

    # Condition
    if not val.replace(" ", "").isalpha():
        errorMessage += "Invalid string. Only letters are allowed.\n"
    
    return errorMessage

def validate_ssn(val):
    errorMessage = ""
    cleaned_ssn = val.replace("-", "").replace(" ", "")

    # Must be exactly 9 digits
    if not cleaned_ssn.isdigit() or len(cleaned_ssn) != 9:
        errorMessage += "Invalid SSN format. Expected format: 123-45-6789\n"
    return errorMessage
    

def validate_int(val):
    errorMessage = ""

    # Condition
    if not val.isdigit():
        errorMessage += "Invalid integer. Only digits are allowed.\n"
    
    return errorMessage

def validate_email(val):
    errorMessage = ""

    # Basic email format check
    if "@" not in val or len(val.split(".")[-1]) != 3:
        errorMessage += "Invalid email. Email must include @ and end in 3-letter top level domain.\n"
    return errorMessage

def validate_course(val):
    errorMessage = ""

    # Condition
    if not len(val) == 9 or not val[:4].isalpha() or not val[5:].isdigit() or not val[5] == "-":
        errorMessage += "Invalid course format. Expected format: ABCD-1234\n"
    
    return errorMessage

def validate_bool(val):
    errorMessage = ""

    # Condition
    if not val == "1" and not val == "0":
        errorMessage += "Invalid boolean. Acceptable options are Yes and No.\n"
    
    return errorMessage






#############################

# -----------------------------
# VALIDATION: Deans
# -----------------------------
def validate_deans(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    email = data['email']
    school = data['school']
    title = data['title']
    active = data['active']

    errorMessage += validate_string(name)
    errorMessage += validate_email(email)
    errorMessage += validate_string(school)
    errorMessage += validate_string(title)
    errorMessage += validate_bool(active)

    if db.row_exists("Deans", ["email"], [email], id):
        errorMessage += "This email is already in use by another dean.\n"

    if errorMessage == "":
        active = True if active == "Yes" else False

        db.insert_dean(
          data
        )
        return redirect('/deans')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('deans/deans_form.html', data=data)


# -----------------------------
# VALIDATION: Students
# -----------------------------
def validate_students(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    ssn = data['ssn']
    email = data['email']
    date_of_birth = data['date_of_birth']
    country_of_birth = data['country_of_birth']
    gender = data['gender']
    grad_year = data['grad_year']
    insurance_provider = data['insurance_provider']
    race = data['race']
    zip = data['zip']
    street = data['street']
    academic_difficulty = data['academic_difficulty']
    dean_id = data['dean_id']
    consent_scope = data['consent_scope']
    active = data['active']

    errorMessage += validate_string(name)
    errorMessage += validate_ssn(ssn)
    errorMessage += validate_email(email)
    errorMessage += validate_string(country_of_birth)
    errorMessage += validate_string(gender)
    errorMessage += validate_int(grad_year)
    errorMessage += validate_string(insurance_provider)
    errorMessage += validate_string(race)
    errorMessage += validate_int(zip)
    errorMessage += validate_string(street)
    errorMessage += validate_bool(academic_difficulty)
    errorMessage += validate_bool(active)

    if errorMessage == "":
        ssn = ssn.replace("-", "").replace(" ", "")
        ssn = int(ssn)
        grad_year = int(grad_year)
        zip = int(zip)
        academic_difficulty = True if academic_difficulty == "Yes" else False
        active = True if active == "Yes" else False

        if db.row_exists("Students", ["email"], [email], id):
            errorMessage += "This email is already in use by another student.\n"
        if db.row_exists("Students", ["ssn"], [ssn], id):
            errorMessage += "This ssn is already in use by another student.\n"

        if errorMessage == "":
            db.insert_student(
                data
            )
            return redirect('/students')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('students/students_form.html', data=data)


# -----------------------------
# VALIDATION: Counselors
# -----------------------------
def validate_counselors(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    ssn = data['ssn']
    email = data['email']
    salary = data['salary']
    highest_degree = data['highest_degree']
    highest_degree_school = data['highest_degree_school']
    yrs_experience = data['yrs_experience']
    yrs_here = data['yrs_here']
    specialization = data['specialization']
    active = data['active']

    errorMessage += validate_string(name)
    errorMessage += validate_ssn(ssn)
    errorMessage += validate_email(email)
    errorMessage += validate_int(salary)
    errorMessage += validate_string(highest_degree)
    errorMessage += validate_string(highest_degree_school)
    errorMessage += validate_int(yrs_experience)
    errorMessage += validate_int(yrs_here)
    errorMessage += validate_string(specialization)
    errorMessage += validate_bool(active)

    if errorMessage == "":
        ssn = ssn.replace("-", "").replace(" ", "")
        ssn = int(ssn)
        salary = int(salary)
        yrs_experience = int(yrs_experience)
        yrs_here = int(yrs_here)
        active = True if active == "Yes" else False

        if db.row_exists("Counselors", ["email"], [email], id):
            errorMessage += "This email is already in use by another counselor.\n"
        if db.row_exists("Counselors", ["ssn"], [ssn], id):
            errorMessage += "This ssn is already in use by another counselor.\n"

        if errorMessage == "" and id == -1:
            db.insert_counselor(data)
            return redirect('/counselors')
        if errorMessage == "" and id > 0:
            db.update_counselor(id, data)
            return redirect('/counselors')
        

    if errorMessage != "":
        flash(errorMessage)
        return render_template('counselors/counselors_form.html', data=data)


# -----------------------------
# VALIDATION: Counselor_Assignments
# -----------------------------
def validate_counselor_assignments(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    counselor_id = data['counselor_id']
    start_date = data['start_date']
    end_date = data['end_date']
    is_primary = data['is_primary']

    errorMessage += validate_bool(is_primary)

    if start_date and end_date and start_date > end_date:
        errorMessage += "End date must be after start date.\n"

    if db.row_exists("Counselor_Assignments", ["student_id", "counselor_id", "start_date"], [student_id, counselor_id, start_date], id):
        errorMessage += "This assignment is already in the database.\n"

    if errorMessage == "":
        is_primary = True if is_primary == "Yes" else False

        db.insert_counselor_assignment(
            data
        )
        return redirect('/counselor_assignments')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('counselor_assignments/counselor_assignments_form.html', data=data)


# -----------------------------
# VALIDATION: Healthcare_Providers
# -----------------------------
def validate_healthcare_providers(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    email = data['email']
    address = data['address']
    specialization = data['specialization']
    active = data['active']

    errorMessage += validate_string(name)
    errorMessage += validate_email(email)
    errorMessage += validate_string(address)
    errorMessage += validate_string(specialization)
    errorMessage += validate_bool(active)

    if db.row_exists("Healthcare_Providers", ["email"], [email], id):
        errorMessage += "This email is already in use by another healthcare provider.\n"
    

    if errorMessage == "":
        active = True if active == "Yes" else False

        db.insert_healthcare_provider(
            data
        )
        return redirect('/healthcare_providers')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('healthcare_providers/healthcare_providers_form.html', data=data)


# -----------------------------
# VALIDATION: Symptoms
# -----------------------------
def validate_symptoms(data, db, id=-1):
    errorMessage = ""

    symptom = data['symptom']

    errorMessage += validate_string(symptom)

    if errorMessage == "":
        db.insert_symptom(data)
        return redirect('/symptoms')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('symptoms/symptoms_form.html', data=data)


# -----------------------------
# VALIDATION: Diagnoses
# -----------------------------
def validate_diagnoses(data, db, id=-1):
    errorMessage = ""

    diagnosis = data['diagnosis']

    errorMessage += validate_string(diagnosis)

    if errorMessage == "":
        db.insert_diagnosis(data)
        return redirect('/diagnoses')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('diagnoses/diagnoses_form.html', data=data)


# -----------------------------
# VALIDATION: Categories
# -----------------------------
def validate_categories(data, db, id=-1):
    errorMessage = ""

    category = data['category']

    errorMessage += validate_string(category)

    if errorMessage == "":
        db.insert_category(data)
        return redirect('/categories')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('catagories/categories_form.html', data=data)


# -----------------------------
# VALIDATION: Issues
# -----------------------------
def validate_issues(data, db, id=-1):
    errorMessage = ""

    diagnosis_id = data['diagnosis_id']
    date = data['date']
    student_id = data['student_id']
    provider_id = data['provider_id']
    counselor_id = data['counselor_id']
    comments = data['comments']

    if errorMessage == "":
        db.insert_issue(
           data
        )
        return redirect('/issues')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('issues/issues_form.html', data=data)


# -----------------------------
# VALIDATION: Reported_Symptoms
# -----------------------------
def validate_reported_symptoms(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    date = data['date']
    symptom_id = data['symptom_id']

    if db.row_exists("Reported_Symptoms", ["student_id", "date", "symptom_id"], [student_id, date, symptom_id], id):
        errorMessage += "This symptom has already been reported.\n"
    

    if errorMessage == "":
        db.insert_reported_symptom(
           data
        )
        return redirect('/reported_symptoms')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('reported_symptoms/reported_symptoms_form.html', data=data)


# -----------------------------
# VALIDATION: Diagnosis_Categorization
# -----------------------------
def validate_diagnosis_categorization(data, db, id=-1):
    errorMessage = ""

    diagnosis_id = data['diagnosis_id']
    category_id = data['category_id']

    if db.row_exists("Diagnosis_Categorization", ["diagnosis_id", "category_id"], [diagnosis_id, category_id], id):
        errorMessage += "This diagnosis is already categorized as such.\n"
    

    if errorMessage == "":
        db.insert_diagnosis_categorization(
            data
        )
        return redirect('/diagnosis_categorization')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('diagnosis_categorization/diagnosis_categorization_form.html', data=data)


# -----------------------------
# VALIDATION: Symptom_Categorization
# -----------------------------
def validate_symptom_categorization(data, db, id=-1):
    errorMessage = ""

    symptom_id = data['symptom_id']
    category_id = data['category_id']
    
    if db.row_exists("Symptom_Categorization", ["symptom_id", "category_id"], [symptom_id, category_id], id):
        errorMessage += "This symptom is already categorized as such.\n"
    

    if errorMessage == "":
        db.insert_symptom_categorization(
           data
        )
        return redirect('/symptom_categorization')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('symptom_categorization/symptom_categorization_form.html', data=data)


# -----------------------------
# VALIDATION: Visits
# -----------------------------
def validate_visits(data, db, id=-1):
    errorMessage = ""

    date = data['date']
    student_id = data['student_id']
    in_person = data['in_person']

    errorMessage += validate_bool(in_person)

    if errorMessage == "":
        in_person = True if in_person == "Yes" else False

        db.insert_visit(
            data
        )
        return redirect('/visits')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('visits/visits_form.html', data=data)


# -----------------------------
# VALIDATION: Visit_Counselors
# -----------------------------
def validate_visit_counselors(data, db, id=-1):
    errorMessage = ""

    visit_id = data['visit_id']
    counselor_id = data['counselor_id']

    if db.row_exists("Visit_Counselors", ["visit_id", "counselor_id"], [visit_id, counselor_id], id):
        errorMessage += "This counselor is already assigned to this visit.\n"
    

    if errorMessage == "":
        db.insert_visit_counselor(
            data
        )
        return redirect('/visit_counselors')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('visit_counselors/visit_counselors_form.html', data=data)


# -----------------------------
# VALIDATION: Visit_Comments
# -----------------------------
def validate_visit_comments(data, db, id=-1):
    errorMessage = ""

    visit_id = data['visit_id']
    counselor_id = data['counselor_id']
    comment = data['comment']

    if errorMessage == "":
        db.insert_visit_comment(
            data
        )
        return redirect('/visit_comments')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('visit_comments/visit_comments_form.html', data=data)


# -----------------------------
# VALIDATION: Critical_Situations
# -----------------------------
def validate_critical_situations(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    start_date = data['start_date']
    end_date = data['end_date']

    if start_date and end_date and start_date > end_date:
        errorMessage += "End date must be after start date.\n"

    if db.row_exists("Critical_Situations", ["student_id", "start_date"], [student_id, start_date], id):
        errorMessage += "This student is already in a critical situation beginning on this date.\n"
    

    if errorMessage == "":
        db.insert_critical_situation(
            data
        )
        return redirect('/critical_situations')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('critical_situations/critical_situations_form.html', data=data)


# -----------------------------
# VALIDATION: Follow_Ups
# -----------------------------
def validate_follow_ups(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    counselor_id = data['counselor_id']
    date = data['date']
    completed = data['completed']

    errorMessage += validate_bool(completed)

    if db.row_exists("Follow_Ups", ["student_id", "counselor_id", "date"], [student_id, counselor_id, date], id):
        errorMessage += "This student is already scheduled for a follow up with this counselor on this date.\n"
    

    if errorMessage == "":
        completed = True if completed == "Yes" else False

        db.insert_follow_up(
            data
        )
        return redirect('/follow_ups')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('follow_ups/follow_ups_form.html', data=data)


# -----------------------------
# VALIDATION: Tutors
# -----------------------------
def validate_tutors(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    email = data['email']
    specialty = data['specialty']
    age = data['age']
    active = data['active']

    errorMessage += validate_string(name)
    errorMessage += validate_email(email)
    errorMessage += validate_string(specialty)
    errorMessage += validate_int(age)
    errorMessage += validate_bool(active)

    if db.row_exists("Tutors", ["email"], [email], id):
        errorMessage += "This email is already in use by another tutor.\n"
    

    if errorMessage == "":
        age = int(age)
        active = True if active == "Yes" else False

        db.insert_tutor(
            data
        )
        return redirect('/tutors')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('tutors/tutors_form.html', data=data)


# -----------------------------
# VALIDATION: Employment_Events
# -----------------------------
def validate_employment_events(data, db, id=-1):
    errorMessage = ""

    name = data['name']
    date = data['date']
    type_ = data['type']
    location = data['location']

    errorMessage += validate_string(name)
    errorMessage += validate_string(type_)
    errorMessage += validate_string(location)

    if errorMessage == "":
        db.insert_employment_event(
            data
        )
        return redirect('/employment_events')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('employment_events/employment_events_form.html', data=data)


# -----------------------------
# VALIDATION: Healthcare_Referrals
# -----------------------------
def validate_healthcare_referrals(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    provider_id = data['provider_id']
    date = data['date']
    resolution_details = data['resolution_details']

    if errorMessage == "":
        db.insert_healthcare_referral(
            data
        )
        return redirect('/healthcare_referrals')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('healthcare_referrals/healthcare_referrals_form.html', data=data)


# -----------------------------
# VALIDATION: Dean_Referrals
# -----------------------------
def validate_dean_referrals(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    dean_id = data['dean_id']
    date = data['date']
    resolution_details = data['resolution_details']

    if errorMessage == "":
        db.insert_dean_referral(
            data
        )
        return redirect('/dean_referrals')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('dean_referrals/dean_referrals_form.html', data=data)


# -----------------------------
# VALIDATION: Tutor_Referrals
# -----------------------------
def validate_tutor_referrals(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    tutor_id = data['tutor_id']
    date = data['date']
    resolution_details = data['resolution_details']

    if errorMessage == "":
        db.insert_tutor_referral(
            data
        )
        return redirect('/tutor_referrals')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('tutor_referrals/tutor_referrals_form.html', data=data)


# -----------------------------
# VALIDATION: Job_Referrals
# -----------------------------
def validate_job_referrals(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    event_id = data['event_id']
    date = data['date']
    resolution_details = data['resolution_details']

    if errorMessage == "":
        db.insert_job_referral(
            data
        )
        return redirect('/job_referrals')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('job_referrals/job_referrals_form.html', data=data)


# -----------------------------
# VALIDATION: Struggle_Courses
# -----------------------------
def validate_struggle_courses(data, db, id=-1):
    errorMessage = ""

    student_id = data['student_id']
    course_number = data['course_number']

    errorMessage += validate_course(course_number)

    if db.row_exists("Struggle_Courses", ["student_id", "course_number"], [student_id, course_number], id):
        errorMessage += "This student is already struggling with this course.\n"
    

    if errorMessage == "":
        db.insert_struggle_course(
            data
        )
        return redirect('/struggle_courses')

    if errorMessage != "":
        flash(errorMessage)
        return render_template('struggle_courses/struggle_courses_form.html', data=data)