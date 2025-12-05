
-- Clean slate: drop and recreate database
DROP DATABASE IF EXISTS project3510;
CREATE DATABASE project3510;
USE project3510;

-- Create dedicated user with privileges
GRANT ALL ON project3510.* TO root@localhost IDENTIFIED BY 'Aa@12345678';

-- Always a good idea before creating FKs in a fresh schema
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- Deans
-- ============================================
CREATE TABLE Deans (
    dean_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    school VARCHAR(255),
    title VARCHAR(255),
    `active` BOOL DEFAULT TRUE,
    CONSTRAINT uq_deans_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Students
-- ============================================
CREATE TABLE Students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    ssn VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    country_of_birth VARCHAR(255),
    gender VARCHAR(50),
    grad_year INT,
    insurance_provider VARCHAR(255),
    race VARCHAR(255),
    zip VARCHAR(20),
    street VARCHAR(255),
    academic_difficulty BOOL DEFAULT FALSE,
    dean_id INT,
    consent_scope VARCHAR(255),
    `active` BOOL DEFAULT TRUE,
    CONSTRAINT uq_students_ssn UNIQUE (ssn),
    CONSTRAINT uq_students_email UNIQUE (email),
    CONSTRAINT fk_students_dean
        FOREIGN KEY (dean_id) REFERENCES Deans(dean_id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Counselors
-- ============================================
CREATE TABLE Counselors (
    counselor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    ssn VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    salary INT DEFAULT 0,
    highest_degree VARCHAR(255) NOT NULL,
    highest_degree_school VARCHAR(255) NOT NULL,
    yrs_experience INT NOT NULL,
    yrs_here INT NOT NULL,
    specialization VARCHAR(255) NOT NULL,
    `active` BOOL DEFAULT TRUE,
    CONSTRAINT uq_counselors_ssn UNIQUE (ssn),
    CONSTRAINT uq_counselors_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Counselor_Assignments
-- ============================================
CREATE TABLE Counselor_Assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    counselor_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_primary BOOL DEFAULT TRUE,
    CONSTRAINT uq_counselor_assign UNIQUE (student_id, counselor_id, start_date),
    CONSTRAINT fk_counselor_assign_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_counselor_assign_counselor
        FOREIGN KEY (counselor_id) REFERENCES Counselors(counselor_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Healthcare_Providers
-- ============================================
CREATE TABLE Healthcare_Providers (
    provider_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    specialization VARCHAR(255),
    `active` BOOL DEFAULT TRUE,
    CONSTRAINT uq_healthcare_providers_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Symptoms
-- ============================================
CREATE TABLE Symptoms (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    symptom VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Diagnoses
-- ============================================
CREATE TABLE Diagnoses (
    diagnosis_id INT PRIMARY KEY AUTO_INCREMENT,
    diagnosis VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Categories
-- ============================================
CREATE TABLE Categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Issues
-- ============================================
CREATE TABLE Issues (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    diagnosis_id INT NOT NULL,
    `date` DATE NOT NULL,
    student_id INT NOT NULL,
    provider_id INT,
    counselor_id INT,
    visit_id INT,
    comments TEXT,
    CONSTRAINT fk_issues_diagnosis
        FOREIGN KEY (diagnosis_id) REFERENCES Diagnoses(diagnosis_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_issues_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_issues_provider
        FOREIGN KEY (provider_id) REFERENCES Healthcare_Providers(provider_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_issues_visits
        FOREIGN KEY (visit_id) REFERENCES Visits(visit_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Reported_Symptoms
-- ============================================
CREATE TABLE Reported_Symptoms (
    reported_symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    `date` DATE NOT NULL,
    symptom_id INT NOT NULL,
    CONSTRAINT uq_reported_symptoms UNIQUE (student_id, `date`, symptom_id),
    CONSTRAINT fk_reported_symptoms_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_reported_symptoms_symptom
        FOREIGN KEY (symptom_id) REFERENCES Symptoms(symptom_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Diagnosis_Categorization
-- ============================================
CREATE TABLE Diagnosis_Categorization (
    diagnosis_categorization_id INT PRIMARY KEY AUTO_INCREMENT,
    diagnosis_id INT NOT NULL,
    category_id INT NOT NULL,
    CONSTRAINT uq_diag_cat UNIQUE (diagnosis_id, category_id),
    CONSTRAINT fk_diag_cat_diagnosis
        FOREIGN KEY (diagnosis_id) REFERENCES Diagnoses(diagnosis_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_diag_cat_category
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Symptom_Categorization
-- ============================================
CREATE TABLE Symptom_Categorization (
    symptom_categorization_id INT PRIMARY KEY AUTO_INCREMENT,
    symptom_id INT NOT NULL,
    category_id INT NOT NULL,
    CONSTRAINT uq_sym_cat UNIQUE (symptom_id, category_id),
    CONSTRAINT fk_sym_cat_symptom
        FOREIGN KEY (symptom_id) REFERENCES Symptoms(symptom_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_sym_cat_category
        FOREIGN KEY (category_id) REFERENCES Categories(category_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Visits
-- ============================================
CREATE TABLE Visits (
    visit_id INT PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL,
    student_id INT NOT NULL,
    in_person BOOL DEFAULT TRUE,
    CONSTRAINT fk_visits_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Visit_Counselors
-- ============================================
CREATE TABLE Visit_Counselors (
    visit_counselor_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    counselor_id INT NOT NULL,
    CONSTRAINT uq_visit_counselors UNIQUE (visit_id, counselor_id),
    CONSTRAINT fk_visit_counselors_visit
        FOREIGN KEY (visit_id) REFERENCES Visits(visit_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_visit_counselors_counselor
        FOREIGN KEY (counselor_id) REFERENCES Counselors(counselor_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Visit_Comments
-- ============================================
CREATE TABLE Visit_Comments (
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    counselor_id INT NOT NULL,
    `comment` TEXT NOT NULL,
    CONSTRAINT fk_visit_comments_visit_counselor
        FOREIGN KEY (visit_id, counselor_id)
        REFERENCES Visit_Counselors(visit_id, counselor_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Critical_Situations
-- ============================================
CREATE TABLE Critical_Situations (
    situation_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    CONSTRAINT uq_critical_student UNIQUE (student_id, start_date),
    CONSTRAINT fk_critical_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Follow_Ups
-- ============================================
CREATE TABLE Follow_Ups (
    follow_up_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    counselor_id INT NOT NULL,
    `date` DATE NOT NULL,
    completed BOOL DEFAULT FALSE,
    CONSTRAINT uq_followups UNIQUE (student_id, counselor_id, `date`),
    CONSTRAINT fk_followups_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_followups_counselor
        FOREIGN KEY (counselor_id) REFERENCES Counselors(counselor_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Tutors
-- ============================================
CREATE TABLE Tutors (
    tutor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    age INT,
    `active` BOOL DEFAULT TRUE,
    CONSTRAINT uq_tutors_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Employment_Events
-- ============================================
CREATE TABLE Employment_Events (
    event_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    `date` DATE NOT NULL,
    `type` VARCHAR(100),
    location VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Healthcare_Referrals
-- ============================================
CREATE TABLE Healthcare_Referrals (
    referral_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    `date` DATE NOT NULL,
    provider_id INT NOT NULL,
    resolution_details TEXT,
    CONSTRAINT fk_health_ref_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_health_ref_provider
        FOREIGN KEY (provider_id) REFERENCES Healthcare_Providers(provider_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Dean_Referrals
-- ============================================
CREATE TABLE Dean_Referrals (
    referral_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    `date` DATE NOT NULL,
    dean_id INT NOT NULL,
    resolution_details TEXT,
    CONSTRAINT fk_dean_ref_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_dean_ref_dean
        FOREIGN KEY (dean_id) REFERENCES Deans(dean_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Tutor_Referrals
-- ============================================
CREATE TABLE Tutor_Referrals (
    referral_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    `date` DATE NOT NULL,
    tutor_id INT NOT NULL,
    resolution_details TEXT,
    CONSTRAINT fk_tutor_ref_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_tutor_ref_tutor
        FOREIGN KEY (tutor_id) REFERENCES Tutors(tutor_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Job_Referrals
-- ============================================
CREATE TABLE Job_Referrals (
    referral_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    `date` DATE NOT NULL,
    event_id INT NOT NULL,
    resolution_details TEXT,
    CONSTRAINT fk_job_ref_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_job_ref_event
        FOREIGN KEY (event_id) REFERENCES Employment_Events(event_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Struggle_Courses
-- ============================================
CREATE TABLE Struggle_Courses (
    struggle_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_number VARCHAR(50) NOT NULL,
    CONSTRAINT uq_struggle_courses UNIQUE (student_id, course_number),
    CONSTRAINT fk_struggle_courses_student
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;


-- ============================
-- SAMPLE DATA
-- ============================

-- =====================================================
-- DEANS
-- =====================================================
INSERT INTO Deans (name, email, school, title) VALUES
('Dr. Alice Morgan', 'amorgan@univ.edu', 'Engineering', 'Dean of Engineering'),
('Dr. Robert Fields', 'rfields@univ.edu', 'Arts & Sciences', 'Associate Dean'),
('Dr. Linda Xu', 'lxu@univ.edu', 'Business', 'Dean of Business');

-- =====================================================
-- STUDENTS
-- =====================================================
INSERT INTO Students (name, ssn, email, date_of_birth, country_of_birth, gender, grad_year,
                      insurance_provider, race, zip, street, academic_difficulty, dean_id, consent_scope)
VALUES
('John Carter','111-22-3333','jcarter@univ.edu','2003-04-12','USA','Male',2025,'Aetna','White','02139','123 Main St',TRUE,1,'full'),
('Maria Gomez','222-33-4444','mgomez@univ.edu','2002-11-02','Mexico','Female',2025,'BlueCross','Hispanic','98101','45 Pine Rd',TRUE,2,'limited'),
('Chen Wei','333-44-5555','cwei@univ.edu','2001-07-19','China','Male',2024,NULL,'Asian','10001','78 East St',FALSE,NULL,NULL),
('Sarah Thompson','444-55-6666','sthompson@univ.edu','2004-02-28','USA','Female',2026,'Aetna','Black','60601','22 Lake Shore Dr',TRUE,1,'full'),
('David Kim','555-66-7777','dkim@univ.edu','2003-09-05','South Korea','Male',2025,NULL,'Asian','30301','900 Peachtree Ave',FALSE,3,'limited'),
('Emma Rossi','666-77-8888','erossi@univ.edu','2002-03-14','Italy','Female',2025,'Cigna','White','75201','16 Elm St',FALSE,NULL,NULL);

-- =====================================================
-- COUNSELORS
-- =====================================================
INSERT INTO Counselors VALUES
(NULL,'James Miller','999-11-1111','jmiller@univ.edu',70000,'MS Counseling','NYU',8,3,'Anxiety',TRUE),
(NULL,'Lisa Park','999-22-2222','lpark@univ.edu',85000,'PhD Psychology','Harvard',12,5,'Depression',TRUE),
(NULL,'Eric Johnson','999-33-3333','ejohnson@univ.edu',0,'MA Therapy','UCLA',6,2,'Academic Stress',TRUE),
(NULL,'Patricia Lee','999-44-4444','plee@univ.edu',0,'PhD Clinical Psych','UMich',15,7,'Crisis Intervention',TRUE);

-- =====================================================
-- COUNSELOR ASSIGNMENTS
-- =====================================================
INSERT INTO Counselor_Assignments (student_id, counselor_id, start_date, end_date, is_primary) VALUES
(1,1,'2025-09-01',NULL,TRUE),
(2,2,'2025-09-05',NULL,TRUE),
(3,3,'2025-10-01',NULL,TRUE),
(4,4,'2025-10-10',NULL,TRUE),
(5,3,'2025-09-20',NULL,TRUE),
(6,2,'2025-10-05',NULL,TRUE);

-- =====================================================
-- PROVIDERS
-- =====================================================
INSERT INTO Healthcare_Providers VALUES
(NULL,'Dr. Helen Carter','hcarter@med.org','1 Wellness Way','General Medicine',TRUE),
(NULL,'Dr. Omar Siddiq','osiddiq@care.org','17 Health Plaza','Psychiatry',TRUE),
(NULL,'Dr. Nina Patel','npatel@clinic.org','55 Clinic Rd','Neurology',TRUE);

-- =====================================================
-- CATEGORIES (expanded)
-- =====================================================
INSERT INTO Categories (category) VALUES
('Mental Health'),
('Physical Health'),
('Academic'),
('Crisis'),
('Sleep Related'),
('Stress Related'),
('Cognitive'),
('Psychosomatic');

-- =====================================================
-- SYMPTOMS (expanded + overlapping)
-- =====================================================
INSERT INTO Symptoms (symptom) VALUES
('Anxiety'),
('Insomnia'),
('Headache'),
('Fatigue'),
('Difficulty Concentrating'),
('Panic Attacks'),
('Nausea'),
('Shortness of Breath'),
('Memory Issues'),
('Chest Tightness'),
('Brain Fog'),
('Irritability');

-- =====================================================
-- SYMPTOM CATEGORIZATION (MULTI-CATEGORY, HEAVY OVERLAP)
-- =====================================================
INSERT INTO Symptom_Categorization (symptom_id, category_id) VALUES
-- Anxiety
(1,1),(1,4),(1,6),(1,8),
-- Insomnia
(2,5),(2,1),(2,6),(2,8),
-- Headache
(3,2),(3,6),(3,8),
-- Fatigue
(4,2),(4,5),(4,6),(4,3),
-- Difficulty Concentrating
(5,3),(5,7),(5,6),
-- Panic Attacks
(6,1),(6,4),(6,8),
-- Nausea
(7,2),(7,8),(7,6),
-- Shortness of Breath
(8,2),(8,4),(8,8),
-- Memory Issues
(9,7),(9,3),(9,6),
-- Chest Tightness
(10,2),(10,4),(10,8),
-- Brain Fog
(11,7),(11,6),(11,3),
-- Irritability
(12,1),(12,6),(12,8);

-- =====================================================
-- DIAGNOSES
-- =====================================================
INSERT INTO Diagnoses (diagnosis) VALUES
('Generalized Anxiety Disorder'),
('Major Depressive Disorder'),
('Migraine'),
('Academic Burnout'),
('Panic Disorder'),
('Adjustment Disorder'),
('Stress-Induced Somatic Symptoms');

-- =====================================================
-- DIAGNOSIS CATEGORIZATION (OVERLAP-RICH)
-- =====================================================
INSERT INTO Diagnosis_Categorization (diagnosis_id, category_id) VALUES
(1,1),(1,6),
(2,1),
(3,2),(3,8),
(4,3),(4,6),
(5,1),(5,4),
(6,1),(6,3),(6,6),
(7,2),(7,6),(7,8);

-- =====================================================
-- ISSUES (DATES NEAR DEC 2025)
-- =====================================================
INSERT INTO Issues (diagnosis_id, date, student_id, provider_id, counselor_id, comments) VALUES
(1,'2025-12-01',1,2,1,'Heightened anxiety during finals'),
(3,'2025-11-22',2,1,NULL,'Recurring migraines'),
(4,'2025-12-05',3,NULL,3,'Late-semester academic burnout'),
(2,'2025-11-30',4,2,4,'Depressive episode worsening'),
(5,'2025-12-03',1,NULL,4,'Panic attacks in lecture hall'),
(6,'2025-11-15',2,NULL,2,'Adjustment difficulties after program change'),
(3,'2025-10-28',5,3,NULL,'Severe headaches'),
(7,'2025-12-06',6,NULL,2,'Stress-related physical symptoms'),
(4,'2025-11-27',1,NULL,3,'Burnout from workload'),
(2,'2025-10-30',2,2,2,'Moderate depression symptoms');

-- =====================================================
-- REPORTED SYMPTOMS
-- =====================================================
INSERT INTO Reported_Symptoms VALUES
(NULL,1,'2025-12-01',1),
(NULL,1,'2025-12-01',2),
(NULL,2,'2025-11-22',3),
(NULL,2,'2025-11-22',7),
(NULL,3,'2025-12-05',5),
(NULL,4,'2025-11-30',12),
(NULL,4,'2025-11-30',9),
(NULL,5,'2025-10-28',3),
(NULL,6,'2025-12-06',10),
(NULL,6,'2025-12-06',11);

-- =====================================================
-- VISITS
-- =====================================================
INSERT INTO Visits (date, student_id, in_person) VALUES
('2025-12-01',1,TRUE),
('2025-11-23',2,FALSE),
('2025-12-06',3,TRUE),
('2025-11-30',4,TRUE),
('2025-10-29',5,FALSE);

-- =====================================================
-- VISIT COUNSELORS
-- =====================================================
INSERT INTO Visit_Counselors (visit_id, counselor_id) VALUES
(1,1),(2,2),(3,3),(4,4),(5,1);

-- =====================================================
-- VISIT COMMENTS
-- =====================================================
INSERT INTO Visit_Comments VALUES
(NULL,1,1,'Finals stress coping strategies'),
(NULL,2,2,'Migraine tracking advised'),
(NULL,3,3,'Academic recovery plan created'),
(NULL,4,4,'Crisis intervention session'),
(NULL,5,1,'Telehealth stress check-in');

-- =====================================================
-- CRITICAL SITUATIONS
-- =====================================================
INSERT INTO Critical_Situations (student_id, start_date, end_date) VALUES
(4,'2025-11-30',NULL),
(1,'2025-12-02','2025-12-05');

-- =====================================================
-- FOLLOW UPS
-- =====================================================
INSERT INTO Follow_Ups VALUES
(NULL,1,1,'2025-12-08',TRUE),
(NULL,2,2,'2025-12-02',FALSE),
(NULL,3,3,'2025-12-10',FALSE),
(NULL,4,4,'2025-12-12',FALSE),
(NULL,6,2,'2025-11-29',TRUE);

-- =====================================================
-- TUTORS
-- =====================================================
INSERT INTO Tutors VALUES
(NULL,'Mark Benson','mbenson@univ.edu','Math',31,TRUE),
(NULL,'Alice Romano','aromano@univ.edu','Chemistry',44,TRUE),
(NULL,'Jacob Lin','jlin@univ.edu','Computer Science',29,TRUE);

-- =====================================================
-- EMPLOYMENT EVENTS
-- =====================================================
INSERT INTO Employment_Events VALUES
(NULL,'Tech Internship Fair','2025-11-18','Career Fair','Campus Hall'),
(NULL,'Business Networking Night','2025-11-25','Networking','Biz Center'),
(NULL,'STEM Research Expo','2025-12-03','Expo','Lab Building');

-- =====================================================
-- REFERRALS
-- =====================================================
INSERT INTO Tutor_Referrals VALUES
(NULL,1,'2025-12-04',1,'Weekly tutoring'),
(NULL,4,'2025-12-06',2,NULL);

INSERT INTO Healthcare_Referrals VALUES
(NULL,1,'2025-12-02',2,'Psych eval scheduled'),
(NULL,5,'2025-10-30',3,'Neurology consult complete');

INSERT INTO Dean_Referrals VALUES
(NULL,4,'2025-12-05',1,'Academic probation review');

INSERT INTO Job_Referrals VALUES
(NULL,2,'2025-11-26',2,'Event attended'),
(NULL,6,'2025-11-18',1,'Recruiter follow-up');

-- =====================================================
-- STRUGGLE COURSES
-- =====================================================
INSERT INTO Struggle_Courses VALUES
(NULL,1,'COSC-3510'),
(NULL,2,'COSC-1050'),
(NULL,2,'COSC-3510'),
(NULL,4,'COSC-1050'),
(NULL,4,'COSC-2000'),
(NULL,4,'COSC-3510'),
(NULL,4,'COSC-4000');



-- ============================================
-- CHECKING STUFF GOES HERE
-- ============================================
-- Check all tables exist
SHOW TABLES;

