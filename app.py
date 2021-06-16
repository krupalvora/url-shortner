from flask import Flask
from flask import Flask, render_template, request, flash, redirect, url_for
from flaskext.mysql import MySQL
from hashids import Hashids
app = Flask(__name__)

app.config['SECRET_KEY'] = 'dada bhagwan'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'kv462000'
app.config['MYSQL_DATABASE_DB'] = 'be'
app.config['MYSQL_DATABASE_HOST'] = 'database-1.cirddckxfqzh.us-east-2.rds.amazonaws.com'
mysql.init_app(app)
print('------------------------------------------------------------')

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = mysql.connect()
    cursor = conn.cursor()
    if request.method == 'POST':
        data=dict(request.form)
        url =data['url'] 
        custom=data['custom']
        data = cursor.execute('SELECT extend FROM urls WHERE extend = (%s)', (custom,))
        data = cursor.fetchone()
        print('*******************************************',data)
        try:
            if data[0]!='':
                flash('set other custom url !')
                return redirect(url_for('index'))
        except:
            pass
        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        url_id = cursor.execute('select id from urls ORDER BY id desc')
        url_id =cursor.fetchall()
        url_id=url_id[0]
        url_id=url_id[0]
        if custom=='':
            hashid = hashids.encode(url_id)
            short_url = request.host_url + hashid
        else:
            short_url = request.host_url + custom
            hashid=custom
        url_data = cursor.execute(
            'INSERT INTO urls (original_url,new_url,extend) VALUES (%s,%s,%s)', (url, short_url, hashid))
        
        conn.commit()
        conn.close()
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    original_id=id
    if original_id:
        data = cursor.execute('SELECT * FROM urls WHERE extend = (%s)', (original_id,))
        data = cursor.fetchone()
        id=data[0]
        original_url = data[2]
        click = data[3]
        new_url=data[4]
        extend=data[5]
        cursor.execute('UPDATE urls SET click = (%s) WHERE extend = (%s)',(click+1, original_id))
        cursor.execute(
            'INSERT INTO views (id,original_url,new_url,extend) VALUES (%s,%s,%s,%s)', (id,original_url,new_url, extend))
        
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
    urls = list(db_urls)
    urls=urls[1:]
    return render_template('stats.html', urls=urls)
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/delete/<string:id>',methods = ['POST', 'GET'])
def delete(id):
    id=int(id)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('delete from urls  where id= (%s)', (id,))    
    conn.commit()
    conn.close()
    return redirect(url_for('stats'))
if __name__ == '__main__':
    app.run(debug=True)
