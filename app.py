import os
from flask import Flask ,jsonify
from flask import Flask, render_template, request, flash, redirect, url_for,session
import flask
from flaskext.mysql import MySQL
from hashids import Hashids
import json
import bson
import pymysql
import sys
from flask_session import Session

app = Flask(__name__)

app.config['SECRET_KEY'] = 'krupal'
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
    if not session.get("name"):
        return render_template('login.html')
    else:
        name=session.get("name")
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
        url_id = cursor.execute('select id from `%s` ORDER BY id desc',name)
        url_id =cursor.fetchall()
        url_id=url_id[0]
        url_id=url_id[0]
        if custom=='':
            hashid = hashids.encode(url_id)
            short_url = request.host_url + hashid
        else:
            short_url = request.host_url + custom
            hashid=custom
        url_data = cursor.execute('INSERT INTO `%s` (original_url,new_url,extend) VALUES (%s,%s,%s)', (name,url, short_url, hashid))
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
    if original_id=='favicon.ico':
        return flash(u'Invalid Url')
    print('**************automate exe***************************',original_id,'hmmmmmmmm')
    if original_id and original_id!='favicon.ico':
        if  session.get("name"):
            name=session.get("name")
            data = cursor.execute('SELECT * FROM `%s` WHERE extend = (%s)', (name,original_id,))
            data = cursor.fetchone()    
            id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
            cursor.execute('UPDATE `%s` SET click = (%s) WHERE extend = (%s)',(name,click+1,original_id))

        else:
            data = cursor.execute('SELECT * FROM urls WHERE extend = (%s)', (original_id,))
            data = cursor.fetchone()
            id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
            cursor.execute('UPDATE urls SET click = (%s) WHERE extend = (%s)',(click+1, original_id))
        
        print('**aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',id)
        conn.commit()
        conn.close()
        print('--------------if executed--------------------------')
        return render_template('details.html', url=original_url,id=id,new_url=new_url,extend=extend)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))
        
