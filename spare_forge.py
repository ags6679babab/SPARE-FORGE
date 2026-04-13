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
<a href="/delete/{{p[11]}}" onclick="return confirm('Delete product?')">Delete</a>
</p>
{% endfor %}
""", products=products)
