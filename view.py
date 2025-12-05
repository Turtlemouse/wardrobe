# view.py — PROJECT 3510 (NO LOGIN VERSION)

from flask import Flask, render_template, request, redirect, flash, jsonify
import re
import config
from logic import Database
import validation


app = Flask(__name__)
app.secret_key = "shhhhhh"
db = None

app.host = config.APP_HOST
app.port = config.APP_PORT
app.debug = config.APP_DEBUG




# -------------------------------
#       PAGES
# -------------------------------

@app.route('/peopletab')
def people():
    return render_template("navigation/people.html")

@app.route('/visitstab')
def visits():
    return render_template("navigation/visits.html")

@app.route('/followupstab')
def followups():
    return render_template("navigation/followups.html")

@app.route('/misctab')
def misc():
    return render_template("navigation/misc.html")


# ==========================================================
#                          STUDENTS
# ==========================================================

@app.route('/students')
def list_students():
    students = db.get_students()
    return render_template('students/students.html', students=students)


@app.route('/students/new', methods=['GET'])
def new_student_form():
    deans = db.get_deans()  # dean_id is a foreign key
    return render_template('students/students_form.html', student=None, deans=deans)


@app.route('/students/new', methods=['POST'])
def create_student():
    data = request.form.to_dict()

    # Clean SSN (remove dashes/spaces)
    data['ssn'] = data['ssn'].replace("-", "").replace(" ", "")

    db.insert_student(data)
    return redirect('/students')


@app.route('/students/<int:id>/delete')
def delete_student(id):
    db.delete_student(id)
    return redirect('/students')


@app.route('/students/<int:id>/edit', methods=['GET'])
def edit_student_form(id):
    student = db.get_student_by_id(id)
    deans = db.get_deans()
    return render_template('students/students_form.html', student=student, deans=deans)


@app.route('/students/<int:id>/edit', methods=['POST'])
def edit_student(id):
    data = request.form.to_dict()
    data['ssn'] = data['ssn'].replace("-", "").replace(" ", "")

    db.update_student(id, data)
    return redirect('/students')


# ==========================================================
#                     COUNSELORS
# ==========================================================
@app.route('/counselors')
def list_counselors():
    counselors = db.get_counselors()  # TODO
    return render_template('counselors/counselors.html', counselors=counselors)

@app.route('/counselors/new', methods=['GET'])
def new_counselor_form():
    return render_template('counselors/counselors_form.html', counselor=None)

@app.route('/counselors/new', methods=['POST'])
def create_counselor():
    data = request.form

    return validation.validate_counselors(data, db)

@app.route('/counselors/<int:id>/delete')
def delete_counselor(id):
    db.delete_counselor(id)
    return redirect('/counselors')

@app.route('/counselors/<int:id>/edit', methods=['GET'])
def edit_counselor_form(id):
    counselor = db.get_counselor_by_id(id)
    return render_template('counselors/counselors_form.html', counselor=counselor)


@app.route('/counselors/<int:id>/edit', methods=['POST'])
def edit_counselor(id):
    data = request.form.to_dict()

    return validation.validate_counselors(data, db, id)

# ==========================================================
#                COUNSELOR ASSIGNMENTS
# ==========================================================

@app.route('/counselor_assignments')
def list_counselor_assignments():
    assignments = db.get_counselor_assignments()
    print(assignments)
    return render_template(
        'counselor_assignments/counselor_assignments.html',
        assignments=assignments
    )


@app.route('/counselor_assignments/new', methods=['GET'])
def new_counselor_assignment_form():
    students = db.get_students()
    counselors = db.get_counselors()
    return render_template(
        'counselor_assignments/counselor_assignments_form.html',
        assignment=None,
        students=students,
        counselors=counselors
    )


@app.route('/counselor_assignments/new', methods=['POST'])
def create_counselor_assignment():
    student_id = request.form['student_id']
    counselor_id = request.form['counselor_id']
    start_date = request.form['start_date']
    end_date = request.form.get('end_date') or None
    is_primary = 1 if request.form.get('is_primary') else 0

    db.insert_counselor_assignment(student_id, counselor_id, start_date, end_date, is_primary)
    return redirect('/counselor_assignments')


@app.route('/counselor_assignments/<int:assignment_id>/edit', methods=['GET'])
def edit_counselor_assignment_form(assignment_id):
    assignment = db.get_counselor_assignment_by_id(assignment_id)
    students = db.get_students()
    counselors = db.get_counselors()
    return render_template(
        'counselor_assignments/counselor_assignments_form.html',
        assignment=assignment,
        students=students,
        counselors=counselors
    )


@app.route('/counselor_assignments/<int:assignment_id>/edit', methods=['POST'])
def edit_counselor_assignment(assignment_id):
    student_id = request.form['student_id']
    counselor_id = request.form['counselor_id']
    start_date = request.form['start_date']
    end_date = request.form.get('end_date') or None
    is_primary = 1 if request.form.get('is_primary') else 0

    db.update_counselor_assignment(
        assignment_id, student_id, counselor_id,
        start_date, end_date, is_primary
    )

    return redirect('/counselor_assignments')


@app.route('/counselor_assignments/<int:assignment_id>/delete')
def delete_counselor_assignment(assignment_id):
    db.delete_counselor_assignment(assignment_id)
    return redirect('/counselor_assignments')

# ==========================================================
#                     HEALTHCARE_PROVIDERS
# ==========================================================

@app.route('/providers')
def list_providers():
    providers = db.get_providers()
    return render_template('providers/providers.html', providers=providers)


@app.route('/providers/new', methods=['GET'])
def new_provider_form():
    return render_template('providers/providers_form.html', provider=None)


@app.route('/providers/new', methods=['POST'])
def create_provider():
    data = request.form.to_dict()
    db.insert_provider(data)
    return redirect('/providers')


@app.route('/providers/<int:id>/delete')
def delete_provider(id):
    db.delete_provider(id)
    return redirect('/providers')


@app.route('/providers/<int:id>/edit', methods=['GET'])
def edit_provider_form(id):
    provider = db.get_provider_by_id(id)
    return render_template('providers/providers_form.html', provider=provider)


@app.route('/providers/<int:id>/edit', methods=['POST'])
def edit_provider(id):
    data = request.form.to_dict()
    db.update_provider(id, data)
    return redirect('/providers')

# ==========================================================
#                     SYMPTOMS
# ==========================================================

