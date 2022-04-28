
from pickletools import read_unicodestring1
import sqlite3 as SQL
from tokenize import String
from flask import Flask, redirect, render_template, request, session
from flask_session.__init__ import Session
# from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)    


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    products = dbCall("SELECT * FROM products")
    categories = dbCall("SELECT * FROM categories")
    # print(f"table: {products}")
    # print(f"session: {session['test']}")    
    return render_template("index.html", products=products, categories=categories)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    print(request.method)
    if request.method == "POST":
        print("This is a post request")
        return redirect("/")
    else:
        print("this is a get request")
        return render_template("login.html")
@app.route("/contact")
def contact():
    return render_template("contact.html")

def dbCall(query):    
    conn = SQL.connect("shop.db", check_same_thread=False)
    db = conn.cursor()
    data = db.execute(query).fetchall()
    print(f"fetch data: {data}")
    newData = []
    for row in data:
        tmp = []
        for atr in row:
            tmp.append(atr)
            
        newData.append(tmp)
    conn.commit()
    db.close()
    return newData  


# INSERT INTO categories (name) VALUES ('cpu');
# INSERT INTO categories (name) VALUES ('psu');
# INSERT INTO categories (name) VALUES ('gpu');
# INSERT INTO categories (name) VALUES ('ram');
# INSERT INTO categories (name) VALUES ('storage');
# INSERT INTO categories (name) VALUES ('case');

