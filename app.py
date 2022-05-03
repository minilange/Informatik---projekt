from math import prod
import sqlite3 as SQL
from string import punctuation
from flask import Flask, redirect, render_template, request, session
from datetime import datetime
from flask_session.__init__ import Session
from string import punctuation, digits, ascii_lowercase as lower, ascii_uppercase as upper
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)    

conn = SQL.connect("shop.db", check_same_thread=False)
db = conn.cursor()


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    products = readDB("SELECT * FROM products")
    categories = readDB("SELECT * FROM categories")
    
    return render_template("index.html", products=products, categories=categories, active_category='all')

@app.route("/sortCategories", methods=["GET", "POST"])
def sort():
    category_name = request.form.get("category_name")
    print(category_name)
    category = readDB(f"SELECT * FROM categories WHERE name='{category_name}'")[0][0]
    products = readDB(f"SELECT * FROM products WHERE category='{category}'")
    categories = readDB("SELECT * FROM categories")

    return render_template("index.html", products=products, categories=categories, active_category=category_name)

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "" or password == "":
            return render_template("login.html", error="Please fill in all fields")

        dbUser = readDB(f"SELECT * FROM users WHERE username = '{username}'")

        if len(dbUser) == 0:
            return render_template("login.html", error="User does not exist")
        
        dbUser = dbUser[0]
        
        if not check_password_hash(dbUser[3], password):
            return render_template("login.html", error="Incorrect username and/or password")

        session["user"] = username
        session["user_id"] = dbUser[0]
        
        if dbUser[4] == 1:
            session["admin"] = True
        
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        email = request.form.get("email")

        if username == "" or password == "" or confirm == "" or email == "":
            return render_template("register.html", error="Udfyld venligst alle felter")

        if email.count("@") != 1 and email.count(".") == 0:
            return render_template("register.html", error="Indtast venligst en gyldig email")

        if password != confirm:
            return render_template("register.html", error="Adgangskoder er ikke ens")

        upper = False
        punct = False
        number = False

        for ele in password:
            if ele.isupper():
                upper = True
            elif ele.isnumeric():
                number = True
            elif ele in punctuation:
                punct = True

        if len(password) < 8 or not upper or not punct or not number:
            return render_template("register.html", error="Adgangskode skal indeholde mindst 8 tegn, 1 stort bogstav og 1 tal")

        dbUser = readDB(f"SELECT * FROM users WHERE username = '{username}'")

        if len(dbUser) != 0:
            return render_template("register.html", error="Brugernavn er allerede taget")
        
        db.execute("INSERT INTO users (username, password, email, admin) VALUES (?, ?, ?, 0)", (username, generate_password_hash(password), email))
        conn.commit()

        return redirect("/login")
    else:
        print("This is a get request")
        return render_template("register.html")

@app.route("/contact")
def contact():

    return render_template("contact.html")

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/")
    
    orders = []

    users = readDB("SELECT `username`, email, `timestamp`, `order_id` FROM orders INNER JOIN users ON orders.user_id = users.id")

    for user in users:
        tmp_orders = {}
        tmp_orders["user_info"] = user
        tmp_orders["products"] = readDB(f"SELECT p.name, p.price, p.category, p.image, orderlines.quantity FROM orderlines INNER JOIN products AS p ON orderlines.product_id = p.id WHERE order_id = {user[3]}")

        tmp_orders["total_price"] = readDB(f"SELECT SUM(price) FROM orderlines INNER JOIN products ON orderlines.product_id = products.id WHERE order_id = {user[3]}")[0][0]
        orders.append(tmp_orders)

    return render_template("admin.html", orders=orders)

@app.route("/addToCart", methods=["GET", "POST"])
def addToCart():
    product_id = request.form.get("product_id")
    
    try:
        if session["cart"].get(product_id) == None:
            session["cart"][product_id] = []
            session["cart"][product_id].append(1)
            session["cart"][product_id].append(request.form.get("product_name"))
            print(f"Added {product_id} to cart")
        else:
            session["cart"][product_id][0] += 1
            print(f"Added {product_id} to cart with quantity {session['cart'][product_id]}")
        
        print(f"cart: {session['cart']}")
        return redirect("/")
    except KeyError:
        print("session['cart'] is empty")
        session["cart"] = {}
        session["cart"][product_id] = []
        session["cart"][product_id].append(1)
        session["cart"][product_id].append(request.form.get("product_name"))
        return redirect("/")

