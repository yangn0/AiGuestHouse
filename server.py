from flask import Flask, request, jsonify
from flask import render_template
from flask import redirect, render_template, session
from functools import wraps
import json
import sql
import time
import os
import uuid
from face import main_video
import cv2


# def time_data1(time_sj):  # 传入单个时间比如'2019-8-01'，类型为str
#     data_sj = time.strptime(time_sj, "%Y-%m-%d")  # 定义格式
#     time_int = int(time.mktime(data_sj))
#     return time_int  # 返回传入时间的时间戳，类型为int


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yangning'   #设置一个随机24位字符串为加密盐
app.config.update(TEMPLATE_AUTO_RELOAD=True)

main_video.action()
main_video.init()

# 装饰器装饰多个视图函数
def wrapper(func):
    @wraps(func)  # 保存原来函数的所有属性,包括文件名
    def inner(*args, **kwargs):
        # 校验session
        if session.get("user"):
            r = func(*args, **kwargs)  # func = home
            return r
        else:
            return redirect("/login")
    return inner

@app.route('/')
def a():
    return redirect("/login")

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
    print(r[0]['Upassword'])
    if(r[0]['Upassword'] == str(request.form['password'])):
        if(admin==1):
            if(r[0]['Uper']==0):
                session["user"] = request.form
                return redirect('/index')
                #return render_template('admin.html', user=request.form)
            else:
                return "无管理员权限"
        session["user"] = request.form
        return redirect("/roomsearch")
    else:
        return "密码错误"

@app.route('/index',methods=['GET'])
@wrapper
def index():
    print(session["user"])
    #return render_template('admin.html')
    return redirect("/orderinfo")

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
    s.add('Userlogin',0, request.form['username'], request.form['password'], 1)
    return render_template('login.html')


@app.route('/roomsearch', methods=['GET','POST'])
@wrapper
def roomsearch():
    if request.method == "GET":
        return render_template('roomsearch.html',user=session['user'])
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
        cant_l.append(i['Croomnum'])
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
        room_num=r['Rroomnum']
        roomid=r['id']
        r=s.execute("SELECT * FROM Roomtype WHERE id=%s"%r['Rtypeid'])
        print(r)
        r=r[0]
        type_str=r['Rtypename']
        price=r['Rprice']
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
    #return jsonify(roomlist)
    return render_template('roomlist.html',indexs=roomlist)


@app.route('/roomlist', methods=['GET', 'POST'])
@wrapper
def roomlist():
    return render_template('roomlist.html')

@app.route('/orderlist', methods=['GET', 'POST'])
@wrapper
def orderlist():
    s = sql.Sql()
    username=request.args.get('userid')
    r=s.execute("SELECT * FROM Checkin WHERE Cuserid IN(SELECT id FROM Userlogin WHERE Uusername='%s')" % username)
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['roomnum']=(s.execute("SELECT * FROM Room WHERE id='%s'"% i['Croomnum']) )[0]['Rroomnum']
        d['name']=(s.execute("SELECT * FROM Guest WHERE id='%s'"% i['Cguestid']) )[0]['Gname']
        d['startdate']=i['Cstartdate']
        d['enddate']=i['Clastdate']
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
    Gface=request.files["Gface"]
    if Gface:
        filepath = "pic/%s.jpg" % uuid.uuid4()
        Gface.save(filepath)

    # 加载图片
    im=main_video.face_class.IM()
    im.filepath=filepath
    im=main_video.fun.LoadImg(im)
    ret=main_video.fun.RLSB(im)
    if ret[0]==-1:
        print('人脸识别失败:',ret)
    else:
        print('人脸识别成功:',ret)
    ft=main_video.fun.getsingleface(ret[1],0)
    tz1=main_video.fun.RLTZ(im.data,ft)[1]
    tzfilepath = 'tz/%s.dat' % uuid.uuid4()
    main_video.fun.writeFTFile(tz1,tzfilepath)


    r=s.execute("SELECT * FROM Guest WHERE Gidcard='%s'"%Gidcard)
    print(r)
    if(len(r)==0):
        s.add('Guest',0,Gname,Gsex,Gidcard,Gphone,tzfilepath,1,1,1)
    else:
        Cguestid=r[0]['id']
    r=s.execute("SELECT * FROM Guest WHERE Gidcard='%s'"%Gidcard)
    Cguestid=r[0]['id']                                                        #客户id
    print(r)

    r=s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'"%username)
    userid=r[0]['id']                                                                #userid
    print(r)

    s.add('Checkin',0,userid,roomid,Cguestid,startdate,enddate,'')
    return redirect("/roomsearch")

@app.route("/findface",methods=['POST'])
def findface():
    tz1=request.files["tz"]
    if tz1:
        filepath = "tz1/%s.dat" % uuid.uuid4()
        tz1.save(filepath)
    for i in os.walk('tz/'):
        for u in i[2]:
            tz1=main_video.fun.ftfromfile(filepath)
            tz=main_video.fun.ftfromfile(os.path.join('tz/',u))
            jg= main_video.fun.BD(tz1,tz)
            if(float(jg[1])>=0.9):
                s=sql.Sql()
                r=s.execute("SELECT * FROM Guest WHERE Gface='%s'"% ('tz/'+u))
                if(len(r)==0):
                    continue
                guestid=r[0]['id']
                r=s.execute("SELECT * FROM checkin WHERE cguestid='%s'"% guestid)
                if(len(r)==0):
                    continue
                print(r)
                return jsonify(r)
    return "error"