# INSERT INTO products (name, price, description, category, image) VALUES ('AMD Ryzen 9 5900X', 3400, 'Processor 3.7 GHz, Unlocked 12 kerner, 24 tråde, 70MB cache', 1, 'https://gyazo.com/451d7646bd9add6c02be502914d6979e');
# INSERT INTO products (name, price, description, category, image) VALUES ('AMD Ryzen 7 5800X', 2650, 'Processor 3.8 GHz, Unlocked 8 kerner, 16 tråde, 36MB cache', 1, 'https://gyazo.com/cbd003d4232bb7587014445017e8c5a7');
# INSERT INTO products (name, price, description, category, image) VALUES ('AMD Ryzen 5 5900X', 1899, 'Processor 3.7 GHz, Unlocked 6 kerner, 12 tråde, 32MB cache', 1, 'https://gyazo.com/a8443ef6b41a276586b712f717ed24b7');
# INSERT INTO products (name, price, description, category, image) VALUES ('Intel Core i9-12900K Alder Lake', 4790, 'Processor 3.2 GHz, Unlocked 12 kerner, 24 tråde, 14MB cache', 1, 'https://gyazo.com/5df21c3e03f8688ed41d2b14a2440c7c');
# INSERT INTO products (name, price, description, category, image) VALUES ('Intel Core i7-12700K Alder Lake', 3290, 'Processor 3.6 GHz, Unlocked 12 kerner, 20 tråde, 12MB cache', 1, 'https://gyazo.com/b4b0dad68f6fe2c64da058a5bd2849ae');
# INSERT INTO products (name, price, description, category, image) VALUES ('Intel Core i5-12600K Alder Lake', 2400, 'Processor 3.7 GHz, Unlocked 10 kerner, 16 tråde, 9.5MB cache', 1, 'https://gyazo.com/41ce16644196cb155a5a195afb78b29c');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair RM850', 999, 'Strømforsyning ATX12V 2.52 / EPS12V 2.92, 80 Plus Gold, 850Watt', 2, 'https://gyazo.com/3c03b75202f58e0c4df342088b761a52');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair RM1000x', 1399, 'Strømforsyning ATX12V 2.4 / EPS12V 2.92, 80 Plus Gold, 1000Watt', 2, 'https://gyazo.com/5bb7e9b4ace75a3a410f416386ee33f6');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair RM650', 699, 'Strømforsyning ATX12V 2.52 / EPS12V 2.92, 80 Plus Gold, 650Watt', 2, 'https://gyazo.com/72fad975e5954e0a09b9ae9bdeac1772');
# INSERT INTO products (name, price, description, category, image) VALUES ('ASUS GeForce RTX 3090 Ti TUF', 17890, 'Grafikkort, NVIDIA GeForce 3090 Ti, 10752 CUDA kerner, 24GB GDDR6X', 3, 'https://gyazo.com/75d34c891524c350fb9475b461439ff8');
# INSERT INTO products (name, price, description, category, image) VALUES ('ASUS GeForce RTX 3080 Ti TUF', 9795, 'Grafikkort, NVIDIA GeForce 3080 Ti, 10240 CUDA kerner, 12GB GDDR6X', 3, 'https://gyazo.com/bb581e7c6fc5bdd099a2390181378f88');
# INSERT INTO products (name, price, description, category, image) VALUES ('ASUS GeForce RTX 3070 Ti TUF', 5590, 'Grafikkort, NVIDIA GeForce 3070 Ti, 6144 CUDA kerner, 8GB GDDR6X', 3, 'https://gyazo.com/9f6e6c7ab6ad13348d79846c92ef2f2f');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair Vengeance LPX DDR4 - 16GB', 610, 'Hukommelse, 16GB: 2 x 8 GB, DIMM 288-pin 3200MHz / PC4-25600', 4, 'https://gyazo.com/c530b97f21e02ee75399a63777fbdc8b');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair Vengeance LPX DDR4 - 32GB', 1120, 'Hukommelse, 32GB: 2 x 16 GB, DIMM 288-pin 3200MHz / PC4-25600', 4, 'https://gyazo.com/c530b97f21e02ee75399a63777fbdc8b');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair Vengeance RGB PRO DDR4 - 16GB', 689, 'Hukommelse, 16GB: 2 x 8 GB, DIMM 288-pin 3600MHz / PC4-28800', 4, 'https://gyazo.com/3d1cf170bce59a8b15c957813acde521');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair Vengeance RGB PRO DDR4 - 32GB', 1288, 'Hukommelse, 32GB: 2 x 16 GB, DIMM 288-pin 3600MHz / PC4-28800', 4, 'https://gyazo.com/3d1cf170bce59a8b15c957813acde521');
# INSERT INTO products (name, price, description, category, image) VALUES ('Samsung 980 PRO SSD - 2TB', 2293, 'SSD, 2 TB, intern, 7000 MBps (læs) / 5100 MBps (skriv), 2GB LPDDR4 cache', 5, 'https://gyazo.com/135afb1593e164749ee8d3a626d1cc00');
# INSERT INTO products (name, price, description, category, image) VALUES ('Samsung 980 PRO SSD - 1TB', 1215, 'SSD, 1 TB, intern, 7000 MBps (læs) / 5100 MBps (skriv), 1GB LPDDR4 cache', 5, 'https://gyazo.com/29d0c7eb9482441082206fe55b041d86');
# INSERT INTO products (name, price, description, category, image) VALUES ('Samsung 970 EVO Plus SSD - 500GB', 564, 'SSD, 500 GB, intern, 3500 MBps (læs) / 3200 MBps (skriv), 512MB LPDDR4 cache', 5, 'https://gyazo.com/016910bf57cf05ed35f8be6698968620');
# INSERT INTO products (name, price, description, category, image) VALUES ('Corsair 4000D AIRFLOW TG - Black', 749, 'Miditower, ATX, ingen strømforsyning, front 1 x USB 3.0, 1 x USB 3.1 Type C', 6, 'https://gyazo.com/ffa548f0bfa613e419155c567b8aef69');
# INSERT INTO products (name, price, description, category, image) VALUES ('DUTZO C320 TG RGB - Black', 299, 'Miditower, ATX, ingen strømforsyning, front med RGB knap, 2 x USB 2.0, 1 x USB 3.0', 6, 'https://gyazo.com/4e4f90f9a09b1be3a9b77cfd4a2740a5');
# INSERT INTO products (name, price, description, category, image) VALUES ('Cooler Master MasterBox Lite 5 ARGB - Black', 499, 'Miditower, ATX, ingen strømforsyning, front med RGB knap, 2 x USB 3.2 Gen 1 Type A', 6, 'https://gyazo.com/64f0c63ce2829e17d32c116c89afc842');
# INSERT INTO products (name, price, description, category, image) VALUES ('Seagate BarraCuda 3.5" ST2000DM008', 402, 'Harddisk, 2 TB, intern, 3.5", SATA-600, 7200 rpm, buffer: 256 MB - ST2000DM008', 5, 'https://gyazo.com/09c4f81520f4f0bf4ca79f420e6184c1');
# INSERT INTO products (name, price, description, category, image) VALUES ('Seagate BarraCuda 3.5" ST4000DM004', 667, 'Harddisk, 4 TB, intern, 3.5", SATA-600, 5400 rpm, buffer: 256 MB - ST4000DM004', 5, 'https://gyazo.com/2d81e2e4a815bdf18d118d9581a741f2');