@app.route('/details/',methods = ['POST', 'GET'])
def details():
        print('2222222222222222222222222222222222222222222222')
        data=request.form['data']
        print(type(data))
        data=json.loads(data)
        print(data)
        print(data['os'],data['br'],data['id'],data['new_url'],data['original_url'],data['extend'])
        det=data['ct']
        print(det['country'],det['regionName'],det['city'],det['isp'])
        conn = mysql.connect()
        cursor = conn.cursor()
        if  session.get("name"):
            name=session.get("name")
            views=name+'views'
            print(views)
            cursor.execute('INSERT INTO `%s` (id,original_url,extend,new_url,country,state,city,service,os,browser) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (views,data['id'],data['original_url'],data['extend'],data['new_url'],det['country'],det['regionName'],det['city'],det['isp'],data['os'],data['br']))
            print('iiiiiiiiiiiiiiiiiiiiiiiiiinnnnnnnnnnnnnnnnnnnnnnnnnssssssssssssssssssseeeeeeeeeeeeeeeeeeerrrrrrrrrtttttttt')
        else:
            cursor.execute('INSERT INTO views (id,original_url,extend,new_url,country,state,city,service,os,browser) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (data['id'],data['original_url'],data['extend'],data['new_url'],det['country'],det['regionName'],det['city'],det['isp'],data['os'],data['br']))
        conn.commit()
        conn.close()
        return None
@app.route('/stats')
def stats():
    conn = mysql.connect()
    cursor = conn.cursor() 
    if  session.get("name"):
        name=session.get("name")
        db_urls = cursor.execute('SELECT * FROM `%s`',(name))
        db_urls=cursor.fetchall()
        conn.close()
        urls = list(db_urls)
        urls=urls[1:]
        return render_template('stats.html', urls=urls,name=name)
    else:
        db_urls = cursor.execute('SELECT * FROM urls')
        db_urls=cursor.fetchall()
        conn.close()
        urls = list(db_urls)
        urls=urls[1:]
        return render_template('stats.html', urls=urls)

@app.route('/about')
def about():
    if  session.get("name"):
        name=session.get("name")
        return render_template('about.html',name=name)
    else:
        return render_template('about.html')

@app.route('/delete/<string:id>',methods = ['POST', 'GET'])
def delete(id):
    if  session.get("name"):
        name=session.get("name")
        id=int(id)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('delete from `%s`  where id= (%s)', (name,id,))
        conn.commit()
        conn.close()
        return redirect(url_for('stats'))
    else:
        return redirect(url_for('login'))

@app.route('/edit/<string:id>',methods = ['POST', 'GET'])
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    id=int(id)
    if  session.get("name"):
        print('iiiiiiiiiiiiiiiiiiiiiiiiiiinnnnnnnnnnnnnnnnnnnnnnnniiiiiiiiiiiiiiiiiiiffffffffffffffff')
        name=session.get("name")
        views=name+'views'
        data=cursor.execute('select * from `%s`  where id= (%s)', (name,id,))  
        data=cursor.fetchone()
        id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
        print(data[0],data[2],data[3],data[4],data[5])
        data=cursor.execute('select date,count(date) noof from `%s` where id= %s group by date order by date',(views,id,))
        data=cursor.fetchall()
        data2=cursor.execute('select country,count(country) noof from `%s` where id= %s group by country order by country',(views,id,))
        data2=cursor.fetchall()
        data3=cursor.execute('select os,count(os) noof from `%s` where id= %s group by os order by os',(views,id,))
        data3=cursor.fetchall()
        data4=cursor.execute('select browser,count(browser) noof from `%s` where id= %s group by browser order by browser',(views,id,))
        data4=cursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('edit.html',data4=data4,data3=data3,data2=data2,data=data,id=id,original_url=original_url,new_url=new_url,click=click)

    else:
        data=cursor.execute('select * from urls  where id= (%s)', (id,))  
        data=cursor.fetchone()
        id,original_url,click,new_url,extend=data[0],data[2],data[3],data[4],data[5]
        print(data[0],data[2],data[3],data[4],data[5])
        data=cursor.execute('select date,count(date) noof from views where id= (%s) group by date order by date',(id,))
        data=cursor.fetchall()
        data2=cursor.execute('select country,count(country) noof from views where id= (%s) group by country order by country',(id,))
        data2=cursor.fetchall()
        data3=cursor.execute('select os,count(os) noof from views where id= (%s) group by os order by os',(id,))
        data3=cursor.fetchall()
        data4=cursor.execute('select browser,count(browser) noof from views where id= (%s) group by browser order by browser',(id,))
        data4=cursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('edit.html',data4=data4,data3=data3,data2=data2,data=data,id=id,original_url=original_url,new_url=new_url,click=click)
@app.route('/login', methods=["GET","POST"])
def login():
    if  session.get("name"):
        name=session.get("name")
        return render_template('login.html',name=name)
    elif request.method == "POST":
        req = request.form
        name = request.form["name"]
        password = request.form["password"]
        details=[name,password]
        conn = mysql.connect()
        cursor = conn.cursor()
        data=cursor.execute('select * from login where name=(%s) and password=(%s)',(name,password))
        data=cursor.fetchall()
        conn.commit()
        conn.close()
        try:
            if data[0][0]==name and data[0][1]==password:
                session["name"] = name
                return render_template('index.html',details=details)
        except:       
            flash(u'invalid Email or password ')
            
    return render_template('login.html')
@app.route('/signup', methods=["GET","POST"])
def signup():
    if request.method == "POST":
        req = request.form
        email = request.form["email"]
        name = request.form["name"]
        password = request.form["password"]
        views=name+'views'
        try :
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('insert into user(name,email,password) values (%s,%s,%s)',(name,email,password)) 
            cursor.execute('insert into login(name,password) values (%s,%s)',(name,password))
            cursor.execute(" CREATE TABLE `%s` (id int(11) NOT NULL AUTO_INCREMENT,created date NOT NULL DEFAULT current_timestamp(),original_url text  NOT NULL,click int(11) NOT NULL DEFAULT 0,new_url text DEFAULT NULL,extend text  DEFAULT NULL,PRIMARY KEY (id))",name)
            cursor.execute('CREATE TABLE `%s` ( `id` int(11) DEFAULT NULL,`date` date NOT NULL DEFAULT current_timestamp(),   `original_url` text COLLATE utf8mb4_unicode_ci NOT NULL,   `extend` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,   `new_url` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,`country` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,`state` text COLLATE utf8mb4_unicode_ci DEFAULT NULL ,`city` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,`service` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,`os` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,`browser` text COLLATE utf8mb4_unicode_ci DEFAULT NULL)',views)
            cursor.execute("insert into `%s`(id,original_url,new_url,extend) values (1,'null','null','null')",name)
            conn.commit()
            conn.close()
            session["name"] = name
            return render_template('index.html')#return redirect(url_for('index'))
        except pymysql.err.IntegrityError:
            flash(u'User name already in use')
    return render_template('signup.html')
@app.route("/logout", methods=["GET","POST"])
def logout():
    session["name"] = None
    return render_template('login.html')#redirect("index")
@app.route("/del_acc/<string:name>", methods=["GET","POST"])
def del_acc(name):
    name=session.get("name")
    views=name+'views'
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("drop table `%s`",name)
    cursor.execute("drop table `%s`",views)
    conn.commit()
    conn.close()
    session["name"] = None
    return render_template('signup.html')
#pymysql.err.IntegrityError: (1062, "Duplicate entry 'krupal.vora@sakec.ac.in' for key 'PRIMARY'")
if __name__ == '__main__':
    app.run(host='localhost',port=5000  ,debug=True)
