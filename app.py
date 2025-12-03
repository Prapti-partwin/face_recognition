# app.py
from flask import Flask, request, render_template, redirect, url_for, flash
import cv2
import numpy as np
import face_recognition
import os
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "face_recognition_secret_key"

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'face_recognition_db',
    'port': 3300
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def get_all_face_encodings():
    """Fetch all face encodings from the database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.id, p.name, p.age, p.email, p.phone, f.encoding, f.image_path 
            FROM persons p
            JOIN face_encodings f ON p.id = f.person_id
        """)
        results = cursor.fetchall()
        
        # Convert string encodings back to numpy arrays
        for result in results:
            if result['encoding']:
                result['encoding'] = np.frombuffer(result['encoding'], dtype=np.float64)
        
        return results
    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    person = {
        'name': ' ',
        'age': ' '

    }
    return render_template('index.html', person=person)


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
        file.save(filepath)
        
        # Process the uploaded image
        try:
            # Load the uploaded image
            image = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                flash('No faces detected in the uploaded image')
                return redirect(url_for('index'))
            
            # Use the first face found
            face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
            
            # Get all face encodings from database
            db_faces = get_all_face_encodings()
            
            if not db_faces:
                flash('No faces found in the database')
                return redirect(url_for('index'))
            
            #- Compare with database faces
            # matched_person = None
            # for person in db_faces:
                #- Compare faces with a tolerance of 0.6 (lower means more strict)
                # if person['encoding'] is not None:
                    # matches = face_recognition.compare_faces([person['encoding']], face_encoding, tolerance=0.6)
                    # if matches[0]:
                        # matched_person = person
                        # break
            matched_person = None
            known_encodings = [person['encoding'] for person in db_faces if person['encoding'] is not None]

            if not known_encodings:
                flash('No valid face encodings in database')
                return redirect(url_for('index'))

            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            # Use a strict threshold (e.g., 0.5)
            if face_distances[best_match_index] < 0.5:
                matched_person = db_faces[best_match_index]

            if matched_person:
                # Display the matched person's details
                return render_template('result.html', 
                                      person=matched_person, 
                                      uploaded_image=filepath,
                                      db_image=matched_person['image_path'])
            else:
                flash('No matching face found in the database')
                return redirect(url_for('index'))


            if matched_person:
                # Display the matched person's details
                return render_template('result.html', 
                                      person=matched_person, 
                                      uploaded_image=filepath,
                                      db_image=matched_person['image_path'])
            else:
                flash('No matching face found in the database')
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Only JPG, JPEG, and PNG are allowed.')
    return redirect(url_for('index'))

# Route to add a new person to the database
@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        name = request.form.get('name')
        age = request.form.get('age')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        if file.filename == '' or not name:
            flash('Missing required information')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process face encoding
                image = face_recognition.load_image_file(filepath)
                face_locations = face_recognition.face_locations(image)
                
                if not face_locations:
                    flash('No faces detected in the uploaded image')
                    return redirect(request.url)
                
                face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
                
                # Save to database
                conn = get_db_connection()
                if not conn:
                    flash('Database connection error')
                    return redirect(request.url)
                
                cursor = conn.cursor()
                try:
                    # Insert person
                    cursor.execute(
                        "INSERT INTO persons (name, age, email, phone) VALUES (%s, %s, %s, %s)",
                        (name, age, email, phone)
                    )
                    person_id = cursor.lastrowid
                    
                    # Insert face encoding
                    cursor.execute(
                        "INSERT INTO face_encodings (person_id, encoding, image_path) VALUES (%s, %s, %s)",
                        (person_id, face_encoding.tobytes(), filepath)
                    )
                    
                    conn.commit()
                    flash('Person added successfully')
                    return redirect(url_for('index'))
                    
                except mysql.connector.Error as err:
                    conn.rollback()
                    flash(f'Database error: {err}')
                    return redirect(request.url)
                finally:
                    cursor.close()
                    conn.close()
                    
            except Exception as e:
                flash(f'Error processing image: {str(e)}')
                return redirect(request.url)
    
    return render_template('add_person.html')

if __name__ == '__main__':
    app.run(debug=True)