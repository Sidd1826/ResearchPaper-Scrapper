from flask import Flask, request, render_template, redirect, session, url_for, flash, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = 'secret_key'

# Flask MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hello'
mysql = MySQL(app)

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
print("Current working directory is:", os.getcwd())


def delete_previous_csv():
    if os.path.exists("paper.csv"):
        os.remove("paper.csv")
        print("Previous CSV file deleted.")


# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
#         email = request.form['email']
#         password = request.form['password']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM register WHERE email = %s AND password = %s', (email, password,))
#         user = cursor.fetchone()
#         if user:
#             session['loggedin'] = True
#             # session['userid'] = user['userid']
#             session['name'] = user['name']
#             session['email'] = user['email']
#             flash('Logged in successfully!')
#             return redirect(url_for('index'))
#         else:
#             flash('Please enter correct email/password!')
#             return render_template('login.html')


# @app.route('/',  methods=['GET', 'POST'])
# def home():
#     if 'loggedin' in session:
#         return render_template('index.html', name=session['name'])
#     return redirect(url_for('login'))
# @app.before_first_request
# def redirect_to_login():
#     return redirect(url_for('login'))
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM register WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['name'] = user['name']
            session['email'] = user['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password!', 'error')

    # Render the login template for GET requests and invalid credentials
    return render_template('login.html')


@app.route('/logout')
def logout():
    # session.pop('loggedin', None)
    # session.pop('id', None)
    # session.pop('name', None)
    # session.pop('email', None)
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('userid', None)
#     session.pop('email', None)
#     return redirect(url_for('login'))

# @app.route("/cart")
# def cart():
#   # Render the cart.html template
#   return render_template("cart.html")

# @app.route("/cart", methods=['GET', 'POST'])
# def add_to_cart():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute(
#         "INSERT INTO cart (title, author) VALUES ( %s, %s)",
#         (title, author)
#     )
#     mysql.connection.commit()
#     cursor.close()
#     mysql.connection.close()

#     # Get the paper information from the POST request
#     paper_id = request.form["paper_id"]
#     title = request.form["title"]
#     author = request.form["author"]

#     # Add the paper to the cart in the session
#     if "cart" not in session:
#         session["cart"] = []
#     session["cart"].append(
#         {"paper_id": paper_id, "title": title, "author": author})
    

#     print(session["cart"])
#     print("____________")
#     print(paper_id)

#     # Redirect the user to the cart page
#     # return redirect(url_for("cart"))
#     return render_template('cart.html')

def create_table(name):
    # Get the session name for the current user
    table_name = f"{name}_table"
    
    # Create a new table for the current user
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(f"CREATE TABLE {table_name} (sr_no INT NOT NULL PRIMARY KEY AUTO_INCREMENT , title VARCHAR(500), author VARCHAR(500), url VARCHAR(500))")
    cursor.execute(f"CREATE TABLE {table_name} (sr_no INT NOT NULL PRIMARY KEY AUTO_INCREMENT , title VARCHAR(500), author VARCHAR(500), url VARCHAR(500))")

    
    return f"Table {table_name} created successfully!"

# def create_history_table(name):
#     # Get the session name for the current user
#     table_name = f"{name}_history"
    
#     # Create a new table for the current user
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute(f"CREATE TABLE {table_name} (sr_no INT(255) AUTO_INCREMENT, search_query VARCHAR(500), author VARCHAR(500), url VARCHAR(500), PRIMARY KEY(sr_no))")

#     return f"Table {table_name} created successfully!"

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    user_id = session['name']
    table_name = f"{user_id}_table"

    cur = mysql.connection.cursor()
    hello = f"SELECT * FROM {table_name} WHERE title LIKE '%{query}%'"
    cur.execute(hello)
    data = cur.fetchall()
    cur.close()

    return render_template('search.html', data=data, query=query)

@app.route('/download_csv')
def download_csv():
    title = request.args.get('title')
    author = request.args.get('author')
    url = request.args.get('url')
    
    csv_data = f"Title,Author,URL\n{title},{author},{url}"
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=data.csv"}
    )



@app.route('/display')
def display():
    user_id = session['name']
    table_name = f"{user_id}_table"

    cur = mysql.connection.cursor()
    query = f"SELECT * FROM {table_name}"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return render_template('display.html', data=data)
                  

@app.route("/cart", methods=['GET', 'POST'])
def add_to_cart():
    # Get the paper information from the POST request
    paper_id = request.form["paper_id"]
    title = request.form["title"]
    author = request.form["author"]
    url=request.form["url of paper"]

    user_id = session['name']
    table_name = f"{user_id}_table"

    # Add the paper to the cart in the session
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(
        {"paper_id": paper_id, "title": title, "author": author, "url":url})

    # Insert the paper into the database
    cursor = mysql.connection.cursor()
    query = f"INSERT INTO {table_name} (title, author, url) VALUES (%s, %s, %s)"
    cursor.execute(query, (title, author, url))
    mysql.connection.commit()
    cursor.close()
   
    return render_template('cart.html')


# def validate_user(name):
#     cursor = mysql.connection.cursor()
#     query = f"SELECT COUNT(*) FROM register WHERE name='{name}'"
#     cursor.execute(query)
#     result = cursor.fetchone()

#     if result[0] > 0:
#         return False
#     else:
#         return True


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'name' in request.form and 'phone' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # if not validate_user(name):
        #     flash("Username already taken")
        #     return redirect(url_for('register'))
        # else:
        cursor.execute('INSERT INTO register (name, phone, email, password) VALUES (%s, %s, %s, %s)',
                        (name, phone, email, password,))
        mysql.connection.commit()
        create_table(name)
        flash('You have successfully registered!')
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'name' in session:
        print('Hello world')
        if request.method == 'POST':
            research_paper = request.form['research_paper'].replace(" ", "+")

            # Delete previous CSV file if it exists
            delete_previous_csv()

            paper_names = []
            authors_list = []
            # cite_count = []
            links = []

            for i in range(10):
                start = i * 10
                url = f'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={research_paper}&btnG=&oq=&start={start}'
                response = requests.get(url, headers=headers)
                print(response.status_code)
                page_contents = response.text
                length = len(page_contents)
                print(length)
                doc = BeautifulSoup(page_contents, 'html.parser')
                print(type(doc))
                paper_names_tag = doc.select('[data-lid]')
                for tag in paper_names_tag:
                    paper_names.append(tag.select('h3')[0].get_text())
                # citations = doc.select('a.gs_or_cit')
                # print(citations)
                # for i in citations:
                #     try:
                #         cite = i.text
                #         cite_count.append(int(re.search(r'\d+', cite).group()))
                #     except AttributeError:
                #         cite_count.append(0)

                link_tag = doc.find_all('h3', {"class": "gs_rt"})
                for i in range(len(link_tag)):
                    link_element = link_tag[i].find('a')
                    link = link_element.get('href') if link_element else ''
                    links.append(link)

                author_tag = doc.select('div.gs_a')
                for tag in author_tag:
                    authors_list.append(tag.get_text())

            # papers_dict = {'paper title': paper_names, 'authors': authors_list,
            #                'citation': cite_count, 'url of paper': links}
            papers_dict = {'paper title': paper_names, 'authors': authors_list, 'url of paper': links}
            print(json.dumps(papers_dict, indent=4))

            # Create dataframe and save to csv file
            papers_df = pd.DataFrame(papers_dict)
            # print(papers_df)
            papers_df.to_csv('./paper.csv', index=False)
            print("CSV file saved successfully.")

            return render_template('index.html', papers=papers_dict)

        return render_template('index.html', papers=None)
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
