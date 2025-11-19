from flask import Flask, render_template, request
from flask import redirect, url_for
from webservice import get_api_data, extract_time_series, filter_data, plot_data
from datetime import datetime
import csv
import os
import sqlite3

# make a Flask application object called app
app = Flask(__name__)
#app.config["DEBUG"] = True
app.secret_key = 'your-secret-key'

# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn

# function to retrieve a post from the database
def get_post(post_id):
    conn = get_db_connection()
    # '*' means ALL
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        abort(404)
    
    return post


# use the app.route() decorator to create a Flask view function called index()

def index():
    
    # send the posts to the index.html template to be displayed
    return render_template('index.html', posts=posts)

# route to create a post
@app.route('/create/', methods=('GET', 'POST'))
def create():
    
    return render_template('create.html')

# create a route to edit a post. Load page with get or post method
# pass the post id as url parameter
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    # get the post from the database with a select query for the post with that id
    post = get_post(id)
    
    # determine if the page was requested with a GET or POST
    # if POST, process the form data. Get the data and validate it. Update the post and redirect to the homepage
    if request.method == 'POST':
        # get the title and content
        title = request.form['title']
        content = request.form['content']
        
        # if no title or content, flash an error message
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            # update the post
            conn = get_db_connection()
            
            conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?', (title, content, id))
            conn.commit()
            conn.close()
            
            # redirect to the homepage
            return redirect(url_for('index'))
    
        
    
    # if GET then display page
    return render_template('edit.html', post=post)

# create a route to delete a post
# Delete page will only be processed with a POST method
# the post id  is the url parameter
@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    # get the post from the database
    post = get_post(id)
    
    # connect to the database
    conn = get_db_connection()
    
    # execute a delete query
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    
    # commit and close the connection
    conn.commit()
    conn.close()
    
    # flash a success message
    flash('"{}" was successfully deleted!'.format(post['title']))
    
    # redirect to the homepage
    return redirect(url_for('index'))
    

##-----------------------------------------------

##-----------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('stocks'))

def load_stocks():
    stocks = []
    csv_path = os.path.join(os.path.dirname(__file__), "stocks.csv")
    with open("stocks.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stocks.append({
                "symbol": row["Symbol"],
                "name": row["Name"],
                "sector": row["Sector"]
            })
    return stocks

@app.route('/', methods=['GET', 'POST'])
@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    chart_file = None
    stock_list = load_stocks()
    
    if request.method == 'POST':
        symbol = request.form['symbol'].upper()
        function = request.form.get('function', 'TIME_SERIES_DAILY')
        chart_type = request.form.get('chart_type', 'line')
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        data = get_api_data(symbol, function)
        time_series = extract_time_series(data)
        
        if time_series:
            filtered = filter_data(time_series, start_date, end_date)
            chart_file = plot_data(filtered, symbol, chart_type)
    
    return render_template('stocks.html', stocks=stock_list, chart_file=chart_file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)