@app.route('/getusername', methods=['POST'])
@wrapper
def getusername():
    return session["user"]['username']

@app.route('/orderinfo', methods=['GET','POST'])
@wrapper
def orderinfo():
    if request.method=="GET":
        return render_template('orderinfo_temp.html')
    s = sql.Sql()
    r=s.execute("SELECT * FROM Checkin")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['roomnum']=(s.execute("SELECT * FROM Room WHERE id='%s'"% i['Croomnum']) )[0]['Rroomnum']
        d['name']=(s.execute("SELECT * FROM Guest WHERE id='%s'"% i['Croomnum']) )[0]['Gname']
        d['startdate']=i['Cstartdate']
        d['enddate']=i['Clastdate']
        orderlist.append(d)
    #return  render_template('orderinfo.html',indexs=orderlist)
    return jsonify(orderlist)

@app.route('/guestinfo', methods=['GET','POST'])
@wrapper
def guestinfo():
    if request.method=="GET":
        return render_template('guestinfo_temp.html')
    s = sql.Sql()
    r=s.execute("SELECT * FROM Guest")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['name']=i['Gname']
        d['sex']=i['Gsex']
        d['idcard']=i['Gidcard']
        d['phone']=i['Gphone']
        d['bodybuild']=i['Gbodybuilding']
        d['food']=i['Gfood']
        d['vip']=i['Gvip']
        orderlist.append(d)
    #return  render_template('guestinfo.html',indexs=orderlist)
    return jsonify(orderlist)
    
@app.route('/roominfo', methods=['GET','POST'])
@wrapper
def roominfo():
    if request.method=="GET":
        return render_template('roominfo_temp.html')
    s = sql.Sql()
    r=s.execute("SELECT * FROM ROOM")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['roomnum']=i['Rroomnum']
        d['typename']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i['Rtypeid'])[0]['Rtypename']
        d['price']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i['Rtypeid'])[0]['Rprice']
        orderlist.append(d)
    #return  render_template('roominfo.html',indexs=orderlist)
    return jsonify(orderlist)

@app.route('/roomtypeinfo', methods=['GET','POST'])
@wrapper
def roomtypeinfo():
    if request.method=="GET":
        return render_template('roomtypeinfo_temp.html')
    s = sql.Sql()
    r=s.execute("SELECT * FROM ROOMTYPE")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['typename']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i['id'])[0]['Rtypename']
        d['price']=s.execute("SELECT * FROM Roomtype WHERE id='%s'"%i['id'])[0]['Rprice']
        orderlist.append(d)
    #return  render_template('roominfo.html',indexs=orderlist)
    return jsonify(orderlist)

@app.route('/userinfo', methods=['GET','POST'])
@wrapper
def userinfo():
    if request.method=="GET":
        return render_template('userinfo_temp.html')
    s = sql.Sql()
    r=s.execute("SELECT * FROM Userlogin")
    orderlist=list()
    for i in r:
        d=dict()
        d['id']=i['id']
        d['username']=i['Uusername']
        d['password']=i['Upassword']
        d['per']=i['Uper']
        orderlist.append(d)
    #return  render_template('userinfo.html',indexs=orderlist)
    return jsonify(orderlist)

@app.route('/orderdel', methods=['POST'])
@wrapper
def orderdel():
    s = sql.Sql()
    for i in request.form:
        r=s.no_ret_execute("DELETE FROM Checkin WHERE id='%s'"%i)
        print(i)
    return 'ok'

@app.route('/useradd', methods=['GET','POST'])
@wrapper
def useradd():
    if request.method=="GET":
        return render_template('user-add.html')
    username=request.form['username']
    password=request.form['password']
    per=request.form['per']
    s = sql.Sql()
    s.add("Userlogin",0,username,password,per)
    return '添加成功'

@app.route('/roomadd', methods=['GET','POST'])
@wrapper
def roomadd():
    if request.method=="GET":
        return render_template('room-add.html')
    roomnum=request.form['roomnum']
    typeid=request.form['typeid']
    s = sql.Sql()
    s.add("Room",0,roomnum,typeid)
    return '添加成功'

@app.route('/getRoomtype', methods=['POST'])
@wrapper
def getRoomtype():
    s = sql.Sql()
    t=s.execute("SELECT * FROM Roomtype")
    l=list()
    for i in t:
        d=dict()
        d['id']=i['id']
        d['name']=i['Rtypename']
        l.append(d)
    return jsonify(l)

@app.route('/roomtypeadd', methods=['GET','POST'])
@wrapper
def roomtypeadd():
    if request.method=="GET":
        return render_template('roomtype-add.html')
    typename=request.form['typename']
    price=request.form['price']
    s = sql.Sql()
    s.add("Roomtype",0,typename,price)
    return '添加成功'

# @app.route('/userdel', methods=['POST'])
# @wrapper
# def guestdel():
#     s = sql.Sql()
#     for i in request.form:
#         r=s.no_ret_execute("DELETE FROM Userlogin WHERE id='%s'"%i)
#         print(i)
#     return 'ok'

# @app.route('/roomtypedel', methods=['POST'])
# @wrapper
# def roomtypedel():
#     s = sql.Sql()
#     for i in request.form:
#         r=s.no_ret_execute("DELETE FROM Userlogin WHERE id='%s'"%i)
#         print(i)
#     return 'ok'


# def test():
#     request.form
#     request.json
#     return Response(json.dumps(result),  mimetype='application/json')
#     retrun jsonify(d)


if __name__ == '__main__':
    app.run(debug=True)
