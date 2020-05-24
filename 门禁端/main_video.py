import face_dll,face_class
from ctypes import *
import cv2 as cv
import face_function as fun
import threading
import time,os
from pynput import keyboard
import pymysql
import requests
import uuid
import json

Appkey=b'Cr1CUs7iKkuG6wg6186jLLXZudnqKk7UvaW5f71KuYgH'
SDKey=b'3D9qMCzCH5UN8cF3gKtAKgt5nJbKsJ4JRqD1qRbJVctg'

ip=''
roomnum=''

# def insert_sql(name,Phone_number,Department,Project_group,addr):
#     db = pymysql.connect(host='localhost', user='root', password='88888888', port=3306, db='faces')
#     cursor = db.cursor()
#     sql = 'INSERT INTO faces_2 (id, name, Phone_number,Department,Project_group,addr) values(%s,%s,%s,%s,%s,%s)'
#     sq_num='SELECT COUNT(*) FROM faces_2'
#     cursor.execute(sq_num)
#     num = cursor.fetchone()
#     #print(num[0])
#     try:
#         cursor.execute(sql, (str(num[0]+1), name,Phone_number,Department,Project_group,addr+str(num[0]+1)+".dat"))
#         db.commit()
#     except:
#         db.rollback()
#     db.close()
#     return num[0]+1

# def read_sql():
#     db = pymysql.connect(host='localhost', user='root', password='88888888', port=3306, db='faces')
#     cursor = db.cursor()
#     sql='SELECT * FROM faces_2'
#     cursor.execute(sql)
#     while(1):
#         row=cursor.fetchone()
#         yield row
    
def action():
    # 激活
    ret=fun.JH(Appkey,SDKey)
    if ret==0 or ret==90114:
        print('激活成功:',ret)
    else:
        print('激活失败:',ret)
        pass
def init():
    # 初始化
    ret=fun.CSH()
    if ret[0]==0:
        print('初始化成功:',ret,'句柄',fun.Handle)
    else:
        print('初始化失败:',ret)
def input_pic():
    # 加载图片
    im=face_class.IM()
    im.filepath='3.jpg'
    im=fun.LoadImg(im)
    print(im.filepath,im.width,im.height)
    # cv2.imshow('im',im.data)
    # cv2.waitKey(0)
    print('加载图片完成:',im)
    return im

def reg_face(im,ret):
    ft=fun.getsingleface(ret[1],0)
    tz1=fun.RLTZ(im,ft)[1]
    #print("人脸特征提取成功。")
    print("-----------------------------------------------")
    return tz1

def save_face(tz1):
    s=input("姓名：")
    Phone_number=input("电话：")
    Department=input("部门:")
    Project_group=input("项目组：")
    n=insert_sql(s,Phone_number,Department,Project_group,'tz/')
    fun.writeFTFile(tz1,'tz/%s.dat' % n)
    #print("人脸特征保存成功。")
    print("-----------------------------------------------")

def find_face_old(tz1):
    for i in os.walk('tz/'):
        for u in i[2]:
            tz=fun.ftfromfile(os.path.join('tz/',u))
            jg= fun.BD(tz1,tz)
            if(float(jg[1])>=0.9):
                print(u.split('.')[0],jg[1])
                print("-----------------------------------------------")

def find_face(tz1):
    tzfilepath = 'tz/%s.dat' % uuid.uuid4()
    fun.writeFTFile(tz1,tzfilepath)
    r=requests.post(ip+'/findface',files = {'tz': open(tzfilepath,'rb')})
    return r.text


#print(jg[1])
#rint(jg)

#ret=fun.RLSB(im)
'''if ret[0]==-1:
    print('人脸识别失败:',ret)
    pass
else:
    print('人脸识别成功:',ret)
ret=ret[1]
# 显示人脸照片 ret.faceOrient.contents.value ret.faceRect.contents
fun.showimg(im,ret)'''
#提取单人1特征
#ft=fun.getsingleface(ret[1],0)
#tz1=fun.RLTZ(im,ft)[1]
#提取单人2特征
#ft=fun.getsingleface(ret[1],1)
#tz2=fun.RLTZ(im,ft)[1]
#特征保存到文件
# fun.writeFTFile(tz1,'d:/1.dat')
# fun.writeFTFile(tz2,'d:/2.dat')
#文件获取特征
#tz=fun.ftfromfile('d:/1.dat')
#jg=fun.BD(tz1,tz)
#print(jg[1])
#结果比对
# jg=fun.BD(tz1,tz2)
# print(jg[1])
def thread1():
    global frame
    global real
    global ret
    global ip
    global roomnum
    ip=input("输入服务端ip：")
    roomnum=input("输入本房间房间号：")
    while(1):
        ret1,real=cap.read()
        frame=real
        try:
            frame=fun.draw_div(frame,ret[1])
        except:
            pass
        cv.imshow('test',frame)
        if cv.waitKey(1)&0xFF == ord('q'):
            break
            
def thread2():
    global frame
    global ret
    while(1):
        try:
            ret=fun.VF(frame)
            print(ret[1].faceRect[i])
        except:
            pass
        
def thread3():
    global frame
    global ret
    global roomnum

    # def on_press(key):
    #     if(str(key)=='Key.f9'):
    #         print("提取人脸特征，并在人脸库比对……")
    #         tz_now=reg_face(frame,ret)
    #         r=find_face(tz_now)
    #         if r =='error':
    #             print("未找到此人脸订单信息。")
    #         else:
    #             for i in json.loads(r):
    #                 if str(i['Croomnum'])==roomnum :
    #                     Cstartdate=time.mktime(time.strptime(i['Cstartdate'],"%a, %d %b %Y %H:%M:%S %Z")) # 字符串转时间戳
    #                     Clastdate=time.mktime(time.strptime(i['Clastdate'],"%a, %d %b %Y %H:%M:%S %Z")) # 字符串转时间戳
    #                     if(Cstartdate>time.time()):
    #                         print("未到订单开始时间")
    #                     elif(Clastdate<time.time()):
    #                         print("本房间时间已结束")
    #                     else:
    #                         print("-------开锁-------")
    #                 else:
    #                     print("非本房间。")
            
    #     # if(str(key)=='Key.f10'):
    #     #     print("保存人脸特征……")
    #     #     save_face(reg_face(frame,ret))
            
    # with keyboard.Listener(on_press=on_press) as listener:
    #     listener.join()

    while(1):
        try:
            tz_now=reg_face(frame,ret)
        except:
            continue
        r=find_face(tz_now)
        if r =='error':
            print("未找到此人脸订单信息。")
        else:
            for i in json.loads(r):
                if str(i['Croomnum'])==roomnum :
                    Cstartdate=time.mktime(time.strptime(i['Cstartdate'],"%a, %d %b %Y %H:%M:%S %Z")) # 字符串转时间戳
                    Clastdate=time.mktime(time.strptime(i['Clastdate'],"%a, %d %b %Y %H:%M:%S %Z")) # 字符串转时间戳
                    if(Cstartdate>time.time()):
                        print("未到订单开始时间")
                    elif(Clastdate<time.time()):
                        print("本房间时间已结束")
                    else:
                        print("-------开锁-------")
                else:
                    print("非本房间。")
        
if __name__ == "__main__":
    action()
    init()
    lock=threading.Lock()
    cap=cv.VideoCapture(0) # 0 为摄像头
    t1 = threading.Thread(target=thread1)
    t1.setDaemon(True)
    t1.start()
    t2=threading.Thread(target=thread2)
    t2.start()
    t3=threading.Thread(target=thread3)
    t3.start()
    
