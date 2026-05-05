import os
import socket

# FORCE IPv4 FIRST (keep if you want)
_orig_getaddrinfo = socket.getaddrinfo

def _ipv4(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = _ipv4


# IMPORT FLASK FIRST
from flask import Flask, render_template_string, request, redirect, session, send_from_directory
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
@app.route("/product/<int:id>")
def product_page(id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT name, price, old_price, image, brand, part_number
    FROM products WHERE id=%s
    """, (id,))

    product = c.fetchone()
    conn.close()

    if not product:
        return "Not found"

    return render_template_string("""
    <html>
    <head>
        <title>{{p[0]}} | Spare Forge Kenya</title>
        <meta name="description" content="{{p[0]}} spare part in Kenya for {{p[4]}}">
    </head>
    <body>
        <h1>{{p[0]}}</h1>
        <p>Ksh {{p[1]}}</p>
    </body>
    </html>
    """, p=product)

@app.route("/")
def home():
    q = request.args.get("q", "")
    q = (q or "").strip()

    brand = request.args.get("brand", "")

    print("SEARCH Q:", q)

    conn = get_conn()
    c = conn.cursor()

    if q:
        c.execute("""
        SELECT name, price, old_price, image, code,
        part_name, part_number, part_description,
        part_category, part_condition, brand, id
        FROM products
        WHERE name ILIKE %s OR part_number ILIKE %s
        """,
        ('%' + q + '%', '%' + q + '%'))

    elif brand:
        c.execute("""
        SELECT name, price, old_price, image, code,
        part_name, part_number, part_description,
        part_category, part_condition, brand, id
        FROM products
        WHERE brand=%s
        """, (brand,))

    else:
        c.execute("""
        SELECT name, price, old_price, image, code,
        part_name, part_number, part_description,
        part_category, part_condition, brand, id
        FROM products
        """)

    products = c.fetchall()
    conn.close()

    brands = ["Nissan","Volkswagen","BMW","Mercedes","Mazda","Toyota","Subaru"]

    return render_template_string(""" 
<!DOCTYPE html>
<html>
<head>
<link rel="canonical" href="https://YOUR-DOMAIN.com/" />

<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="google-site-verification" content="h-X6tHTJ_YuQoJz62E5_ts_yEqvOWTOOP3ZNziJqxn0" />

<title>Car Spare Parts Kenya | Toyota, BMW, Nissan - Spare Forge</title>

<meta name="description" content="Buy affordable car spare parts in Kenya. Toyota, BMW, Nissan, Mazda and more. Fast delivery and trusted sellers.">

<meta name="keywords" content="spare parts Kenya, car parts Nairobi, Toyota parts Kenya, BMW spare parts, Nissan parts Kenya, cheap auto parts Kenya">

<meta name="robots" content="index, follow">

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
    gap:4px;
    padding:4px;
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
    padding:3px;
    text-align:center;
    display:flex;
    flex-direction:column;
    gap:3px;
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

<h1 style="text-align:center; margin:10px 0; font-size:20px;">
Affordable Car Spare Parts in Kenya
</h1>

<p style="text-align:center; font-size:14px; color:#ddd;">
Toyota, BMW, Nissan, Mazda & Mercedes parts with fast delivery in Kenya.
</p>

<form>
<input class="search" name="q" placeholder="Search">
</form>
</header>

<div class="category">
{% for b in brands %}
<div class="cat">
<a href="/?brand={{b}}">
    {{b}} Spare Parts Kenya
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
<div style="
    display:grid;
    grid-template-columns:repeat(auto-fit, minmax(120px, 1fr));
    gap:6px;
">
    {% for img in p[3].split(',') %}
        {% if img.strip() %}
            <img
                src="{{ img.strip().replace('/upload/', '/upload/w_400,q_auto,f_auto/') }}"
                loading="lazy"
                onclick="openModal(this.src)"
                style="
                    cursor:pointer;"
                    width:100%;
                    height:140px;
                    object-fit:cover;
                    border-radius:10px;
                "
            >
        {% endif %}
    {% endfor %}
</div>
{% endif %}

<div style="display:flex; flex-direction:column; gap:2px; margin-top:4px; text-align:left;">

    <h2 style="font-weight:bold; font-size:16px;">
<a href="/product/{{p[11]}}" style="color:white; text-decoration:none;">
{{p[0]}} - {{p[10]}} Spare Parts Kenya
</a>
</h2>

    <div style="font-size:13px; color:#ccc;">
        Part No: {{ p[6] if p|length > 6 and p[6] else "N/A" }}
    </div>

    <div style="font-size:15px; font-weight:bold; color:green;">
        Ksh {{p[1]}}
    </div>

    {% if p[2] and p[2] > 0 %}
    <div style="font-size:13px; color:gray; text-decoration:line-through;">
        Ksh {{p[2]}}
    </div>
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

<div id="imgModal" style="
    display:none;
    position:fixed;
    z-index:9999;
    left:0;
    top:0;
    width:100%;
    height:100%;
    background:rgba(0,0,0,0.95);
    justify-content:center;
    align-items:center;
">

    <span onclick="closeModal()" style="
        position:absolute;
        top:20px;
        right:25px;
        font-size:35px;
        color:white;
        cursor:pointer;
    ">✖</span>

    <img id="modalImg" style="
        max-width:95%;
        max-height:90%;
        border-radius:10px;
    ">
</div>

<!-- ✅ ADD THIS SCRIPT -->
<script>
function openModal(src){
    const modal = document.getElementById("imgModal");
    const modalImg = document.getElementById("modalImg");

    modal.style.display = "flex";

    // ✅ optimized full image (less data)
    modalImg.src = src.replace('/upload/', '/upload/w_900,q_auto,f_auto/');
}

function closeModal(){
    document.getElementById("imgModal").style.display = "none";
}
</script>

</body>
</html>
""", products=products, brands=brands)

@app.route("/sitemap.xml")
def sitemap():
    return app.send_static_file("sitemap.xml")

@app.route("/robots.txt")
def robots():
    return app.send_static_file("robots.txt")

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
@app.route("/delete/<pid>")
def delete(pid):
    if not session.get("admin"):
        return redirect("/hidden-admin-portal")

    try:
        pid = int(pid)
    except:
        return "Invalid ID"

    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()

    if c.rowcount == 0:
        conn.close()
        return "Delete failed: ID not found"

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

        price_raw = request.form.get("p")

        try:
            price = int(float(str(price_raw).replace(",", "").strip()))
        except:
            price = 0

        old_raw = request.form.get("old_price")
        
        try:
            old_price = int(float(str(old_raw).replace(",", "").strip()))
        except:
            old_price = 0.0

        image_urls = []
        files = request.files.getlist("i")

        for file in files:
            if file and file.filename != "":
                print("Uploading:", file.filename)
                try:
                    upload = cloudinary.uploader.upload(file, resource_type="image")
                    url = upload.get("secure_url")
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

    # ✅ FIXED QUERY (ONLY CHANGE)
    c.execute("""
    SELECT name, price, old_price, image, code,
    part_name, part_number, part_description,
    part_category, part_condition, brand, id
    FROM products
    """)

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
