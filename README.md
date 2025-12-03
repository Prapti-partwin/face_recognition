# face_recognition
VaidyaSutra is a web-based emergency patient identification platform designed to quickly identify unknown or unconscious patients using facial recognition and retrieve their medical records from a secure database.
This system helps hospitals and emergency responders access critical health information (allergies, medical history, blood group, emergency contacts, etc.) within seconds.

---

## 🚀 **Features**

### 🔍 **1. Face Recognition for Patient Identification**

* Uses **dlib** and **face_recognition** library
* Extracts facial embeddings and matches them with stored data
* Works with webcam inputs or uploaded images

### 🧠 **2. Secure Patient Data Storage**

* Patient details stored in **MySQL (Oracle)**
* Uses `mysql-connector-python` for communication
* Stores:

  * Name
  * Age
  * Medical history
  * Blood group
  * Emergency contacts
  * Facial encodings

### 🌐 **3. Web Application (Flask)**

* Built using **Flask (Advanced Python)**
* User-friendly interface for:

  * Registering new patients
  * Capturing facial data
  * Searching/identifying patients
  * Viewing medical profiles

### 🎥 **4. Camera & Image Support**

* Uses **OpenCV** for:

  * Real-time webcam capture
  * Preprocessing
  * Face detection

---

## 🛠 **Tech Stack**

### **Backend**

* Python (Anaconda Environment)
* Flask (Advanced Python)
* OpenCV
* face_recognition (dlib)
* MySQL Connector

### **Database**

* MySQL (Oracle)

### **Tools**

* dlib
* numpy
* opencv-python
* mysql-connector-python

---

## 📁 **Project Structure (Example)**

```
VaidyaSutra/
│
├── app.py                 # Main Flask app
├── database.py            # MySQL connection & queries
├── face_utils.py          # Face encoding & matching
├── static/ uploads               # CSS, JS, images
├── templates/'all html files'    # HTML templates
└── dataset/               # Stored facial images & encodings
```

---

## ⚙️ **Installation & Setup**

### **1. Create Conda Environment**

```bash
conda create -n vaidya python=3.10
conda activate vaidya
```

### **2. Install Dependencies**

```bash
pip install flask opencv-python mysql-connector-python face_recognition dlib numpy
```

### **3. Setup MySQL Database**

* Create a database:

  ```sql
  CREATE DATABASE vaidya_db;
  ```
* Create `patients` table (example):

  ```sql
  CREATE TABLE patients (
      id INT PRIMARY KEY AUTO_INCREMENT,
      name VARCHAR(100),
      age INT,
      blood_group VARCHAR(10),
      contact VARCHAR(20),
      medical_history TEXT,
      face_encoding LONGBLOB
  );
  ```

### **4. Run the Application**

```bash
python app.py
```

Open the browser and visit:
👉 `http://127.0.0.1:5000/`

---

## 🧪 **How It Works**

### **🔹 Register Patient**

* Capture an image through webcam
* Generate facial encoding
* Store encoding + patient details in MySQL

### **🔹 Identify Patient**

* Capture face
* Generate encoding
* Compare with stored encodings
* Display matching patient profile instantly

---

## 📦 **Future Enhancements**

* Integration with hospital APIs
* Fingerprint & Iris-based identification
* Emergency alert system
* Cloud-based storage & scaling
* Mobile app version

---

## 👥 **Team / Contribution**

This project was developed during **MECIA Hacks 2.0** hackathon.

---
