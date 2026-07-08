# Steganography Web Application

## Overview

This project is a Flask-based web application that allows authenticated users to embed and extract hidden messages within uploaded files using a bit-replacement steganography algorithm. Embedded files can then be posted to a public gallery where all visitors can browse and download them.

The application was developed as a university project to demonstrate web development, user authentication, database integration, file handling, and steganography concepts.

Please note that this is intended for testing, do not use or post sensitive information.

---

## Features

* User registration and login with hashed passwords
* Session-based authentication
* Upload files for steganographic embedding
* Extract hidden messages from uploaded files
* Public gallery of uploaded files
* Image preview for supported image formats
* Audio/video playback for supported media types
* Download support for all uploaded files
* Previous/Next navigation through uploaded posts
* SQLite database for user and post management

---

## Technologies Used

* Python
* Flask
* SQLite
* HTML5
* CSS3
* Jinja2 Templates
* Gunicorn (deployment)
* Microsoft Azure App Service

---

## Project Structure

```text
.
├── app.py
├── steg.py
├── wsgi.py
├── requirements.txt
├── app.db
├── static/
│   ├── css/
│   └── uploads/
└── templates/
```

---

## Running Locally

1. Clone the repository.

2. Create and activate a virtual environment.

3. Install the required packages.

```bash
pip install -r requirements.txt
```

4. Set a local Flask secret key.

Windows PowerShell:

```powershell
$env:SECRET_KEY="your-local-secret-key"
```

5. Run the application.

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Deployment

The application is configured for deployment to Microsoft Azure App Service using Gunicorn.

Example startup command:

```text
gunicorn wsgi:app
```

---

## Steganography Algorithm

The application implements a configurable bit-replacement steganography algorithm based on user-selected parameters:

* **S** – Starting bit offset before embedding begins
* **L** – Periodicity of modified bits
* **C** – Embedding mode

The algorithm supports embedding arbitrary files within other files and provides corresponding extraction functionality.

---

## Known Limitations

Because the embedding algorithm modifies bits directly throughout the carrier file, some compressed image formats (such as PNG and JPEG) may exhibit visible distortion or become unreadable depending on the chosen parameters and payload size. Larger carrier files and more conservative embedding parameters generally produce better results.

---

## Future Improvements

* Like/comment system
* Search and filtering
* User profile pages
* Cloud-based database
* Improved steganography algorithms with reduced visual distortion
* Drag-and-drop uploads
* Pagination for the public gallery

---

## Author

Isen Maggard

University of Texas at Arlington

Computer Science