@app.route('/symptoms')
def list_symptoms():
    symptoms = db.get_symptoms()
    return render_template('symptoms/symptoms.html', symptoms=symptoms)


@app.route('/symptoms/new', methods=['GET'])
def new_symptom_form():
    return render_template('symptoms/symptoms_form.html', symptom=None)


@app.route('/symptoms/new', methods=['POST'])
def create_symptom():
    data = request.form.to_dict()
    db.insert_symptom(data)
    return redirect('/symptoms')


@app.route('/symptoms/<int:id>/delete')
def delete_symptom(id):
    db.delete_symptom(id)
    return redirect('/symptoms')


@app.route('/symptoms/<int:id>/edit', methods=['GET'])
def edit_symptom_form(id):
    symptom = db.get_symptom_by_id(id)
    return render_template('symptoms/symptoms_form.html', symptom=symptom)


@app.route('/symptoms/<int:id>/edit', methods=['POST'])
def edit_symptom(id):
    data = request.form.to_dict()
    db.update_symptom(id, data)
    return redirect('/symptoms')

# ==========================================================
#                     DIAGNOSES
# ==========================================================

@app.route('/diagnoses')
def list_diagnoses():
    diagnoses = db.get_diagnoses()
    return render_template('diagnoses/diagnoses.html', diagnoses=diagnoses)


@app.route('/diagnoses/new', methods=['GET'])
def new_diagnosis_form():
    return render_template('diagnoses/diagnoses_form.html', diagnosis=None)


@app.route('/diagnoses/new', methods=['POST'])
def create_diagnosis():
    data = request.form.to_dict()
    db.insert_diagnosis(data)
    return redirect('/diagnoses')


@app.route('/diagnoses/<int:id>/delete')
def delete_diagnosis(id):
    db.delete_diagnosis(id)
    return redirect('/diagnoses')


@app.route('/diagnoses/<int:id>/edit', methods=['GET'])
def edit_diagnosis_form(id):
    diagnosis = db.get_diagnosis_by_id(id)
    return render_template('diagnoses/diagnoses_form.html', diagnosis=diagnosis)


@app.route('/diagnoses/<int:id>/edit', methods=['POST'])
def edit_diagnosis(id):
    data = request.form.to_dict()
    db.update_diagnosis(id, data)
    return redirect('/diagnoses')

# ==========================================================
#                     CATEGORIES
# ==========================================================

@app.route('/categories')
def list_categories():
    categories = db.get_categories()
    return render_template('categories/categories.html', categories=categories)


@app.route('/categories/new', methods=['GET'])
def new_category_form():
    return render_template('categories/categories_form.html', category=None)


@app.route('/categories/new', methods=['POST'])
def create_category():
    data = request.form.to_dict()
    db.insert_category(data)
    return redirect('/categories')


@app.route('/categories/<int:id>/delete')
def delete_category(id):
    db.delete_category(id)
    return redirect('/categories')


@app.route('/categories/<int:id>/edit', methods=['GET'])
def edit_category_form(id):
    category = db.get_category_by_id(id)
    return render_template('categories/categories_form.html', category=category)


@app.route('/categories/<int:id>/edit', methods=['POST'])
def edit_category(id):
    data = request.form.to_dict()
    db.update_category(id, data)
    return redirect('/categories')

# ==========================================================
#                     ISSUES
# ==========================================================

@app.route('/issues')
def list_issues():
    issues = db.get_issues()
    return render_template('issues/issues.html', issues=issues)


@app.route('/issues/new', methods=['GET'])
def new_issue_form():
    diagnoses = db.get_diagnoses()
    students = db.get_students()
    providers = db.get_providers()
    counselors = db.get_counselors()
    visits = db.get_visits_for_dropdown()
    return render_template('issues/issues_form.html', 
                         issue=None,
                         diagnoses=diagnoses,
                         students=students,
                         providers=providers,
                         counselors=counselors,
                         visits=visits)


@app.route('/issues/new', methods=['POST'])
def create_issue():
    data = request.form.to_dict()
    
    # Handle optional foreign keys (empty string to None)
    if not data.get('provider_id'):
        data['provider_id'] = None
    if not data.get('counselor_id'):
        data['counselor_id'] = None
    if not data.get('visit_id'):
        data['visit_id'] = None
    
    db.insert_issue(data)
    return redirect('/issues')


@app.route('/issues/<int:id>/delete')
def delete_issue(id):
    db.delete_issue(id)
    return redirect('/issues')


@app.route('/issues/<int:id>/edit', methods=['GET'])
def edit_issue_form(id):
    issue = db.get_issue_by_id(id)
    diagnoses = db.get_diagnoses()
    students = db.get_students()
    providers = db.get_providers()
    counselors = db.get_counselors()
    visits = db.get_visits_for_dropdown()
    return render_template('issues/issues_form.html',
                         issue=issue,
                         diagnoses=diagnoses,
                         students=students,
                         providers=providers,
                         counselors=counselors,
                         visits=visits)


@app.route('/issues/<int:id>/edit', methods=['POST'])
def edit_issue(id):
    data = request.form.to_dict()
    
    # Handle optional foreign keys (empty string to None)
    if not data.get('provider_id'):
        data['provider_id'] = None
    if not data.get('counselor_id'):
        data['counselor_id'] = None
    if not data.get('visit_id'):
        data['visit_id'] = None
    
    db.update_issue(id, data)
    return redirect('/issues')

# ==========================================================
#                     REPORTED_SYMPTOMS
# ==========================================================

@app.route('/reported_symptoms')
def list_reported_symptoms():
    reported_symptoms = db.get_reported_symptoms()
    return render_template('reported_symptoms/reported_symptoms.html', reported_symptoms=reported_symptoms)


@app.route('/reported_symptoms/new', methods=['GET'])
def new_reported_symptom_form():
    students = db.get_students()
    symptoms = db.get_symptoms()
    return render_template('reported_symptoms/reported_symptoms_form.html',
                         reported_symptom=None,
                         students=students,
                         symptoms=symptoms)


@app.route('/reported_symptoms/new', methods=['POST'])
def create_reported_symptom():
    data = request.form.to_dict()
    db.insert_reported_symptom(data)
    return redirect('/reported_symptoms')


@app.route('/reported_symptoms/<int:id>/delete')
def delete_reported_symptom(id):
    db.delete_reported_symptom(id)
    return redirect('/reported_symptoms')