@app.route("/removeFromCart", methods=["GET", "POST"])
def removeFromCart():
    product_id = request.args.get("id")
    
    session["cart"].pop(product_id, None)
    print(f"cart: {session['cart']}")
    return redirect("/")


@app.route("/cart", methods=["GET", "POST"])
def cart():
    
    if request.method == "POST":
        if not session.get("user_id"):
            return redirect("/login")
        
        db.execute(f"INSERT INTO orders (user_id, timestamp) VALUES ({session['user_id']}, '{datetime.now()}')")
        conn.commit()

        order_id = readDB(f"SELECT order_id FROM orders WHERE user_id = {session['user_id']} ORDER BY timestamp DESC LIMIT 1")[0][0]

        for product_id in session["cart"]:
            print(session["cart"][product_id])
            
            db.execute(f"INSERT INTO orderlines (order_id, product_id, quantity) VALUES ({order_id}, {product_id}, {session['cart'][product_id][0]})")
            conn.commit()

        session["cart"] = {}
        return redirect("/")
    else:
        products = []
        totalPrice = 0
        if session.get("cart"):
            for key in session["cart"]:
                product = readDB(f"SELECT * FROM products WHERE id = {key}")[0]
                product.append(session["cart"][key][0])
                products.append(product)
                totalPrice += product[2]

        return render_template("cart.html", products=products, totalPrice=totalPrice)

def readDB(query):    
    data = db.execute(query).fetchall()
    
    newData = []
    for row in data:
        tmp = []
        for atr in row:
            tmp.append(atr)
            
        newData.append(tmp)
    conn.commit()
    return newData

if __name__ == "__main__":
    app.run(debug=True)

# INSERT INTO categories (name) VALUES ('cpu');
# INSERT INTO categories (name) VALUES ('psu');
# INSERT INTO categories (name) VALUES ('gpu');
# INSERT INTO categories (name) VALUES ('ram');
# INSERT INTO categories (name) VALUES ('storage');
# INSERT INTO categories (name) VALUES ('case');

# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('AMD Ryzen 9 5900X', 3400, 'Processor 3.7 GHz, Unlocked 12 kerner, 24 tråde, 70MB cache', 1, 'https://gyazo.com/451d7646bd9add6c02be502914d6979e', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('AMD Ryzen 7 5800X', 2650, 'Processor 3.8 GHz, Unlocked 8 kerner, 16 tråde, 36MB cache', 1, 'https://gyazo.com/cbd003d4232bb7587014445017e8c5a7', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('AMD Ryzen 5 5600X', 1899, 'Processor 3.7 GHz, Unlocked 6 kerner, 12 tråde, 32MB cache', 1, 'https://gyazo.com/a8443ef6b41a276586b712f717ed24b7', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Intel Core i9-12900K Alder Lake', 4790, 'Processor 3.2 GHz, Unlocked 12 kerner, 24 tråde, 14MB cache', 1, 'https://gyazo.com/5df21c3e03f8688ed41d2b14a2440c7c', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Intel Core i7-12700K Alder Lake', 3290, 'Processor 3.6 GHz, Unlocked 12 kerner, 20 tråde, 12MB cache', 1, 'https://gyazo.com/b4b0dad68f6fe2c64da058a5bd2849ae', 100;
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Intel Core i5-12600K Alder Lake', 2400, 'Processor 3.7 GHz, Unlocked 10 kerner, 16 tråde, 9.5MB cache', 1, 'https://gyazo.com/41ce16644196cb155a5a195afb78b29c', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair RM850', 999, 'Strømforsyning ATX12V 2.52 / EPS12V 2.92, 80 Plus Gold, 850Watt', 2, 'https://gyazo.com/3c03b75202f58e0c4df342088b761a52', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair RM1000x', 1399, 'Strømforsyning ATX12V 2.4 / EPS12V 2.92, 80 Plus Gold, 1000Watt', 2, 'https://gyazo.com/5bb7e9b4ace75a3a410f416386ee33f6', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair RM650', 699, 'Strømforsyning ATX12V 2.52 / EPS12V 2.92, 80 Plus Gold, 650Watt', 2, 'https://gyazo.com/72fad975e5954e0a09b9ae9bdeac1772', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('ASUS GeForce RTX 3090 Ti TUF', 17890, 'Grafikkort, NVIDIA GeForce 3090 Ti, 10752 CUDA kerner, 24GB GDDR6X', 3, 'https://gyazo.com/75d34c891524c350fb9475b461439ff8', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('ASUS GeForce RTX 3080 Ti TUF', 9795, 'Grafikkort, NVIDIA GeForce 3080 Ti, 10240 CUDA kerner, 12GB GDDR6X', 3, 'https://gyazo.com/bb581e7c6fc5bdd099a2390181378f88', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('ASUS GeForce RTX 3070 Ti TUF', 5590, 'Grafikkort, NVIDIA GeForce 3070 Ti, 6144 CUDA kerner, 8GB GDDR6X', 3, 'https://gyazo.com/9f6e6c7ab6ad13348d79846c92ef2f2f', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair Vengeance LPX DDR4 - 16GB', 610, 'Hukommelse, 16GB: 2 x 8 GB, DIMM 288-pin 3200MHz / PC4-25600', 4, 'https://gyazo.com/c530b97f21e02ee75399a63777fbdc8b', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair Vengeance LPX DDR4 - 32GB', 1120, 'Hukommelse, 32GB: 2 x 16 GB, DIMM 288-pin 3200MHz / PC4-25600', 4, 'https://gyazo.com/c530b97f21e02ee75399a63777fbdc8b', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair Vengeance RGB PRO DDR4 - 16GB', 689, 'Hukommelse, 16GB: 2 x 8 GB, DIMM 288-pin 3600MHz / PC4-28800', 4, 'https://gyazo.com/3d1cf170bce59a8b15c957813acde521', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair Vengeance RGB PRO DDR4 - 32GB', 1288, 'Hukommelse, 32GB: 2 x 16 GB, DIMM 288-pin 3600MHz / PC4-28800', 4, 'https://gyazo.com/3d1cf170bce59a8b15c957813acde521', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Samsung 980 PRO SSD - 2TB', 2293, 'SSD, 2 TB, intern, 7000 MBps (læs) / 5100 MBps (skriv), 2GB LPDDR4 cache', 5, 'https://gyazo.com/135afb1593e164749ee8d3a626d1cc00', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Samsung 980 PRO SSD - 1TB', 1215, 'SSD, 1 TB, intern, 7000 MBps (læs) / 5100 MBps (skriv), 1GB LPDDR4 cache', 5, 'https://gyazo.com/29d0c7eb9482441082206fe55b041d86', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Samsung 970 EVO Plus SSD - 500GB', 564, 'SSD, 500 GB, intern, 3500 MBps (læs) / 3200 MBps (skriv), 512MB LPDDR4 cache', 5, 'https://gyazo.com/016910bf57cf05ed35f8be6698968620', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Corsair 4000D AIRFLOW TG - Black', 749, 'Miditower, ATX, ingen strømforsyning, front 1 x USB 3.0, 1 x USB 3.1 Type C', 6, 'https://gyazo.com/ffa548f0bfa613e419155c567b8aef69', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('DUTZO C320 TG RGB - Black', 299, 'Miditower, ATX, ingen strømforsyning, front med RGB knap, 2 x USB 2.0, 1 x USB 3.0', 6, 'https://gyazo.com/4e4f90f9a09b1be3a9b77cfd4a2740a5', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Cooler Master MasterBox Lite 5 ARGB - Black', 499, 'Miditower, ATX, ingen strømforsyning, front med RGB knap, 2 x USB 3.2 Gen 1 Type A', 6, 'https://gyazo.com/64f0c63ce2829e17d32c116c89afc842', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Seagate BarraCuda 3.5" ST2000DM008', 402, 'Harddisk, 2 TB, intern, 3.5", SATA-600, 7200 rpm, buffer: 256 MB - ST2000DM008', 5, 'https://gyazo.com/09c4f81520f4f0bf4ca79f420e6184c1', 100);
# INSERT INTO products (name, price, description, category, image, quantity) VALUES ('Seagate BarraCuda 3.5" ST4000DM004', 667, 'Harddisk, 4 TB, intern, 3.5", SATA-600, 5400 rpm, buffer: 256 MB - ST4000DM004', 5, 'https://gyazo.com/2d81e2e4a815bdf18d118d9581a741f2', 100);