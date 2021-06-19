from flask import Flask 
from flask import Flask, render_template, request, flash, redirect, url_for
from flaskext.mysql import MySQL
from hashids import Hashids
import json
import bson
import pymysql
app = Flask(__name__)

app.config['SECRET_KEY'] = 'krupal vora'
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'krupal'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'be'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
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
        url_data = cursor.execute('INSERT INTO urls (original_url,new_url,extend) VALUES (%s,%s,%s)', (url, short_url, hashid))
        conn.commit()
        conn.close()
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<id>',methods = ['POST', 'GET'])
def url_redirect(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    original_id=id
    print('**************automate exe***************************',original_id,'hmmmmmmmm')
    if original_id and original_id!='favicon.ico':
        data = cursor.execute('SELECT * FROM urls WHERE extend = (%s)', (original_id,))
        data = cursor.fetchone()
        id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
        cursor.execute('UPDATE urls SET click = (%s) WHERE extend = (%s)',(click+1, original_id))
        cursor.execute('INSERT INTO views (id,original_url,new_url,extend) VALUES (%s,%s,%s,%s)', (id,original_url,new_url, extend))
        conn.commit()
        conn.close()
        print('--------------if executed--------------------------')
        return render_template('details.html', url=original_url)#redirect(original_url)
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

@app.route('/edit/<string:id>',methods = ['POST', 'GET'])
def edit(id):
    id=int(id)
    conn = mysql.connect()
    cursor = conn.cursor()
    data=cursor.execute('select * from urls  where id= (%s)', (id,))  
    data=cursor.fetchone()
    id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
    print(data[0],data[2],data[3],data[4],data[5])
    data=cursor.execute('select date,count(date) noof from views where id= (%s) group by date order by date',(id,))
    data=cursor.fetchall()
    #data=json.dumps(data, indent=4, sort_keys=True, default=str)#json.loads(data)
    print('*******************************',data)
    conn.commit()
    conn.close()
    return render_template('edit.html',data=data,id=id,original_url=original_url,new_url=new_url,click=click)
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        req = request.form
        email = request.form["email"]
        password = request.form["password"]
        details=[email,password]
        
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++',details)
        conn = mysql.connect()
        cursor = conn.cursor()
        data=cursor.execute('select * from login where id=(%s) and password=(%s)',(email,password))
        data=cursor.fetchall()
        print(data)
        print(data[0])
        conn.commit()
        conn.close()
        if data[0][0]==email and data[0][1]==password:
            return render_template('index.html',details=details)
        else:       
            print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEExcept  ')
            flash(u'invalid Email or password ')
            
    return render_template('login.html')
@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == "POST":
        req = request.form
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        #email="`"+email+"`"
        print(email,str(email),']]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')
        email=str(email)
        try :
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('insert into user(id,name,password) values (%s,%s,%s)',(email,name,password)) 
            cursor.execute('insert into login(id,password) values (%s,%s)',(email,password))
            cursor.execute(" CREATE TABLE `%s` (id int(11) NOT NULL AUTO_INCREMENT,created date NOT NULL DEFAULT current_timestamp(),original_url text  NOT NULL,click int(11) NOT NULL DEFAULT 0,new_url text DEFAULT NULL,extend text  DEFAULT NULL,PRIMARY KEY (id))",email)
            conn.commit()
            conn.close()
        except pymysql.err.IntegrityError:
            print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEExcept  ')
            flash(u'Email already in use')
        
    return render_template('signup.html')

#pymysql.err.IntegrityError: (1062, "Duplicate entry 'krupal.vora@sakec.ac.in' for key 'PRIMARY'")
if __name__ == '__main__':
    app.run(host='localhost',port=8000  ,debug=True)