@app.route('/reported_symptoms/<int:id>/edit', methods=['GET'])
def edit_reported_symptom_form(id):
    reported_symptom = db.get_reported_symptom_by_id(id)
    students = db.get_students()
    symptoms = db.get_symptoms()
    return render_template('reported_symptoms/reported_symptoms_form.html',
                         reported_symptom=reported_symptom,
                         students=students,
                         symptoms=symptoms)


@app.route('/reported_symptoms/<int:id>/edit', methods=['POST'])
def edit_reported_symptom(id):
    data = request.form.to_dict()
    db.update_reported_symptom(id, data)
    return redirect('/reported_symptoms')

# ==========================================================
#                     DIAGNOSIS_CATEGORIZATION
# ==========================================================

@app.route('/diagnosis_categorization')
def list_diagnosis_categorization():
    diagnosis_categorizations = db.get_diagnosis_categorizations()
    return render_template('diagnosis_categorization/diagnosis_categorization.html', 
                         diagnosis_categorizations=diagnosis_categorizations)


@app.route('/diagnosis_categorization/new', methods=['GET'])
def new_diagnosis_categorization_form():
    diagnoses = db.get_diagnoses()
    categories = db.get_categories()
    return render_template('diagnosis_categorization/diagnosis_categorization_form.html',
                         diagnosis_categorization=None,
                         diagnoses=diagnoses,
                         categories=categories)


@app.route('/diagnosis_categorization/new', methods=['POST'])
def create_diagnosis_categorization():
    data = request.form.to_dict()
    db.insert_diagnosis_categorization(data)
    return redirect('/diagnosis_categorization')


@app.route('/diagnosis_categorization/<int:id>/delete')
def delete_diagnosis_categorization(id):
    db.delete_diagnosis_categorization(id)
    return redirect('/diagnosis_categorization')


@app.route('/diagnosis_categorization/<int:id>/edit', methods=['GET'])
def edit_diagnosis_categorization_form(id):
    diagnosis_categorization = db.get_diagnosis_categorization_by_id(id)
    diagnoses = db.get_diagnoses()
    categories = db.get_categories()
    return render_template('diagnosis_categorization/diagnosis_categorization_form.html',
                         diagnosis_categorization=diagnosis_categorization,
                         diagnoses=diagnoses,
                         categories=categories)


@app.route('/diagnosis_categorization/<int:id>/edit', methods=['POST'])
def edit_diagnosis_categorization(id):
    data = request.form.to_dict()
    db.update_diagnosis_categorization(id, data)
    return redirect('/diagnosis_categorization')

# ==========================================================
#                     SYMPTOM_CATEGORIZATION
# ==========================================================

@app.route('/symptom_categorization')
def list_symptom_categorization():
    symptom_categorizations = db.get_symptom_categorizations()
    return render_template('symptom_categorization/symptom_categorization.html', 
                         symptom_categorizations=symptom_categorizations)


@app.route('/symptom_categorization/new', methods=['GET'])
def new_symptom_categorization_form():
    symptoms = db.get_symptoms()
    categories = db.get_categories()
    return render_template('symptom_categorization/symptom_categorization_form.html',
                         symptom_categorization=None,
                         symptoms=symptoms,
                         categories=categories)


@app.route('/symptom_categorization/new', methods=['POST'])
def create_symptom_categorization():
    data = request.form.to_dict()
    db.insert_symptom_categorization(data)
    return redirect('/symptom_categorization')


@app.route('/symptom_categorization/<int:id>/delete')
def delete_symptom_categorization(id):
    db.delete_symptom_categorization(id)
    return redirect('/symptom_categorization')


@app.route('/symptom_categorization/<int:id>/edit', methods=['GET'])
def edit_symptom_categorization_form(id):
    symptom_categorization = db.get_symptom_categorization_by_id(id)
    symptoms = db.get_symptoms()
    categories = db.get_categories()
    return render_template('symptom_categorization/symptom_categorization_form.html',
                         symptom_categorization=symptom_categorization,
                         symptoms=symptoms,
                         categories=categories)


@app.route('/symptom_categorization/<int:id>/edit', methods=['POST'])
def edit_symptom_categorization(id):
    data = request.form.to_dict()
    db.update_symptom_categorization(id, data)
    return redirect('/symptom_categorization')

# ==========================================================
#                     VISITS
# ==========================================================

@app.route('/visits')
def list_visits():
    visits = db.get_visits()
    return render_template('visits/visits.html', visits=visits)


@app.route('/visits/new', methods=['GET'])
def new_visit_form():
    students = db.get_students()
    return render_template('visits/visits_form.html', visit=None, students=students)


@app.route('/visits/new', methods=['POST'])
def create_visit():
    data = request.form.to_dict()
    db.insert_visit(data)
    return redirect('/visits')


@app.route('/visits/<int:id>/delete')
def delete_visit(id):
    db.delete_visit(id)
    return redirect('/visits')


@app.route('/visits/<int:id>/edit', methods=['GET'])
def edit_visit_form(id):
    visit = db.get_visit_by_id(id)
    students = db.get_students()
    return render_template('visits/visits_form.html', visit=visit, students=students)


@app.route('/visits/<int:id>/edit', methods=['POST'])
def edit_visit(id):
    data = request.form.to_dict()
    db.update_visit(id, data)
    return redirect('/visits')

# ==========================================================
#                     VISITS_COUNSELORS
# ==========================================================

@app.route('/visit_counselors')
def list_visit_counselors():
    visit_counselors = db.get_visit_counselors()
    return render_template('visit_counselors/visit_counselors.html', visit_counselors=visit_counselors)


@app.route('/visit_counselors/new', methods=['GET'])
def new_visit_counselor_form():
    visits = db.get_visits_for_dropdown()
    counselors = db.get_counselors()
    return render_template('visit_counselors/visit_counselors_form.html',
                         visit_counselor=None,
                         visits=visits,
                         counselors=counselors)


@app.route('/visit_counselors/new', methods=['POST'])
def create_visit_counselor():
    data = request.form.to_dict()
    db.insert_visit_counselor(data)
    return redirect('/visit_counselors')


@app.route('/visit_counselors/<int:id>/delete')
def delete_visit_counselor(id):
    db.delete_visit_counselor(id)
    return redirect('/visit_counselors')


