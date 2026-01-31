from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, desc TEXT, image TEXT)''')
    
    # Seed Data (Now with "images" - using emoji as placeholders for simplicity)
    if c.execute("SELECT count(*) FROM users").fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
        c.execute("INSERT INTO users (username, password) VALUES ('john', 'securepass')")
        
    if c.execute("SELECT count(*) FROM products").fetchone()[0] == 0:
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('The AI Sentinel', 59, 'Mastering Adversarial Machine Learning.', '🤖')")
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('Black Hat Python', 45, 'Python programming for hackers and pentesters.', '🐍')")
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('SQL Injection Bible', 30, 'The complete guide to database exploitation.', '💉')")
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('Zero Day', 25, 'A novel about the end of the internet.', '💀')")
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('Ghost in the Wires', 15, 'My adventures as the world''s most wanted hacker.', '👻')")
        c.execute("INSERT INTO products (name, price, desc, image) VALUES ('Blue Team Handbook', 55, 'Incident response & digital forensics.', '🛡️')")
    
    conn.commit()
    conn.close()

# --- MODERN UI TEMPLATES ---

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuroShop | Secure Tech Books</title>
    <style>
        :root {
            --primary: #2563eb;
            --secondary: #1e293b;
            --accent: #f59e0b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #334155;
        }
        body { margin: 0; font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); }
        
        /* Navbar */
        nav { background: var(--secondary); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .logo { color: white; font-weight: 800; font-size: 1.5rem; text-decoration: none; display: flex; align-items: center; gap: 10px; }
        .nav-links a { color: #cbd5e1; text-decoration: none; margin-left: 20px; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: white; }
        .login-btn { background: var(--primary); padding: 8px 20px; border-radius: 6px; color: white !important; }

        /* Container */
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        
        /* Hero */
        .hero { text-align: center; margin-bottom: 50px; }
        .hero h1 { font-size: 3rem; margin-bottom: 10px; color: var(--secondary); }
        .hero p { font-size: 1.2rem; color: #64748b; }

        /* Search Bar */
        .search-container { max-width: 600px; margin: 0 auto 50px auto; display: flex; gap: 10px; }
        .search-input { flex: 1; padding: 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1rem; outline: none; transition: border-color 0.3s; }
        .search-input:focus { border-color: var(--primary); }
        .search-btn { padding: 0 30px; background: var(--secondary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
        .search-btn:hover { background: var(--primary); }

        /* Product Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; }
        .card { background: var(--card-bg); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); transition: transform 0.2s, box-shadow 0.2s; border: 1px solid #e2e8f0; display: flex; flex-direction: column; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .card-img { height: 200px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-size: 5rem; }
        .card-body { padding: 20px; flex: 1; display: flex; flex-direction: column; }
        .card h3 { margin: 0 0 10px 0; font-size: 1.25rem; }
        .card h3 a { color: var(--secondary); text-decoration: none; }
        .price { font-size: 1.5rem; color: var(--primary); font-weight: 700; margin-bottom: 10px; }
        .desc { color: #64748b; line-height: 1.5; font-size: 0.95rem; flex: 1; }
        .btn-buy { margin-top: 15px; width: 100%; padding: 10px; background: white; border: 2px solid var(--primary); color: var(--primary); font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
        .btn-buy:hover { background: var(--primary); color: white; }

        /* Forms (Login) */
        .auth-card { max-width: 400px; margin: 50px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center; }
        .form-group { margin-bottom: 20px; text-align: left; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--secondary); }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 6px; box-sizing: border-box; }
        .btn-primary { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 6px; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .error-msg { background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 6px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <nav>
        <a href="/" class="logo">🧠 NeuroShop</a>
        <div class="nav-links">
            <a href="/">Books</a>
            <a href="/login" class="login-btn">
                {% if session.get('user') %}
                    👤 {{ session.user }} (Logout)
                {% else %}
                    Login
                {% endif %}
            </a>
        </div>
    </nav>

    <div class="container">
        {{ content|safe }}
    </div>

    <footer style="text-align: center; color: #94a3b8; margin-top: 50px; padding: 20px;">
        &copy; 2026 NeuroShop. Security is not a feature, it's a lifestyle.
    </footer>
</body>
</html>
"""

# --- PAGES ---

PAGE_HOME = """
    <div class="hero">
        <h1>Curated for Cyber Punks.</h1>
        <p>The world's most vulnerable bookstore. Can you find the hidden exploits?</p>
    </div>

    <div class="search-container">
        <form action="/search" method="GET" style="display: flex; width: 100%; gap: 10px;">
            <input type="text" class="search-input" name="q" placeholder="Search titles, authors, or inject SQL...">
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>

    <div class="grid">
        {% for p in products %}
            <div class="card">
                <div class="card-img">{{ p[4] }}</div>
                <div class="card-body">
                    <div class="price">${{ p[2] }}</div>
                    <h3><a href="/product/{{ p[0] }}">{{ p[1] }}</a></h3>
                    <div class="desc">{{ p[3] }}</div>
                    <button class="btn-buy" onclick="alert('This feature is vulnerable to IDOR!')">Add to Cart</button>
                </div>
            </div>
        {% endfor %}
    </div>
"""

PAGE_LOGIN = """
    <div class="auth-card">
        <h2 style="margin-bottom: 30px;">Welcome Back</h2>
        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Try: admin' --">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="********">
            </div>
            <button type="submit" class="btn-primary">Secure Login</button>
        </form>
        <p style="margin-top: 20px; color: #94a3b8; font-size: 0.9rem;">
            Hint: The database is SQLite.
        </p>
    </div>
"""

PAGE_SEARCH = """
    <div class="search-container">
        <form action="/search" method="GET" style="display: flex; width: 100%; gap: 10px;">
            <input type="text" class="search-input" name="q" value="{{ query }}" placeholder="Search...">
            <button type="submit" class="search-btn">Search</button>
        </form>
    </div>

    <h3>Results for: <span style="color: var(--primary);">{{ query|safe }}</span></h3>
    
    {% if products %}
        <div class="grid" style="margin-top: 30px;">
            {% for p in products %}
                <div class="card">
                    <div class="card-img">{{ p[4] }}</div>
                    <div class="card-body">
                        <div class="price">${{ p[2] }}</div>
                        <h3>{{ p[1] }}</h3>
                        <div class="desc">{{ p[3] }}</div>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <div style="text-align: center; padding: 50px; color: #94a3b8;">
            <h2>No results found.</h2>
            <p>Try searching for "Python" or using a UNION SELECT attack.</p>
        </div>
    {% endif %}
"""

PAGE_PRODUCT = """
    <div class="auth-card" style="max-width: 800px; text-align: left; display: flex; gap: 40px; align-items: flex-start;">
        <div style="font-size: 8rem; background: #f1f5f9; padding: 40px; border-radius: 12px;">
            {{ product[4] }}
        </div>
        <div>
            <h1 style="margin-top: 0;">{{ product[1] }}</h1>
            <div class="price" style="font-size: 2.5rem; margin: 20px 0;">${{ product[2] }}</div>
            <p style="line-height: 1.6; color: #64748b; font-size: 1.1rem;">
                {{ product[3] }}
            </p>
            <br>
            <a href="/" style="color: var(--primary); font-weight: 600; text-decoration: none;">&larr; Back to Shop</a>
        </div>
    </div>
"""

PAGE_404 = """
    <div style="text-align: center; padding: 100px;">
        <div style="font-size: 5rem;">🚫</div>
        <h1>Product Not Found</h1>
        <p>Or maybe you just broke the database query?</p>
        <a href="/" class="btn-buy" style="display: inline-block; width: auto; padding: 10px 30px; margin-top: 20px; text-decoration: none;">Go Home</a>
    </div>
"""

# --- ROUTES (Logic remains Vulnerable) ---

@app.route('/')
def home():
    conn = sqlite3.connect('shop.db')
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    
    # Render Home
    content = render_template_string(PAGE_HOME, products=products)
    return render_template_string(BASE_LAYOUT, content=content, session=session)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user clicks Logout (hacky way for single file)
    if session.get('user'):
        session.pop('user', None)
        return redirect('/')

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # VULNERABLE SQL QUERY
        conn = sqlite3.connect('shop.db')
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"⚠️ [VULN] Executing SQL: {query}")
        try:
            user = conn.execute(query).fetchone()
            if user:
                session['user'] = user[1]
                return redirect('/')
            else:
                error = "Invalid Credentials"
        except Exception as e:
            error = f"Database Error: {e}"
        finally:
            conn.close()
            
    content = render_template_string(PAGE_LOGIN, error=error)
    return render_template_string(BASE_LAYOUT, content=content, session=session)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    products = []
    if query:
        # VULNERABLE SQL QUERY
        conn = sqlite3.connect('shop.db')
        sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
        print(f"⚠️ [VULN] Executing SQL: {sql}")
        try:
            products = conn.execute(sql).fetchall()
        except Exception as e:
            print(f"❌ SQL Error: {e}")
        conn.close()
    
    content = render_template_string(PAGE_SEARCH, query=query, products=products)
    return render_template_string(BASE_LAYOUT, content=content, session=session)

@app.route('/product/<id>')
def product(id):
    conn = sqlite3.connect('shop.db')
    product = None
    try:
        # VULNERABLE ID
        product = conn.execute(f"SELECT * FROM products WHERE id = {id}").fetchone()
    except:
        pass
    conn.close()
    
    if product:
        content = render_template_string(PAGE_PRODUCT, product=product)
    else:
        content = PAGE_404
        
    return render_template_string(BASE_LAYOUT, content=content, session=session)

if __name__ == '__main__':
    init_db()
    print("🛒 NeuroShop v2.0 running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)