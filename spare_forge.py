import os
import socket

# FORCE IPv4 FIRST (keep if you want)
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = _ipv4


# IMPORT FLASK FIRST
from flask import Flask, render_template_string, request, redirect, session
from werkzeug.utils import secure_filename
import uuid
import cloudinary
import cloudinary.uploader
import psycopg2

def get_conn():
    return psycopg2.connect(
        os.environ.get("DATABASE_URL"),
        sslmode="require"
    )

# 🔥 CREATE APP HERE (THIS IS REQUIRED BEFORE ANY app.*)
app = Flask(__name__)

# THEN CONFIG
app.secret_key = "forge_ultra_secure"

cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)

UPLOAD_FOLDER = "static/uploads"
BRAND_FOLDER = "static/brands"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BRAND_FOLDER, exist_ok=True)


# ---------------- INIT ----------------
def init():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS products(
        name TEXT,
        price INTEGER,
        old_price REAL,
        image TEXT,
        code TEXT,
        part_name TEXT,
        part_number TEXT,
        part_description TEXT,
        part_category TEXT,
        part_condition TEXT,
        brand TEXT,
        id SERIAL PRIMARY KEY
    )""")

    conn.commit()
    conn.close()

init()

def code():
    return "SFS-" + str(uuid.uuid4())[:5].upper()

# ---------------- HOME ----------------
@app.route("/")
def home():
    q = request.args.get("q", "")
    brand = request.args.get("brand", "")

    conn = get_conn()
    c = conn.cursor()

    if q:
        c.execute("""SELECT * FROM products 
        WHERE name ILIKE %s OR part_number ILIKE %s""",
        ('%' + q + '%', '%' + q + '%'))

    elif brand:
        c.execute("SELECT * FROM products WHERE brand=%s", (brand,))
    else:
        c.execute("SELECT * FROM products")

    products = c.fetchall()
    conn.close()

    brands = ["Nissan","Volkswagen","BMW","Mercedes","Mazda","Toyota","Subaru"]

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<style>
*{
    box-sizing: border-box;
}

.container{
    width:100%;
    max-width:1200px;
    margin:auto;
    overflow-x:hidden;
}

body{
    margin:0;
    font-family:Arial;
    background:#0a3d62;
    color:#fff;
    overflow-x:hidden;
    width:100%;
}

html, body{
    max-width:100%;
    overflow-x:hidden;
}

header{
    background:#074173;
    padding:15px;
    display:flex;
    justify-content:center;
    align-items:center;
    flex-wrap:wrap; /* ✅ allows stacking on small screens */
    gap:10px;
}

@media (max-width: 600px){
    .logo img{
        height:140px;
    }
}

.logo{
    display:flex;
    align-items:center;
    gap:10px;
}

.logo img {
    height: 220px;
    width: auto;
    max-width: 100%
}

.search{
    padding:10px;
    width:100%;
    max-width:180px;
    border-radius:20px;
    border:none;
}

form{
    width:100%;
}

.category{
    display:flex;
    gap:15px;
    overflow-x:auto;
    padding:15px;
    background:#082f4f;
}

.cat{
    text-align:center;
}

.cat img{
    width:60px;
    height:60px;
    border-radius:10px;
}

.grid{
    display:grid;
    grid-template-columns:repeat(2, 1fr);
    gap:10px;
    padding:10px;
}

/* tablet */
@media (min-width: 700px){
    .grid{
        grid-template-columns:repeat(3, 1fr);
    }
}

/* desktop */
@media (min-width: 1000px){
    .grid{
        grid-template-columns:repeat(4, 1fr);
    }
}

.card{
    background:transparent;
    color:white;
    border-radius:0;
    padding:5px;
    text-align:center;
    display:flex;
    flex-direction:column;
    gap:6px;
}

.card img{
    width:100%;
    height:160px;
    object-fit:cover;
    border-radius:10px;
    background:transparent;
}

.price{font-weight:bold;color:green;}

.old{
    text-decoration: line-through;
    color: gray;
    font-size:14px;
}

.card h4, .card p {
    margin:3px 0;
}

footer{
    background:#074173;
    padding:20px;
    text-align:center;
}
</style>
</head>

<body>

<header>
<div class="logo">
<img src="/static/logo.png">
</div>

<form>
<input class="search" name="q" placeholder="Search">
</form>
</header>

<div class="category">
{% for b in brands %}
<div class="cat">
<a href="/?brand={{b}}">
<img src="/static/brands/{{b}}.jpg">
<br><span style="color:white;font-weight:bold;">{{b}}</span>
</a>
</div>
{% endfor %}
</div>

<div class="grid">
{% for p in products %}
<div class="card">

{% if p[3] %}
<div style="display:flex; overflow-x:auto; gap:5px;">
{% for img in p[3].split(',') %}
<img src="{{img}}" style="width:100%; border-radius:8px;">
{% endfor %}
</div>
{% endif %}

<h4>{{p[0]}}</h4>
<p>{{ p[6] if p|length > 6 and p[6] else "N/A" }}</p>

<div class="price">
Ksh {{p[1]}}<br>

{% if p[2] %}
<span class="old">Ksh {{ p[2] }}</span>
{% endif %}

</div>

</div>
{% endfor %}
</div>

<footer>
<p><b>Your garage online</b></p>

<p>
<a href="https://wa.me/message/TVW7OUFM7VNTL1" style="color:white;">
📱 WhatsApp
</a>
</p>

<p>Email: flexmuiru@email.com</p>
<p>facebook: spare forge</p>
<p>Phone: 0112752649</p>
</footer>

</body>
</html>
""", products=products, brands=brands)