@app.route('/visit_counselors/<int:id>/edit', methods=['GET'])
def edit_visit_counselor_form(id):
    visit_counselor = db.get_visit_counselor_by_id(id)
    visits = db.get_visits_for_dropdown()
    counselors = db.get_counselors()
    return render_template('visit_counselors/visit_counselors_form.html',
                         visit_counselor=visit_counselor,
                         visits=visits,
                         counselors=counselors)


@app.route('/visit_counselors/<int:id>/edit', methods=['POST'])
def edit_visit_counselor(id):
    data = request.form.to_dict()
    db.update_visit_counselor(id, data)
    return redirect('/visit_counselors')

# ==========================================================
#                     VISITS_COMMENTS
# ==========================================================

@app.route('/visit_comments')
def list_visit_comments():
    visit_comments = db.get_visit_comments()
    return render_template('visit_comments/visit_comments.html', visit_comments=visit_comments)


@app.route('/visit_comments/new', methods=['GET'])
def new_visit_comment_form():
    visit_counselors = db.get_visit_counselors()  # Get existing visit-counselor pairs
    return render_template('visit_comments/visit_comments_form.html',
                         visit_comment=None,
                         visit_counselors=visit_counselors)


@app.route('/visit_comments/new', methods=['POST'])
def create_visit_comment():
    data = request.form.to_dict()
    db.insert_visit_comment(data)
    return redirect('/visit_comments')


@app.route('/visit_comments/<int:id>/delete')
def delete_visit_comment(id):
    db.delete_visit_comment(id)
    return redirect('/visit_comments')


@app.route('/visit_comments/<int:id>/edit', methods=['GET'])
def edit_visit_comment_form(id):
    visit_comment = db.get_visit_comment_by_id(id)
    visit_counselors = db.get_visit_counselors()  # Get existing visit-counselor pairs
    return render_template('visit_comments/visit_comments_form.html',
                         visit_comment=visit_comment,
                         visit_counselors=visit_counselors)


@app.route('/visit_comments/<int:id>/edit', methods=['POST'])
def edit_visit_comment(id):
    data = request.form.to_dict()
    db.update_visit_comment(id, data)
    return redirect('/visit_comments')

# ==========================================================
#                     CRITICAL_SITUATIONS
# ==========================================================

@app.route('/critical_situations')
def list_critical_situations():
    critical_situations = db.get_critical_situations()
    return render_template('critical_situations/critical_situations.html', 
                         critical_situations=critical_situations)


@app.route('/critical_situations/new', methods=['GET'])
def new_critical_situation_form():
    students = db.get_students()
    return render_template('critical_situations/critical_situations_form.html',
                         critical_situation=None,
                         students=students)


@app.route('/critical_situations/new', methods=['POST'])
def create_critical_situation():
    data = request.form.to_dict()
    
    # Handle optional end_date (empty string to None)
    if not data.get('end_date'):
        data['end_date'] = None
    
    db.insert_critical_situation(data)
    return redirect('/critical_situations')


@app.route('/critical_situations/<int:id>/delete')
def delete_critical_situation(id):
    db.delete_critical_situation(id)
    return redirect('/critical_situations')


@app.route('/critical_situations/<int:id>/edit', methods=['GET'])
def edit_critical_situation_form(id):
    critical_situation = db.get_critical_situation_by_id(id)
    students = db.get_students()
    return render_template('critical_situations/critical_situations_form.html',
                         critical_situation=critical_situation,
                         students=students)


@app.route('/critical_situations/<int:id>/edit', methods=['POST'])
def edit_critical_situation(id):
    data = request.form.to_dict()
    
    # Handle optional end_date (empty string to None)
    if not data.get('end_date'):
        data['end_date'] = None
    
    db.update_critical_situation(id, data)
    return redirect('/critical_situations')

# ==========================================================
#                     FOLLOW_UPS
# ==========================================================

@app.route('/followups')
def list_followups():
    followups = db.get_followups()
    return render_template('followups/followups.html', followups=followups)


@app.route('/followups/new', methods=['GET'])
def new_followup_form():
    students = db.get_students()
    counselors = db.get_counselors()
    return render_template('followups/followups_form.html',
                         followup=None,
                         students=students,
                         counselors=counselors)


@app.route('/followups/new', methods=['POST'])
def create_followup():
    data = request.form.to_dict()
    db.insert_followup(data)
    return redirect('/followups')


@app.route('/followups/<int:id>/delete')
def delete_followup(id):
    db.delete_followup(id)
    return redirect('/followups')


@app.route('/followups/<int:id>/edit', methods=['GET'])
def edit_followup_form(id):
    followup = db.get_followup_by_id(id)
    students = db.get_students()
    counselors = db.get_counselors()
    return render_template('followups/followups_form.html',
                         followup=followup,
                         students=students,
                         counselors=counselors)


@app.route('/followups/<int:id>/edit', methods=['POST'])
def edit_followup(id):
    data = request.form.to_dict()
    db.update_followup(id, data)
    return redirect('/followups')

# ==========================================================
#                           DEANS
# ==========================================================

@app.route('/deans')
def list_deans():
    deans = db.get_deans()
    return render_template('deans/deans.html', deans=deans)


@app.route('/deans/new', methods=['GET'])
def new_dean_form():
    return render_template('deans/deans_form.html')


@app.route('/deans/new', methods=['POST'])
def create_dean():
    data = request.form.to_dict()
    db.insert_dean(data)
    return redirect('/deans')


@app.route('/deans/<int:id>/delete')
def delete_dean(id):
    db.delete_dean(id)
    return redirect('/deans')


@app.route('/deans/<int:id>/edit', methods=['GET'])
def edit_dean_form(id):
    dean = db.get_dean_by_id(id)
    return render_template("deans/deans_form.html", dean=dean)


@app.route('/deans/<int:id>/edit', methods=['POST'])
def edit_dean(id):
    data = request.form.to_dict()
    db.update_dean(id, data)
    return redirect('/deans')


# ==========================================================
#                     TUTORS
# ==========================================================

@app.route('/tutors')
def list_tutors():
    tutors = db.get_tutors()
    return render_template('tutors/tutors.html', tutors=tutors)


@app.route('/tutors/new', methods=['GET'])
def new_tutor_form():
    return render_template('tutors/tutors_form.html', tutor=None)


@app.route('/tutors/new', methods=['POST'])
def create_tutor():
    data = request.form.to_dict()
    db.insert_tutor(data)
    return redirect('/tutors')


@app.route('/tutors/<int:id>/delete')
def delete_tutor(id):
    db.delete_tutor(id)
    return redirect('/tutors')


