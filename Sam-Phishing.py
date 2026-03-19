import os
from flask import Flask, request, render_template_string, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = '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'

# 1. Go'aaminta Waddada (Path): Desktop\Data
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
data_folder = os.path.join(desktop_path, "Data")

# Abuur Folder-ka 'Data' haddii uusan jirin
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    print(f"Folder-ka 'Data' waa la abuuray: {data_folder}")

# Magacyada Faylasha
reg_file_path = os.path.join(data_folder, "Reg_Users.txt")
log_file_path = os.path.join(data_folder, "Loginfo.txt")


def init_files():
    """Hubi in faylashu jiraan."""
    if not os.path.exists(reg_file_path):
        with open(reg_file_path, 'w') as f:
            f.write("")
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            f.write("")


init_files()

# HTML Templates
HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Nidaamka Diwaangelinta</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #e9ecef; padding: 40px; }
        .container { background: white; padding: 30px; border-radius: 10px; max-width: 450px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        h2 { text-align: center; color: #333; }
        label { font-weight: bold; display: block; margin-top: 10px; }
        input { width: 100%; padding: 12px; margin: 8px 0 20px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .success { color: #155724; background: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        a { display: block; text-align: center; margin-top: 20px; color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {{ content | safe }}
    </div>
</body>
</html>
"""

LOGIN_FORM = """
<h2>Gal (Login)</h2>
<form method="POST" action="/login">
    <label>Email:</label>
    <input type="email" name="email" required placeholder="Gali Email-kaaga">

    <label>Password:</label>
    <input type="password" name="password" required placeholder="Gali Password-kaaga">

    <label>Number:</label>
    <input type="text" name="number" required placeholder="Gali Lambarkaaga">

    <button type="submit">Gal</button>
</form>
<a href="/register">Ma lihin account? Diwaangeli (Sign Up)</a>
"""

REGISTER_FORM = """
<h2>Diwaangeli (Sign Up)</h2>
<form method="POST" action="/register">
    <label>Email:</label>
    <input type="email" name="email" required placeholder="Tusaale: email@gmail.com">

    <label>Password:</label>
    <input type="password" name="password" required placeholder="Dooro Password">

    <label>Confirm Password:</label>
    <input type="password" name="confirm_password" required placeholder="Ku celi Password-ka">

    <label>Number:</label>
    <input type="text" name="number" required placeholder="Lambarkaaga">

    <label>Recovery Email:</label>
    <input type="email" name="recovery_email" required placeholder="Email kale oo soo celin ah">

    <button type="submit">Diwaangeli</button>
</form>
<a href="/login">Horey ma u diwaangashan tahay? Gal (Login)</a>
"""


def check_user_exists(email):
    """Hubi in email-ku horey u diwaangashan yahay Reg_Users.txt."""
    if not os.path.exists(reg_file_path):
        return False

    with open(reg_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Raadi "Email: email_value"
        target = f"Email: {email}"
        if target in content:
            return True
    return False


def get_user_details(email, password, number):
    """Ka soo qaad xogta saxda ah ee user-ka Reg_Users.txt si loo hubiyo Login-ka."""
    if not os.path.exists(reg_file_path):
        return None

    with open(reg_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_user = {}
    found = False

    for line in lines:
        line = line.strip()
        if line.startswith("======================"):
            if found and current_user.get('email') == email:
                # Hubi Password iyo Number
                if current_user.get('password') == password and current_user.get('number') == number:
                    return current_user
                else:
                    return None  # Password ama Number khaldan
            # Reset for next user block
            current_user = {}
            found = False

        elif line.startswith("Email:"):
            current_user['email'] = line.split("Email:")[1].strip()
            if current_user['email'] == email:
                found = True
        elif line.startswith("Password:"):
            current_user['password'] = line.split("Password:")[1].strip()
        elif line.startswith("Number:"):
            current_user['number'] = line.split("Number:")[1].strip()

    # Check the last block if file doesn't end with separator
    if found and current_user.get('email') == email:
        if current_user.get('password') == password and current_user.get('number') == number:
            return current_user

    return None


def save_registration(email, password, number, recovery_email):
    """Keydi xogta Register-ka qaab tix ah."""
    with open(reg_file_path, 'a', encoding='utf-8') as f:
        f.write("======================\n")
        f.write(f"Email: {email}\n")
        f.write(f"Password: {password}\n")  # Password-ka oo toos ah la soo muujiyay
        f.write(f"Number: {number}\n")
        f.write(f"Recovery Email: {recovery_email}\n")
        f.write("\n")  # Xarig madhan oo kala saaraya


def save_login_attempt(email, password, number, status):
    """Keydi isku dayga Login-ka qaab tix ah."""
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write("======================\n")
        f.write(f"Login Time: (Auto-generated)\n")
        f.write(f"Email: {email}\n")
        f.write(f"Password: {password}\n")  # Password-ka la galiyay
        f.write(f"Number: {number}\n")
        f.write(f"Status: {status}\n")
        f.write("\n")


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        number = request.form['number']

        # Hubi xogta
        user = get_user_details(email, password, number)

        if user:
            save_login_attempt(email, password, number, "SUCCESS")
            flash('Si guul leh ayaad u gashay! (Login Successful)', 'success')
        else:
            save_login_attempt(email, password, number, "FAILED")
            flash('Email, Password, ama Number khaldan ayaa la galiyay.', 'error')

    return render_template_string(HTML_LAYOUT, content=LOGIN_FORM)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        number = request.form['number']
        recovery_email = request.form['recovery_email']

        # 1. Hubi in Password-yadu is waafaqsan yihiin
        if password != confirm_password:
            flash('Password-yada isku ma waafaqsana!', 'error')
            return render_template_string(HTML_LAYOUT, content=REGISTER_FORM)

        # 2. Hubi in Email-ku uusan horey u diwaangashanayn
        if check_user_exists(email):
            flash('Email-kani horey ayuu u diwaangashan yahay.', 'error')
            return render_template_string(HTML_LAYOUT, content=REGISTER_FORM)

        # 3. Keydi xogta
        save_registration(email, password, number, recovery_email)

        flash('Si guul leh ayaad u diwaangashatay! Hadda gal.', 'success')
        return redirect(url_for('login'))

    return render_template_string(HTML_LAYOUT, content=REGISTER_FORM)


if __name__ == '__main__':
    print(f"Xogta Register waxaa lagu keydinayaa: {reg_file_path}")
    print(f"Xogta Login waxaa lagu keydinayaa: {log_file_path}")
    app.run(debug=True)