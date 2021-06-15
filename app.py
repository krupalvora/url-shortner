from flask import Flask
from flask import Flask, render_template, request, flash, redirect, url_for
from flaskext.mysql import MySQL
from hashids import Hashids
app = Flask(__name__)

app.config['SECRET_KEY'] = 'dada bhagwan'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'krupal'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'be'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
print('------------------------------------------------------------')
""" conn = mysql.connect()
cursor = conn.cursor()
data = cursor.execute('SELECT * FROM urls ')
data = cursor.fetchall()
print(data)
conn.commit()
conn.close() """


@app.route('/', methods=('GET', 'POST'))
def index():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        url = request.form['url']
        print(url)
        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        url_id = cursor.execute('select id from urls ORDER BY id desc')
        url_id =cursor.fetchall()
        url_id=url_id[0]
        url_id=url_id[0]
        print('?????????????????????',url_id)
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid
        url_data = cursor.execute(
            'INSERT INTO urls (original_url,new_url,extend) VALUES (%s,%s,%s)', (url, short_url, hashid))
        conn.commit()
        conn.close()
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')


@app.route('/<id>')
def url_redirect(id):
    print(id)
    conn = mysql.connect()
    cursor = conn.cursor()
    original_id = hashids.decode(id)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', original_id)
    if original_id:
        original_id = original_id[0]+1
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', original_id)
        data = cursor.execute(
            'SELECT * FROM urls WHERE id = (%s)', (original_id))
        data = cursor.fetchone()
        original_url = data[2]
        click = data[3]
        cursor.execute('UPDATE urls SET click = (%s) WHERE id = (%s)',(click+1, original_id))
        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/stats')
def stats():
    conn = mysql.connect()
    cursor = conn.cursor() 
    db_urls = cursor.execute('SELECT * FROM urls')
    db_urls=cursor.fetchall()
    conn.close()
    print('+++++++++++++++++++++++++++++++++++++++++++++',db_urls)
    urls = list(db_urls)
    """ for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url) """
    print('+++++++++++++++++++++++++++++++++++++++++++++',urls)
    return render_template('stats.html', urls=urls)
@app.route('/about')
def about():
    return render_template('about.html')
if __name__ == '__main__':
    app.run(debug=True)