@app.route('/tutors/<int:id>/edit', methods=['GET'])
def edit_tutor_form(id):
    tutor = db.get_tutor_by_id(id)
    return render_template('tutors/tutors_form.html', tutor=tutor)


@app.route('/tutors/<int:id>/edit', methods=['POST'])
def edit_tutor(id):
    data = request.form.to_dict()
    db.update_tutor(id, data)
    return redirect('/tutors')

# ==========================================================
#                     EMPLOYMENT_EVENTS
# ==========================================================

@app.route('/employment_events')
def list_employment_events():
    employment_events = db.get_employment_events()
    return render_template('employment_events/employment_events.html', 
                         employment_events=employment_events)


@app.route('/employment_events/new', methods=['GET'])
def new_employment_event_form():
    return render_template('employment_events/employment_events_form.html', 
                         employment_event=None)


@app.route('/employment_events/new', methods=['POST'])
def create_employment_event():
    data = request.form.to_dict()
    db.insert_employment_event(data)
    return redirect('/employment_events')


@app.route('/employment_events/<int:id>/delete')
def delete_employment_event(id):
    db.delete_employment_event(id)
    return redirect('/employment_events')


@app.route('/employment_events/<int:id>/edit', methods=['GET'])
def edit_employment_event_form(id):
    employment_event = db.get_employment_event_by_id(id)
    return render_template('employment_events/employment_events_form.html', 
                         employment_event=employment_event)


@app.route('/employment_events/<int:id>/edit', methods=['POST'])
def edit_employment_event(id):
    data = request.form.to_dict()
    db.update_employment_event(id, data)
    return redirect('/employment_events')

# ==========================================================
#                     HEALTHCARE_REFERRALS
# ==========================================================

@app.route('/healthcare_referrals')
def list_healthcare_referrals():
    healthcare_referrals = db.get_healthcare_referrals()
    return render_template('healthcare_referrals/healthcare_referrals.html', 
                         healthcare_referrals=healthcare_referrals)


@app.route('/healthcare_referrals/new', methods=['GET'])
def new_healthcare_referral_form():
    students = db.get_students()
    providers = db.get_providers()
    return render_template('healthcare_referrals/healthcare_referrals_form.html',
                         healthcare_referral=None,
                         students=students,
                         providers=providers)


@app.route('/healthcare_referrals/new', methods=['POST'])
def create_healthcare_referral():
    data = request.form.to_dict()
    db.insert_healthcare_referral(data)
    return redirect('/healthcare_referrals')


@app.route('/healthcare_referrals/<int:id>/delete')
def delete_healthcare_referral(id):
    db.delete_healthcare_referral(id)
    return redirect('/healthcare_referrals')


@app.route('/healthcare_referrals/<int:id>/edit', methods=['GET'])
def edit_healthcare_referral_form(id):
    healthcare_referral = db.get_healthcare_referral_by_id(id)
    students = db.get_students()
    providers = db.get_providers()
    return render_template('healthcare_referrals/healthcare_referrals_form.html',
                         healthcare_referral=healthcare_referral,
                         students=students,
                         providers=providers)


@app.route('/healthcare_referrals/<int:id>/edit', methods=['POST'])
def edit_healthcare_referral(id):
    data = request.form.to_dict()
    db.update_healthcare_referral(id, data)
    return redirect('/healthcare_referrals')

# ==========================================================
#                     DEAN_REFERRALS
# ==========================================================

@app.route('/dean_referrals')
def list_dean_referrals():
    dean_referrals = db.get_dean_referrals()
    return render_template('dean_referrals/dean_referrals.html', 
                         dean_referrals=dean_referrals)


@app.route('/dean_referrals/new', methods=['GET'])
def new_dean_referral_form():
    students = db.get_students()
    deans = db.get_deans()
    return render_template('dean_referrals/dean_referrals_form.html',
                         dean_referral=None,
                         students=students,
                         deans=deans)


@app.route('/dean_referrals/new', methods=['POST'])
def create_dean_referral():
    data = request.form.to_dict()
    db.insert_dean_referral(data)
    return redirect('/dean_referrals')


@app.route('/dean_referrals/<int:id>/delete')
def delete_dean_referral(id):
    db.delete_dean_referral(id)
    return redirect('/dean_referrals')


@app.route('/dean_referrals/<int:id>/edit', methods=['GET'])
def edit_dean_referral_form(id):
    dean_referral = db.get_dean_referral_by_id(id)
    students = db.get_students()
    deans = db.get_deans()
    return render_template('dean_referrals/dean_referrals_form.html',
                         dean_referral=dean_referral,
                         students=students,
                         deans=deans)


@app.route('/dean_referrals/<int:id>/edit', methods=['POST'])
def edit_dean_referral(id):
    data = request.form.to_dict()
    db.update_dean_referral(id, data)
    return redirect('/dean_referrals')

# ==========================================================
#                     TUTOR_REFFERALS
# ==========================================================

@app.route('/tutor_referrals')
def list_tutor_referrals():
    tutor_referrals = db.get_tutor_referrals()
    return render_template('tutor_referrals/tutor_referrals.html', 
                         tutor_referrals=tutor_referrals)


@app.route('/tutor_referrals/new', methods=['GET'])
def new_tutor_referral_form():
    students = db.get_students()
    tutors = db.get_tutors()
    return render_template('tutor_referrals/tutor_referrals_form.html',
                         tutor_referral=None,
                         students=students,
                         tutors=tutors)


@app.route('/tutor_referrals/new', methods=['POST'])
def create_tutor_referral():
    data = request.form.to_dict()
    db.insert_tutor_referral(data)
    return redirect('/tutor_referrals')


@app.route('/tutor_referrals/<int:id>/delete')
def delete_tutor_referral(id):
    db.delete_tutor_referral(id)
    return redirect('/tutor_referrals')


@app.route('/tutor_referrals/<int:id>/edit', methods=['GET'])
def edit_tutor_referral_form(id):
    tutor_referral = db.get_tutor_referral_by_id(id)
    students = db.get_students()
    tutors = db.get_tutors()
    return render_template('tutor_referrals/tutor_referrals_form.html',
                         tutor_referral=tutor_referral,
                         students=students,
                         tutors=tutors)


@app.route('/tutor_referrals/<int:id>/edit', methods=['POST'])
def edit_tutor_referral(id):
    data = request.form.to_dict()
    db.update_tutor_referral(id, data)
    return redirect('/tutor_referrals')