# ---------------- ADMIN ----------------
ADMIN_USER = "admin"
ADMIN_PASS = "forge2026"

@app.route("/hidden-admin-portal", methods=["GET","POST"])
def admin():
    error = ""

    try:
        if request.method == "POST":
            u = request.form.get("u")
            p = request.form.get("p")

            if u == ADMIN_USER and p == ADMIN_PASS:
                session["admin"] = True
                return redirect("/dashboard")
            else:
                error = "Wrong login"

    except Exception as e:
        return f"Error: {str(e)}"

    return render_template_string("""
    <h2>Admin Login</h2>

    <form method="post">
        <input name="u" placeholder="username"><br><br>
        <input name="p" type="password"><br><br>
        <button>Login</button>
    </form>

    <p style="color:red;">{{error}}</p>
    """, error=error)

# ---------------- DELETE ----------------
@app.route("/delete/<int:pid>")
def delete(pid):
    if not session.get("admin"):
        return redirect("/hidden-admin-portal")

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("admin"):
        return redirect("/hidden-admin-portal")

    conn = get_conn()
    c = conn.cursor()

if request.method == "POST":
    name = request.form.get("n") or ""
    part_number = request.form.get("pnum") or ""
    brand = request.form.get("brand") or ""

    # SAFE PRICE CONVERSION
    try:
        price = int(request.form.get("p"))
    except:
        price = 0

    try:
        old_price = float(request.form.get("old_price"))
    except:
        old_price = 0.0

    image_urls = []

    files = request.files.getlist("i")

    for file in files:
        if file and file.filename != "":
            try:
                upload = cloudinary.uploader.upload(file, resource_type="image")
                url = upload.get("secure_url") if upload else None
                if url:
                    image_urls.append(url)
            except Exception as e:
                print("Cloudinary upload error:", e)

    image_url = ",".join(image_urls) if image_urls else ""

    c.execute("""INSERT INTO products 
    (name, price, old_price, image, code, part_name, part_number, part_description, part_category, part_condition, brand)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
    (
        name,
        price,
        old_price,
        image_url,
        code(),
        name,
        part_number,
        "",
        "",
        "",
        brand
    ))

    conn.commit()

    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>

    <h2>Dashboard</h2>

    <form method="post" enctype="multipart/form-data">
    <input name="n" placeholder="Name">
    <input name="p" placeholder="Price">
    <input name="old_price" placeholder="Old Price">
    <input name="pnum" placeholder="Part Number">

    <select name="brand">
    <option>Nissan</option>
    <option>Volkswagen</option>
    <option>BMW</option>
    <option>Mercedes</option>
    <option>Mazda</option>
    <option>Toyota</option>
    <option>Subaru</option>
    </select>

    <input type="file" name="i" multiple>
    <button>Add Product</button>
    </form>

    <hr>

    {% for p in products %}
    <p>
    <b>{{p[0]}}</b> - Ksh {{p[1]}}
    <a href="/delete/{{p[11]}}">Delete</a>
    </p>
    {% endfor %}

    </body>
    </html>
    """, products=products)

