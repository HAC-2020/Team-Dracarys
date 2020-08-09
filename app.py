# Imports:
from flask import Flask, render_template, request, redirect, url_for, session,flash,make_response,session
import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import twilio
from twilio.rest import Client


# Configs:
app = Flask(__name__)

app.secret_key = 'secret'

app.config['MYSQL_HOST'] = os.environ.get("HOST","")
app.config['MYSQL_USER'] = os.environ.get("USER","")
app.config['MYSQL_PASSWORD'] = os.environ.get("PASSWORD","")
app.config['MYSQL_DB'] = os.environ.get("DB_NAME","")
mysql = MySQL(app)


app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY","")

# Routes:
@app.route('/customer/login', methods=['GET', 'POST'])
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s AND password = %s', (username, password,))
        customer = cursor.fetchone()
        if customer:
            session['loggedin'] = True
            session['id'] = customer['cus_id']
            session['username'] = customer['username']
            session['mobile'] = customer['mobileno']
            session['region'] = customer['region']
            return redirect(url_for('customer_display'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('cuslogin.html',msg=msg)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/shop/login', methods=['GET', 'POST'])
def login1():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shop WHERE username = %s AND password = %s', (username, password,))
        shop = cursor.fetchone()
        if shop:
            session['loggedin'] = True
            session['id'] = shop['shopid']
            session['username'] = shop['username']
            session['mobile'] = shop['mobile']
            session['region'] = shop['region']
            session['address'] = shop['address']
            session['shop_name'] = shop['shop_name']
            session['owner_name'] = shop['owner_name']
            return redirect(url_for('display'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('shoplogin.html',msg=msg)


@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET'])
def home():
    try:
        if request.method=='GET':
            return render_template('index.html')
    except Exception as e:
        print(e)


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('home'))



@app.route('/customer/register', methods=['GET', 'POST'])
def register():
    msg =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        region = request.form['region']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not mobile:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO customer VALUES (NULL, %s, %s, %s,%s,%s)', (username, password, email,mobile,region))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('cuslogin.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('cusregister.html',msg=msg)



@app.route('/shop/register', methods=['GET', 'POST'])
def register1():
    msg =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        ownername = request.form['ownername']
        shopname = request.form['shopname']
        mobile = request.form['mobile']
        address = request.form['address']
        region = request.form['region']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shop WHERE username = %s', (username,))
        shop = cursor.fetchone()
        if shop:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not mobile or not address or not ownername or not shopname:
            # print(1)
            msg = 'Please fill out the form!'
        else:
            # print(3)
            cursor.execute('INSERT INTO shop VALUES (NULL, %s, %s, %s,%s,%s,%s,%s)', (ownername,shopname,region,address,mobile,username, password))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('shoplogin.html')
    elif request.method == 'POST':
        # print(2)
        msg = 'Please fill out the form!'
    return render_template('shopregister.html',msg=msg)



@app.route('/dashboard', methods=['GET', 'POST'])
def display():
    msg=''
    now = datetime.datetime.now()
    shopid = session['id']
    eve = now.replace(hour=19, minute=0, second=0, microsecond=0)
    if now <= eve:
        date = datetime.date.today() + datetime.timedelta(days=1)
    else:
        date = datetime.date.today() + datetime.timedelta(days=2)
    if request.method == 'POST':
        start = request.form['start'][:2]
        end = request.form['end'][:2]
        shopid = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM slotbook WHERE date = %s and id_shop=%s', [date,shopid])
        boolean = cursor.fetchone()
        if boolean:
            msg = 'Slot has been already placed for'
            return render_template('shopdash.html',date=date,session=session,msg=msg,shopid=shopid)
        else:
            cursor.execute('INSERT INTO slotbook VALUES (%s, %s, %s,%s)', (shopid,date, start, end,))
            mysql.connection.commit()
            msg = 'Slot has been Successfully placed for'

    return render_template('shopdash.html',date=date,session=session,msg=msg,shopid=shopid)



@app.route('/customer/today',methods=['GET','POST'])
def today():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    today_date = datetime.date.today()
    cursor.execute('select distinct shop.shop_name,shop.owner_name,shop.address,shop.mobile,slotbook.id_shop from shop inner join slotbook on shop.shopid=slotbook.id_shop where slotbook.date=%s',[today_date,])
    shops_today = cursor.fetchall()
    # print(shops_today,len(shops_today))
    length  =len(shops_today)
    if shops_today:
        return render_template('today.html',shops=shops_today,l=length,date=today_date)
    else:
        return render_template('noshoptoday.html',shops=shops_today,l=length,date=today_date)



@app.route('/customer/tomorrow')
def tomorrow():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        tomorrow_date = date = datetime.date.today() + datetime.timedelta(days=1)
        cursor.execute('select distinct shop.shop_name,shop.owner_name,shop.address,shop.mobile,slotbook.id_shop from shop inner join slotbook on shop.shopid=slotbook.id_shop where slotbook.date=%s',[tomorrow_date,])
        shops_tomorrow = cursor.fetchall()
        # print(shops_tomorrow,len(shops_tomorrow))
        length = len(shops_tomorrow)
        if shops_tomorrow:
            response = make_response(render_template('tomorrow.html',shops=shops_tomorrow,l=length,date=tomorrow_date))
            return response
        else:
            return render_template('noshoptomorrow.html',shops=shops_tomorrow,l=length,date=tomorrow_date)



@app.route('/today/slots',methods=['GET','POST'])
def today_slot():
    today_date = datetime.date.today()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    shopid = request.form['shopid']
    cursor.execute('select start,end from slotbook where date=%s and id_shop=%s',[today_date,shopid])
    duration = cursor.fetchone()
    start = int(duration['start'])
    end=  int(duration['end'])
    cursor.execute('select slot_time from bookedslots where shop_id=%s and date=%s',[shopid,today_date])
    slots = cursor.fetchall()
    # print(slots)
    sl = len(slots)
    return render_template('slot.html',s=start,e=end,shopid=shopid,date=today_date,slots=slots)



@app.route('/tomorrow/slots',methods=['GET','POST'])
def tomorrow_slot():
    tomorrow_date = date = datetime.date.today() + datetime.timedelta(days=1)
    shopid = request.form['shopid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select start,end from slotbook where date=%s and id_shop=%s',[tomorrow_date,shopid])
    duration = cursor.fetchone()
    # print(duration)
    start = int(duration['start'])
    end=  int(duration['end'])
    cursor.execute('select slot_time from bookedslots where shop_id=%s and date=%s',[shopid,tomorrow_date])
    slots = cursor.fetchall()
    # print(slots)
    sl = len(slots)
    return render_template('slot.html',s=start,e=end,shopid=shopid,date=tomorrow_date,slots=slots)



@app.route('/booked/customer',methods=['GET','POST'])
def booked_slots():
    today_date = datetime.date.today()
    shopid = session['id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM bookedslots where date=%s and shop_id=%s order by cast(slot_time as unsigned);',[today_date,shopid])
    booked_slots = cursor.fetchall()
    length = len(booked_slots)
    # print(length)
    return render_template('shopview.html',booked=booked_slots,l=length,shop=shopid)



@app.route('/customer/dashboard',methods=['GET','POST'])
def customer_display():

    if request.method=='GET':
        now = datetime.datetime.now()
        date = datetime.date.today()
        # print(date)
        mobile = session['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM bookedslots where cus_mobile=%s order by date;',[mobile])
        booked_slots = cursor.fetchall()
        shopname=[]
        for k  in range(len(booked_slots)):
            cursor.execute('select shop_name from shop where shopid=%s',[booked_slots[k]['shop_id']])
            shop = cursor.fetchone()
            shopname.append(shop)
        length = len(booked_slots)
        return render_template('cusdash.html',date=date,session=session,booked=booked_slots,l=length,name=shopname)
    elif request.method=='POST':
        time = request.form['slotid']
        name = session['username']
        mobile = session['mobile']
        shopid = request.form['shopid']
        date = request.form['date']
        # print(date)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from bookedslots where cus_mobile=%s and date=%s',[mobile,date])
        exist = cursor.fetchone()
        if exist:
            msg='You have already booked a slot for ' + str(date)
            # print(msg)
        else:
            cursor.execute('insert into bookedslots VALUES (%s, %s, %s,%s,%s)',[name,mobile,time,date,shopid])
            mysql.connection.commit()
            account_sid = 'your_account_sid'
            auth_token = 'your_account_token'
            client = Client(account_sid, auth_token)
            body = 'Your slot has been successfully placed for '+date+' at '+time[:-3]+'.'
            message = client.messages.create(
                                        body=body,      
                                        from_='your_twilio_number',
                                        to='customer_mobile_number'
                                    )

            # print(message.sid)
            



@app.route('/shopkeeper/<int:shop_id>', methods=['POST', 'GET'])
def shopkeeper_inventory(shop_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	if request.method == 'POST':
		name = request.form['name']
		unit = request.form['unit']
		quantity = request.form['quantity']
		shop = shop_id
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM inventory WHERE name = %s AND shop_id = %s',(name,shop,))
		data = cursor.fetchone()
		if data:
			cursor.execute('UPDATE inventory SET QUANTITY = %s WHERE name = %s AND SHOP_ID = %s', (int(quantity) + data['quantity'] ,name,shop,))
		else:
			cursor.execute('INSERT INTO inventory VALUES (NULL, %s, %s, %s, %s)', (name,unit,quantity,shop,))
		mysql.connection.commit()
		cursor.close()
		return redirect('/shopkeeper/' + str(shop_id))
	else:
		cursor.execute('SELECT * FROM inventory WHERE shop_id = %s',(shop_id,))
		items = cursor.fetchall()
		cursor.close()
		return render_template('shopinv.html', data = items, shop=shop_id)



@app.route('/shopkeeper/<int:shop_id>/delete/<int:item_id>')
def remove_item(shop_id,item_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('DELETE FROM inventory WHERE id = %s',(item_id,))
	mysql.connection.commit()
	cursor.close()
	return redirect('/shopkeeper/' + str(shop_id))



@app.route('/shopkeeper/<int:shop_id>/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_qty(shop_id,item_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM inventory WHERE id = %s',(item_id,))
	item = cursor.fetchone()
	val = int(request.form['quantity'])
	if not(val < 0):
		cursor.execute('UPDATE inventory SET quantity = %s WHERE id = %s',(val,item_id,))
		mysql.connection.commit()
	cursor.close()
	return redirect('/shopkeeper/' + str(shop_id))



@app.route('/customer/<int:shop_id>')
def customer_inventory(shop_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM inventory WHERE shop_id = %s',(shop_id,))
	items = cursor.fetchall()
	cursor.close()
	return render_template('cusinv.html', data = items, shop = shop_id)


@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')



@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


port = int(os.getenv('PORT', 5001))

if __name__ == '__main__':
    app.run(host ='0.0.0.0', port = port, debug = True)