# ==========================================================
#                     JOB_REFERRALS
# ==========================================================

@app.route('/job_referrals')
def list_job_referrals():
    job_referrals = db.get_job_referrals()
    return render_template('job_referrals/job_referrals.html', 
                         job_referrals=job_referrals)


@app.route('/job_referrals/new', methods=['GET'])
def new_job_referral_form():
    students = db.get_students()
    employment_events = db.get_employment_events()
    return render_template('job_referrals/job_referrals_form.html',
                         job_referral=None,
                         students=students,
                         employment_events=employment_events)


@app.route('/job_referrals/new', methods=['POST'])
def create_job_referral():
    data = request.form.to_dict()
    db.insert_job_referral(data)
    return redirect('/job_referrals')


@app.route('/job_referrals/<int:id>/delete')
def delete_job_referral(id):
    db.delete_job_referral(id)
    return redirect('/job_referrals')


@app.route('/job_referrals/<int:id>/edit', methods=['GET'])
def edit_job_referral_form(id):
    job_referral = db.get_job_referral_by_id(id)
    students = db.get_students()
    employment_events = db.get_employment_events()
    return render_template('job_referrals/job_referrals_form.html',
                         job_referral=job_referral,
                         students=students,
                         employment_events=employment_events)


@app.route('/job_referrals/<int:id>/edit', methods=['POST'])
def edit_job_referral(id):
    data = request.form.to_dict()
    db.update_job_referral(id, data)
    return redirect('/job_referrals')

# ==========================================================
#                     STRUGGLE_COURSES
# ==========================================================

@app.route('/struggle_courses')
def list_struggle_courses():
    struggle_courses = db.get_struggle_courses()
    return render_template('struggle_courses/struggle_courses.html', 
                         struggle_courses=struggle_courses)


@app.route('/struggle_courses/new', methods=['GET'])
def new_struggle_course_form():
    students = db.get_students()
    return render_template('struggle_courses/struggle_courses_form.html',
                         struggle_course=None,
                         students=students)


@app.route('/struggle_courses/new', methods=['POST'])
def create_struggle_course():
    data = request.form.to_dict()
    db.insert_struggle_course(data)
    return redirect('/struggle_courses')


@app.route('/struggle_courses/<int:id>/delete')
def delete_struggle_course(id):
    db.delete_struggle_course(id)
    return redirect('/struggle_courses')


@app.route('/struggle_courses/<int:id>/edit', methods=['GET'])
def edit_struggle_course_form(id):
    struggle_course = db.get_struggle_course_by_id(id)
    students = db.get_students()
    return render_template('struggle_courses/struggle_courses_form.html',
                         struggle_course=struggle_course,
                         students=students)


@app.route('/struggle_courses/<int:id>/edit', methods=['POST'])
def edit_struggle_course(id):
    data = request.form.to_dict()
    db.update_struggle_course(id, data)
    return redirect('/struggle_courses')



# ==========================================================
#              DATABASE SCHEMA HELPERS
# ==========================================================

def get_all_tables(db):
    """Get list of all tables in the database"""
    sql = """
    SELECT TABLE_NAME 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = DATABASE()
    ORDER BY TABLE_NAME;
    """
    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        # DictCursor returns [{'TABLE_NAME': 'Students'}, {'TABLE_NAME': 'Counselors'}, ...]
        return [row['TABLE_NAME'] for row in results]

def get_table_columns(db, table_name):
    """Get list of all columns for a specific table"""
    sql = """
    SELECT COLUMN_NAME 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = %s
    ORDER BY ORDINAL_POSITION;
    """
    with db.conn.cursor() as cur:
        cur.execute(sql, (table_name,))
        results = cur.fetchall()
        # DictCursor returns [{'COLUMN_NAME': 'student_id'}, {'COLUMN_NAME': 'first_name'}, ...]
        return [row['COLUMN_NAME'] for row in results]

def get_distinct_values(db, table_name, column_name, limit=100):
    """Get distinct values from a column for dropdown options"""
    sql = f"""
    SELECT DISTINCT {column_name}
    FROM {table_name}
    WHERE {column_name} IS NOT NULL
    ORDER BY {column_name}
    LIMIT %s;
    """
    with db.conn.cursor() as cur:
        cur.execute(sql, (limit,))
        results = cur.fetchall()
        # DictCursor returns [{column_name: value}, ...]
        return [row[column_name] for row in results]

# ==========================================================
#              QUERIES (FIXED FOR db.conn AND DictCursor)
# ==========================================================

def mode_of_attribute(db, table_name, column_name):
    sql = f"""
    SELECT {column_name}
    FROM {table_name}
    GROUP BY {column_name}
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    """
    
    with db.conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()
        return result[column_name] if result else None

def get_every_distinct_value_from_a_column(db, table_name, column_name):
    sql = f"""
    SELECT DISTINCT {column_name}
    FROM {table_name};
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        return [row[column_name] for row in results]
    

def get_counts_groupby_column_distinct(
    db,
    base_table,
    display_join_on,
    display_table,
    display_col,
    distinct_col
):
    sql = f"""
    SELECT d.{display_col}, COUNT(DISTINCT b.{distinct_col}) AS cnt
    FROM {base_table} b
    JOIN {display_table} d
        ON b.{display_join_on} = d.{display_join_on}
    GROUP BY d.{display_col}
    ORDER BY cnt DESC;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        return [(row[display_col], row['cnt']) for row in results]
    
def get_distinct_values_via_two_joins(
    db,
    base_table,              # e.g. "Issues"
    display_join_on,         # e.g. "diagnosis_id"
    display_table,           # e.g. "Diagnoses"
    display_col,             # e.g. "diagnosis"
    filter_join_on,          # e.g. "student_id"
    filter_table,            # e.g. "Students"
    filter_col,              # e.g. "name"
    filter_value
):

    sql = f"""
    SELECT DISTINCT d.{display_col}
    FROM {base_table} b
    JOIN {filter_table} f
        ON b.{filter_join_on} = f.{filter_join_on}
    JOIN {display_table} d
        ON b.{display_join_on} = d.{display_join_on}
    WHERE f.{filter_col} = %s;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql, (filter_value,))
        results = cur.fetchall()
        return [row[display_col] for row in results]
    

def count_unique_students_by_issue_category(db):
    sql = """
    SELECT
        c.category_id,
        c.category,
        COUNT(DISTINCT i.student_id) AS student_count
    FROM Issues i
    JOIN Diagnosis_Categorization dc
        ON i.diagnosis_id = dc.diagnosis_id
    JOIN Categories c
        ON dc.category_id = c.category_id
    GROUP BY c.category_id, c.category
    ORDER BY student_count DESC;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        return [(row['category_id'], row['category'], row['student_count']) for row in results]

