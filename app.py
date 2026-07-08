from flask import Flask, render_template, redirect, request, flash, send_file, session
from steg import embed, extract
import json
import hashlib
import struct
import os
from werkzeug.utils import secure_filename
import sqlite3
import uuid
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-only-key"
)
#venvironment activate command (windows cmd)
#venv\Scripts\activate.bat

USER_FILE = "users.json"
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)



def init_db():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, user_id INTEGER)")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall()) 
    
    conn.commit()
    conn.close()


def get_db():
    return sqlite3.connect("app.db")




@app.route("/")
def home():
    return render_template ("login.html")

@app.route("/landing")
def landing_load():
    print("Logged in as user:", session.get("username"))

    
    
    username = session.get("username")
    logged_in = "user_id" in session

    index = int(request.args.get("index",0))
    
    conn = get_db()
    cursor = conn.cursor()

    # cursor.execute("SELECT filename FROM posts")
    cursor.execute("SELECT posts.filename, users.username FROM posts JOIN users ON posts.user_id = users.id" )
    rows=cursor.fetchall()
    conn.close()

    posts=[]

    for row in rows:
        filename = row[0]
        username_posted = row[1]
        ext = filename.split(".")[-1].lower() #get file extension

        posts.append({
            "filename": filename,
            "ext": ext,
            "username":username_posted
        })

    

    message = "View Posts"
    message2 = "Please note, this is a test site and all posts are public. Do not use or post sensitive information."
    
   
    if not posts:
        message = "No posts yet"
        return render_template("landing.html", message = message, message2 = message2, logged_in=logged_in, username = username)
    
    index = index % len(posts)

    current_post = posts[index]

    print(index)
    print("image from db:" ,current_post)

    return render_template("landing.html", posts=posts, logged_in=logged_in, username = username, post = current_post, index = index, total = len(posts), message = message, message2 = message2)



@app.route("/guest_login")
def guest_login():

    index = int(request.args.get("index",0))
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT posts.filename, users.username FROM posts JOIN users ON posts.user_id = users.id")
    rows=cursor.fetchall()
    conn.close()

    posts=[]

    for row in rows:
        filename = row[0]
        username_posted = row[1]
        ext = filename.split(".")[-1].lower() #get file extension

        posts.append({
            "filename": filename,
            "ext": ext,
            "username":username_posted
        })

    message = "View Posts"
    message2 = "Please note, this is a test site and all posts are public. Do not use or post sensitive information."

    
   
    if not posts:
        message = "No posts yet"
        return render_template("landing.html", message = message, message2 = message2, logged_in=False, username = "guest")
    
    index = index % len(posts)

    current_post = posts[index]

    print(index)
    print("image from db:" ,current_post)

    return render_template("landing.html", posts=posts, logged_in=False, username = "guest", post = current_post, index = index, total = len(posts), message = message, message2 = message2)


''' START CREDENTIALS FUNCTIONS '''


'''

Deprocated, unused now that connected to real DB

'''
# def load_users():
#     try:
#         with open(USER_FILE, "r") as f:
#             return json.load(f)
#     except:
#         return{}

# def save_users(users):
#     with open(USER_FILE, "w") as f:
#         json.dump(users,f)




def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    hashed = hash_password(password)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password FROM users WHERE username = ?", (username,)

    )
    user = cursor.fetchone() # user is array with [0] = user id and [1] = password

    conn.close()

    if user and user[1] == hashed:
        session["user_id"] = user[0]
        session["username"] = username
        return redirect("/landing")
        
    else:
        flash("invalid credentials")
        return redirect("/")


#OLD LOGIN BEFORE DB

# def login():

#     username = request.form["username"]
#     password = request.form["password"]

#     users = load_users()
#     hashed = hash_password(password)

#     if username in users and users[username] == hashed:
#         return render_template("landing.html")
#     else:
#         flash("invalid credentials")
#         return redirect("/")


# @app.route("/signup", methods=["POST"])
@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    hashed = hash_password(password)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed)

        )
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Username already exists")
        conn.close()
        return redirect("/signup")
    
    except Exception as e:
        print("DB ERROR: " , e)
        conn.close()
        return "Database error", 500
    
    conn.close()

    flash("Success! Please log in.")
    #return render_template("login.html")
    return redirect("/")



#OLD register BEFORE DB

# def register():
#     username = request.form["username"]
#     password = request.form["password"]

#     users = load_users()
#     users[username] = hash_password(password)
#     save_users(users)

#     flash("Success! Please log in.")
#     return redirect("/")

''' END CREDENTIALS FUNCTIONS '''


#### START STEG FUNCTIONS ####

@app.route("/steg_func_page")
def steg_func_page():
    return render_template("steg.html")

@app.route("/embed", methods=["POST"])
def embed_route():
    carrier_file = request.files["carrier"]
    message_file = request.files["message"]

    S = int(request.form["S"])
    L = int(request.form["L"])

    carrier_bytes = carrier_file.read()
    message_bytes = message_file.read()

    try:
        output_bytes = embed(carrier_bytes, message_bytes, S, L)
    except ValueError as e:
        return str(e), 400

    output_path = os.path.join(OUTPUT_FOLDER, "stego_output")

    # keep original extension
    ext = os.path.splitext(carrier_file.filename)[1]
    output_path += ext

    with open(output_path, "wb") as f:
        f.write(output_bytes)

    return send_file(output_path, as_attachment=True)


@app.route("/extract", methods=["POST"])
def extract_route():
    carrier_file = request.files["carrier"]

    S = int(request.form["S"])
    L = int(request.form["L"])

    carrier_bytes = carrier_file.read()

    message_bytes = extract(carrier_bytes, S, L)

    output_path = os.path.join(OUTPUT_FOLDER, "extracted_message")

    with open(output_path, "wb") as f:
        f.write(message_bytes)

    return send_file(output_path, as_attachment=True)

### END STEG FUNCTIONS ####

###START SITE FUNCTIONS ###

@app.route("/post_page")
def post_page():
    return render_template("post.html")

@app.route("/post", methods=["POST"])
def post_image():
    file = request.files["image"]
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4()}_{filename}" #make filename unique to avoid collisions

    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (filename, user_id) VALUES (?,?)", (unique_name, session["user_id"]))

    conn.commit()
    conn.close()
    

    return redirect("landing")



##### ADMIN FUNC TO REFRESH IMAGES IN DATABASE 
#### ALSO RESETS AUTOINCREMENT


@app.route("/admin-image-refresh")
def admin_image_refresh():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='posts'")

    conn.commit()
    conn.close()
    return redirect("/landing")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



if __name__ == "__main__":
    init_db()
    app.run(debug = False)