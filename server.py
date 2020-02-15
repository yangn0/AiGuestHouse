from flask import Flask, request, jsonify
from flask import render_template
from flask import redirect, render_template, session
from functools import wraps
import json
import sql
import time
import os


# def time_data1(time_sj):  # 传入单个时间比如'2019-8-01'，类型为str
#     data_sj = time.strptime(time_sj, "%Y-%m-%d")  # 定义格式
#     time_int = int(time.mktime(data_sj))
#     return time_int  # 返回传入时间的时间戳，类型为int


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)   #设置一个随机24位字符串为加密盐

# 装饰器装饰多个视图函数
def wrapper(func):
    @wraps(func)  # 保存原来函数的所有属性,包括文件名
    def inner(*args, **kwargs):
        # 校验session
        if session.get("user"):
            ret = func(*args, **kwargs)  # func = home
            return ret
        else:
            return redirect("/login")
    return inner

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    admin=0
    print(request.form['username'])
    print(request.form['password'])
    if('check' in request.form):
        #管理员登录
        admin=1

    s = sql.Sql()
    r = s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'" %
                    request.form['username'])
    if(len(r)==0):
        return "用户名尚未注册"
    print(r[0].Upassword)
    if(r[0].Upassword == str(request.form['password'])):
        if(admin==1):
            if(r[0].Uper==0):
                session["user"] = request.form.get("username")
                return render_template('admin.html', user=request.form)
            else:
                return "无管理员权限"
        session["user"] = request.form.get("username")
        return render_template('roomsearch.html', user=request.form)
    else:
        return "密码错误"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    print(request.form['username'])
    print(request.form['password'])
    s = sql.Sql()
    r = s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'" %
                  request.form['username'])
    if(len(r) != 0):
        return '用户名已存在'
    # "用户名尚未注册"
    s.add('Userlogin', request.form['username'], request.form['password'], 1)
    return render_template('login.html')


@app.route('/roomsearch', methods=['POST'])
@wrapper
def roomsearch():
    s = sql.Sql()
    print(request.form['startdate'])
    print(request.form['enddate'])
    startdate = request.form['startdate']
    enddate = request.form['enddate']
    username=request.form['username']
    # startdate = time_data1(request.form['startdate'])
    # enddate = time_data1(request.form['enddate'])
    # print(startdate)
    # print(enddate)

    # 选择出不能租的客房
    r = s.execute("SELECT * FROM Checkin WHERE (Cstartdate BETWEEN '%s' AND '%s') AND (Clastdate BETWEEN '%s' AND '%s')" %
                  (startdate, enddate, startdate, enddate))
    cant_l = list()
    for i in r:
        cant_l.append(i.Croomnum)
    print(cant_l)
    if(len(cant_l) !=0):
        # 选择能出租的客房
        sql_str = "SELECT * FROM Room WHERE"
        for u, i in enumerate(cant_l):
            if(u == len(cant_l)-1):
                sql_str += (" id!=%s" % i)
            else:
                sql_str += (" id!=%s AND " % i)
    else:
        sql_str = "SELECT * FROM Room"
    n = s.execute(sql_str)
    print(n)
    roomlist = list()
    for r in n:
        room_num=r.Rroomnum
        roomid=r.id
        r=s.execute("SELECT * FROM Roomtype WHERE id=%s"%r.Rtypeid)
        print(r)
        r=r[0]
        type_str=r.Rtypename
        price=r.Rprice
        d=dict()
        d['id']=roomid
        d['roomnum']=room_num
        d['roomtype']=type_str
        d['price']=price
        d['startdate']=startdate
        d['enddate']=enddate
        d['username']=username
        roomlist.append(d)
    print(roomlist)
    return render_template('roomlist.html',indexs=roomlist)


@app.route('/roomlist', methods=['GET', 'POST'])
@wrapper
def roomlist():
    return render_template('roomlist.html')
    print(request.form['startdate'])
    print(request.form['enddate'])
    return 'ok'

@app.route('/orderlist', methods=['GET', 'POST'])
@wrapper
def orderlist():
    s = sql.Sql()
    username=request.args.get('userid')
    r=s.execute("SELECT * FROM Checkin WHERE Cuserid IN(SELECT id FROM Userlogin WHERE Uusername='%s')" % username)
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i.id
        d['roomnum']=(s.execute("SELECT * FROM Room WHERE id='%s'"% i.Croomnum) )[0].Rroomnum
        d['name']=(s.execute("SELECT * FROM Guest WHERE id='%s'"% i.Cguestid) )[0].Gname
        d['startdate']=i.Cstartdate
        d['enddate']=i.Clastdate
        orderlist.append(d)
    print(orderlist)
    return render_template('orderlist.html',indexs=orderlist)

