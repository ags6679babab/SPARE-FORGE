from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, redirect, session
import os
from werkzeug.utils import secure_filename
import sqlite3, uuid

app = Flask(__name__)
app.secret_key = "forge_ultra_secure"

UPLOAD_FOLDER = "static/uploads"
BRAND_FOLDER = "static/brands"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BRAND_FOLDER, exist_ok=True)

DB = "/tmp/store.db"

# ---------------- INIT ----------------
def init():
    conn = sqlite3.connect(DB)
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
        id INTEGER PRIMARY KEY AUTOINCREMENT
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

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if q:
        c.execute("""SELECT * FROM products 
        WHERE LOWER(name) LIKE ? OR LOWER(part_number) LIKE ?""",
        ('%' + q.lower() + '%', '%' + q.lower() + '%'))

    elif brand:
        c.execute("SELECT * FROM products WHERE brand=?", (brand,))
    else:
        c.execute("SELECT * FROM products")

    products = c.fetchall()
    conn.close()

    brands = ["Nissan","Volkswagen","BMW","Mercedes","Mazda","Toyota","Subaru"]

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body{
    margin:0;
    font-family:Arial;
    background:#0a3d62;
    color:#fff;
}

header{
    background:#074173;
    padding:15px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.logo{
    display:flex;
    align-items:center;
    gap:10px;
}

.logo img {
    height: 200px;  /* bigger logo */
    width: auto;    /* keeps aspect ratio */
}

.search{padding:10px;width:220px;border-radius:20px;border:none;}

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
    grid-template-columns:repeat(auto-fill,minmax(220px,1fr));
    gap:20px;
    padding:20px;
}

.card{
    background:transparent;
    color:black;
    border-radius:10px;
    padding:8px;
    text-align:center;
    display:flex;
    flex-direction:column;
    gap:6px;
}

.card img{
    width:100%;
    maximum height:120px;
    object-fit:contain;
    margin-bottom:5px;
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
<style>

.card{
    background:transparent;
    color:black;
    border-radius:10px;
    padding:8px;
    text-align:center;
    display:flex;
    flex-direction:column;
    gap:6px;
}

.card img{
    width:100%;
    height:auto;
    object-fit:contain;
    max-height:220px;
    margin-bottom:5px;
}

/* ✅ ADD IT HERE */
.card h4, .card p {
    margin:3px 0;
}

.price{
    font-weight:bold;
    color:green;
}
</style>
</style>
</head>

<body>

<header>
<div class="logo">
<img src="/static/logo.png">
<div>
<div style="font-weight:bold;">SPARE FORGE SPARES</div>
<div style="font-size:12px;">Your garage online</div>
</div>
</div>

<form>
<input class="search" name="q" placeholder="Search by name or part number">
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
<img src="{{p[3]}}">
{% endif %}

<h4>{{p[0]}}</h4>
<p> {{ p[6] if p[6] else "N/A" }}</p>

<div class="price">
Ksh {{p[1]}}<br>

{% if p[2] and p[2]|float > 0 %}
<span class="old">Ksh {{ "{:,.0f}".format(p[2]) }}</span>
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
<p>facebook: spare forge
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
    if request.method == "POST":
        if request.form.get("u") == ADMIN_USER and request.form.get("p") == ADMIN_PASS:
            session["admin"] = True
            return redirect("/dashboard")

    return """
<form method="post">
<input name="u" placeholder="username"><br><br>
<input name="p" type="password"><br><br>
<button>Login</button>
</form>
"""

# ---------------- DELETE ----------------
@app.route("/delete/<int:pid>")
def delete(pid):
    if not session.get("admin"):
        return redirect("/hidden-admin-portal")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET","POST"])
def dash():
    if not session.get("admin"):
        return redirect("/hidden-admin-portal")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        file = request.files.get("i")
        image_path = ""

        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            image_path = "/" + path

        try:
            price = int(request.form.get("p","0").replace(",",""))
        except:
            price = 0

        try:
            old_price = float(request.form.get("old_price") or 0)
        except:
            old_price = 0

        c.execute("""
        INSERT INTO products(
        name,price,old_price,image,code,
        part_name,part_number,part_description,
        part_category,part_condition,brand
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """,(
            request.form.get("n",""),
            price,
            old_price,
            image_path,
            code(),

            "",
            request.form.get("pnum",""),
            "",
            "",
            "",
            request.form.get("brand","")
        ))

        conn.commit()
        return redirect("/dashboard")

    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return render_template_string("""
<h2>Dashboard</h2>

<form method="post" enctype="multipart/form-data">

<input name="n" placeholder="Name"><br>
<input name="p" placeholder="Price"><br>
<input name="old_price" placeholder="Old Price"><br>
<input name="pnum" placeholder="Part Number"><br>

<select name="brand">
<option>Nissan</option>
<option>Volkswagen</option>
<option>BMW</option>
<option>Mercedes</option>
<option>Mazda</option>
<option>Toyota</option>
<option>Subaru</option>
</select><br><br>

<input type="file" name="i"><br><br>

<button>Add Product</button>
</form>

<hr>

{% for p in products %}
<p>
<b>{{p[0]}}</b> - Ksh {{p[1]}}
<a href="/delete/{{p[11]}}" onclick="return confirm('Delete product?')">❌ Delete</a>
</p>
{% endfor %}
""", products=products)

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