def get_distinct_values_given_NOT_another_attribute(db, table_name, select_col, filter_col, filter_value):
    sql = f"""
    SELECT DISTINCT {select_col}
    FROM {table_name}
    WHERE {filter_col} != %s;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql, (filter_value,))
        results = cur.fetchall()
        return [row[select_col] for row in results]

def get_distinct_values_via_two_joins_NOT(
    db,
    base_table,              # e.g. "Issues"
    display_join_on,         # e.g. "diagnosis_id"
    display_table,           # e.g. "Diagnoses"
    display_col,             # e.g. "diagnosis"
    filter_join_on,          # e.g. "student_id"
    filter_table,            # e.g. "Students"
    filter_col,              # e.g. "name"
    filter_value
):

    sql = f"""
    SELECT DISTINCT d.{display_col}
    FROM {base_table} b
    JOIN {filter_table} f
        ON b.{filter_join_on} = f.{filter_join_on}
    JOIN {display_table} d
        ON b.{display_join_on} = d.{display_join_on}
    WHERE f.{filter_col} != %s;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql, (filter_value,))
        results = cur.fetchall()
        return [row[display_col] for row in results]

def get_salary_stats_of_salaried(db):
    """
    Returns (min_salary, max_salary, avg_salary)
    """
    sql = """
    SELECT
        MIN(salary) as min_salary,
        MAX(salary) as max_salary,
        AVG(salary) as avg_salary
    FROM Counselors
    WHERE salary IS NOT NULL AND salary > 0;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()
        return (result['min_salary'], result['max_salary'], result['avg_salary']) if result else (None, None, None)
    
def get_students_who_have_multiple_issues(db):
    sql = """
    SELECT
        i.student_id,
        s.name,
        COUNT(*) AS cnt
    FROM Issues i
    JOIN Students s
        ON i.student_id = s.student_id
    GROUP BY
        i.student_id,
        s.name
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        return [(row['student_id'], row['name'], row['cnt']) for row in results]
    