@app.route('/orderconfirm', methods=['GET', 'POST'])
@wrapper
def orderconfirm():
    roomid=request.args.get('id')
    roomnum=request.args.get('roomnum')
    roomtype=request.args.get('roomtype')
    price=request.args.get('price')
    startdate=request.args.get('startdate')
    enddate=request.args.get('enddate')
    username=request.args.get('username')
    return render_template('orderconfirm.html',roomid=roomid,roomnum=roomnum,roomtype=roomtype,price=price,startdate=startdate,enddate=enddate,username=username)

@app.route('/order', methods=['POST'])
@wrapper
def order():
    s=sql.Sql()
    roomid=request.form['roomid']
    roomnum=request.form['roomnum']
    roomtype=request.form['roomtype']
    price=request.form['price']
    startdate=request.form['startdate']
    enddate=request.form['enddate']
    Gname=request.form['Gname']
    Gsex=request.form['Gsex']
    Gidcard=request.form['Gidcard']
    Gphone=request.form['Gphone']
    username=request.form['username']
    r=s.execute("SELECT * FROM Guest WHERE Gidcard='%s'"%Gidcard)
    print(r)
    if(len(r)==0):
        s.add('Guest',Gname,Gsex,Gidcard,Gphone,'',1,1,1)
    else:
        Cguestid=r[0].id
    r=s.execute("SELECT * FROM Guest WHERE Gidcard='%s'"%Gidcard)
    Cguestid=r[0].id                                                                #客户id
    print(r)

    r=s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'"%username)
    userid=r[0].id                                                                #userid
    print(r)

    s.add('Checkin',userid,roomid,Cguestid,startdate,enddate,'')
    return "预定成功"

@app.route('/admin/orderinfo', methods=['GET','POST'])
@wrapper
def orderinfo():
    s = sql.Sql()
    r=s.execute("SELECT * FROM Checkin")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i.id
        d['roomnum']=(s.execute("SELECT * FROM Room WHERE id='%s'"% i.Croomnum) )[0].Rroomnum
        d['name']=(s.execute("SELECT * FROM Guest WHERE id='%s'"% i.Cguestid) )[0].Gname
        d['startdate']=i.Cstartdate
        d['enddate']=i.Clastdate
        orderlist.append(d)
    return  render_template('orderinfo.html',indexs=orderlist)

@app.route('/admin/guestinfo', methods=['GET','POST'])
@wrapper
def guestinfo():
    s = sql.Sql()
    r=s.execute("SELECT * FROM Guest")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i.id
        d['name']=i.Gname
        d['sex']=i.Gsex
        d['idcard']=i.Gidcard
        d['phone']=i.Gphone
        d['bodybuild']=i.Gbodybuilding
        d['food']=i.Gfood
        d['vip']=i.Gvip
        orderlist.append(d)
    return  render_template('guestinfo.html',indexs=orderlist)
    
@app.route('/admin/roominfo', methods=['GET','POST'])
@wrapper
def roominfo():
    s = sql.Sql()
    r=s.execute("SELECT * FROM ROOM")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i.id
        d['roomnum']=i.Rroomnum
        d['typename']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i.Rtypeid)[0].Rtypename
        d['price']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i.Rtypeid)[0].Rprice
        orderlist.append(d)
    return  render_template('roominfo.html',indexs=orderlist)

@app.route('/admin/userinfo', methods=['GET','POST'])
@wrapper
def userinfo():
    s = sql.Sql()
    r=s.execute("SELECT * FROM Userlogin")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i.id
        d['username']=i.Uusername
        d['password']=i.Upassword
        d['per']=i.Uper
        orderlist.append(d)
    return  render_template('userinfo.html',indexs=orderlist)

@app.route('/orderdel', methods=['POST'])
@wrapper
def orderdel():
    s = sql.Sql()
    for i in request.form:
        r=s.no_ret_execute("DELETE FROM Checkin WHERE id='%s'"%i)
        print(i)
    return redirect('/admin/orderinfo')

@app.route('/userdel', methods=['POST'])
@wrapper
def guestdel():
    s = sql.Sql()
    for i in request.form:
        r=s.no_ret_execute("DELETE FROM Userlogin WHERE id='%s'"%i)
        print(i)
    return redirect('/admin/userinfo')


# def test():
#     request.form
#     request.json
#     return Response(json.dumps(result),  mimetype='application/json')
#     retrun jsonify(d)


if __name__ == '__main__':
    app.run(debug=True)