def get_students_who_have_given_symptom(db, symptom_name):
    sql = """
    SELECT DISTINCT
        s.student_id,
        s.name
    FROM Reported_Symptoms rs
    JOIN Symptoms sy
        ON rs.symptom_id = sy.symptom_id
    JOIN Students s
        ON rs.student_id = s.student_id
    WHERE sy.symptom = %s;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql, (symptom_name,))
        results = cur.fetchall()
        return [(row['student_id'], row['name']) for row in results]
    
def count_students_with_issues_by_zip(db):
    sql = """
    SELECT
        s.zip,
        COUNT(DISTINCT s.student_id) AS student_count
    FROM Students s
    JOIN Issues i
        ON s.student_id = i.student_id
    GROUP BY s.zip
    ORDER BY student_count DESC;
    """

    with db.conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        return [(row['zip'], row['student_count']) for row in results]

# ==========================================================
#              HELPER FUNCTIONS FOR FORMATTING
# ==========================================================

def format_result(result, query_type):
    """Format query results for display"""
    if result is None:
        return "No results found"
    
    if query_type == 'single_value':
        return str(result)
    
    elif query_type == 'list':
        if not result:
            return "No results found"
        return ", ".join(str(item) for item in result)
    
    elif query_type == 'table':
        if not result:
            return "No results found"
        # Format as HTML table
        html = "<table style='width:100%; border-collapse: collapse; margin-top: 10px;'>"
        for i, row in enumerate(result):
            html += "<tr>"
            for cell in row:
                tag = "th" if i == 0 else "td"
                style = "border: 1px solid #ddd; padding: 8px; text-align: left;"
                if i == 0:
                    style += " background-color: #667eea; color: white; font-weight: bold;"
                html += f"<{tag} style='{style}'>{cell}</{tag}>"
            html += "</tr>"
        html += "</table>"
        return html
    
    elif query_type == 'salary_stats':
        min_sal, max_sal, avg_sal = result
        if min_sal is None:
            return "No salary data found"
        return f"Min: ${min_sal:,.2f} | Max: ${max_sal:,.2f} | Avg: ${avg_sal:,.2f}"
    
    return str(result)

# ==========================================================
#              QUERY HANDLING WRAPPER (FIXED PARAMETER NAMES)
# ==========================================================

FUNCTIONS = {
    'Most Common': {
        'function': lambda table_name, column_name: format_result(
            mode_of_attribute(db, table_name, column_name), 'single_value'
        ),
        'params': [
            {'name': 'table_name', 'type': 'table', 'label': 'Table Name'},
            {'name': 'column_name', 'type': 'column', 'label': 'Column Name', 'depends_on': 'table_name'}
        ]
    },
    'Get Distinct': {
        'function': lambda table_name, column_name: format_result(
            get_every_distinct_value_from_a_column(db, table_name, column_name), 'list'
        ),
        'params': [
            {'name': 'table_name', 'type': 'table', 'label': 'Table Name'},
            {'name': 'column_name', 'type': 'column', 'label': 'Column Name', 'depends_on': 'table_name'}
        ]
    },
    'Count Distinct Groupby': {
        'function': lambda base_table, display_join_on, display_table, display_col, distinct_col: format_result(
            get_counts_groupby_column_distinct(db, base_table, display_join_on, display_table, display_col, distinct_col), 'table'
        ),
        'params': [
            {'name': 'base_table', 'type': 'table', 'label': 'Base Table'},
            {'name': 'display_join_on', 'type': 'column', 'label': 'Join Column', 'depends_on': 'base_table'},
            {'name': 'display_table', 'type': 'table', 'label': 'Display Table'},
            {'name': 'display_col', 'type': 'column', 'label': 'Display Column', 'depends_on': 'display_table'},
            {'name': 'distinct_col', 'type': 'column', 'label': 'Count Distinct Column', 'depends_on': 'base_table'}
        ]
    },
    'Get Two Joins': {
        'function': lambda base_table, display_join_on, display_table, display_col, filter_join_on, filter_table, filter_col, filter_value: format_result(
            get_distinct_values_via_two_joins(db, base_table, display_join_on, display_table, display_col, filter_join_on, filter_table, filter_col, filter_value), 'list'
        ),
        'params': [
            {'name': 'base_table', 'type': 'table', 'label': 'Base Table'},
            {'name': 'display_join_on', 'type': 'column', 'label': 'Display Join Column', 'depends_on': 'base_table'},
            {'name': 'display_table', 'type': 'table', 'label': 'Display Table'},
            {'name': 'display_col', 'type': 'column', 'label': 'Display Column', 'depends_on': 'display_table'},
            {'name': 'filter_join_on', 'type': 'column', 'label': 'Filter Join Column', 'depends_on': 'base_table'},
            {'name': 'filter_table', 'type': 'table', 'label': 'Filter Table'},
            {'name': 'filter_col', 'type': 'column', 'label': 'Filter Column', 'depends_on': 'filter_table'},
            {'name': 'filter_value', 'type': 'str', 'label': 'Filter Value'}
        ]
    },
    'Count Unique Students by Issue Category': {
        'function': lambda: format_result(
            count_unique_students_by_issue_category(db), 'table'
        ),
        'params': []
    },
    'Get Distinct Given NOT Attribute': {
        'function': lambda table_name, select_col, filter_col, filter_value: format_result(
            get_distinct_values_given_NOT_another_attribute(db, table_name, select_col, filter_col, filter_value), 'list'
        ),
        'params': [
            {'name': 'table_name', 'type': 'table', 'label': 'Table Name'},
            {'name': 'select_col', 'type': 'column', 'label': 'Select Column', 'depends_on': 'table_name'},
            {'name': 'filter_col', 'type': 'column', 'label': 'Filter Column', 'depends_on': 'table_name'},
            {'name': 'filter_value', 'type': 'str', 'label': 'Filter Value'}
        ]
    },
    'Get Two Joins (NOT)': {
        'function': lambda base_table, display_join_on, display_table, display_col, filter_join_on, filter_table, filter_col, filter_value: format_result(
            get_distinct_values_via_two_joins_NOT(db, base_table, display_join_on, display_table, display_col, filter_join_on, filter_table, filter_col, filter_value), 'list'
        ),
        'params': [
            {'name': 'base_table', 'type': 'table', 'label': 'Base Table'},
            {'name': 'display_join_on', 'type': 'column', 'label': 'Display Join Column', 'depends_on': 'base_table'},
            {'name': 'display_table', 'type': 'table', 'label': 'Display Table'},
            {'name': 'display_col', 'type': 'column', 'label': 'Display Column', 'depends_on': 'display_table'},
            {'name': 'filter_join_on', 'type': 'column', 'label': 'Filter Join Column', 'depends_on': 'base_table'},
            {'name': 'filter_table', 'type': 'table', 'label': 'Filter Table'},
            {'name': 'filter_col', 'type': 'column', 'label': 'Filter Column', 'depends_on': 'filter_table'},
            {'name': 'filter_value', 'type': 'str', 'label': 'Filter Value'}
        ]
    },
    'Counselor Salary Stats': {
        'function': lambda: format_result(
            get_salary_stats_of_salaried(db), 'salary_stats'
        ),
        'params': []
    },
    'Get Students With Multiple Issues': {
        'function': lambda: format_result(
            get_students_who_have_multiple_issues(db), 'table'
        ),
        'params': []
    },
    'Get Students By Symptom': {
        'function': lambda symptom_name: format_result(
            get_students_who_have_given_symptom(db, symptom_name), 'table'
        ),
        'params': [
            {'name': 'symptom_name', 'type': 'value_from_column', 'label': 'Symptom Name', 
             'source_table': 'Symptoms', 'source_column': 'symptom'}
        ]
    },
    'Count Students With Issues (by Zip)': {
        'function': lambda: format_result(
            count_students_with_issues_by_zip(db), 'table'
        ),
        'params': []
    }
}

# ==========================================================
#              FLASK ROUTES
# ==========================================================

@app.route('/')
def index():
    return render_template('home.html', functions=FUNCTIONS)

@app.route('/get_params/<function_name>')
def get_params(function_name):
    """Return parameters for a specific function"""
    print(f"Getting params for: {function_name}")
    if function_name in FUNCTIONS:
        params = FUNCTIONS[function_name]['params']
        print(f"Returning params: {params}")
        return jsonify(params)
    print(f"Function not found: {function_name}")
    return jsonify([])

@app.route('/get_tables')
def get_tables():
    """Return list of all tables"""
    try:
        tables = get_all_tables(db)
        print(f"Tables found: {tables}")  # Debug log
        return jsonify(tables)
    except Exception as e:
        print(f"Error getting tables: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_columns/<table_name>')
def get_columns(table_name):
    """Return list of columns for a specific table"""
    try:
        columns = get_table_columns(db, table_name)
        print(f"Columns for {table_name}: {columns}")  # Debug log
        return jsonify(columns)
    except Exception as e:
        print(f"Error getting columns: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/get_column_values/<table_name>/<column_name>')
def get_column_values(table_name, column_name):
    """Return distinct values from a specific column"""
    try:
        values = get_distinct_values(db, table_name, column_name)
        print(f"Values for {table_name}.{column_name}: {len(values)} values")  # Debug log
        return jsonify(values)
    except Exception as e:
        print(f"Error getting column values: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/execute', methods=['POST'])
def execute():
    """Execute the selected function with provided parameters"""
    data = request.json
    function_name = data.get('function_name')
    params = data.get('params', {})
    
    print(f"Executing: {function_name} with params: {params}")
    
    if function_name not in FUNCTIONS:
        return jsonify({'error': 'Function not found'}), 404
    
    try:
        func_info = FUNCTIONS[function_name]
        
        # Convert parameters to appropriate types
        converted_params = {}
        for param_info in func_info['params']:
            param_name = param_info['name']
            param_type = param_info['type']
            param_value = params.get(param_name)
            
            if param_type == 'int':
                converted_params[param_name] = int(param_value)
            elif param_type == 'float':
                converted_params[param_name] = float(param_value)
            else:
                converted_params[param_name] = str(param_value)
        
        # Execute the function
        result = func_info['function'](**converted_params)
        print(f"Result: {result}")
        return jsonify({'result': result})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


# ==========================================================
#              START FLASK APP
# ==========================================================
if __name__ == '__main__':
    app.run(host=app.host, port=app.port, debug=app.debug)


