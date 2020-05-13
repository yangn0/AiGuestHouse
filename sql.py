import pymysql

# /*
# 	客户信息表
# */
Guest = '''
CREATE TABLE IF NOT EXISTS Guest
	(id INT NOT NULL auto_increment PRIMARY KEY,     
	Gname VARCHAR(20) NOT NULL,						
	Gsex VARCHAR(2) NOT NULL,						
	Gidcard VARCHAR(30) NOT NULL,                    
	Gphone VARCHAR(20) NOT NULL,                     
	Gface VARCHAR(255) NOT NULL,                      
	Gbodybuilding INT NOT NULL,						
	Gfood INT NOT NULL,								
	Gvip INT NOT NULL								
	);
'''

# /*
# 	登录信息表
# */
Userlogin = '''
CREATE TABLE IF NOT EXISTS Userlogin
	(id  INT NOT NULL auto_increment PRIMARY KEY,   
	Uusername VARCHAR(20)NOT NULL,					
	Upassword VARCHAR(20)NOT NULL,					
	Uper INT NOT NULL								
	);
'''

# /*
# 	房间类型表
# */
Roomtype = '''
CREATE TABLE IF NOT EXISTS Roomtype
	(id INT NOT NULL auto_increment PRIMARY KEY,         
	Rtypename VARCHAR(20)NOT NULL,						
	Rprice INT NOT NULL									
	);
'''

# /*
# 	房间信息表
# */
Room = '''
CREATE TABLE IF NOT EXISTS Room
	(id INT NOT NULL auto_increment PRIMARY KEY,				       
	Rroomnum INT NOT NULL,											
	Rtypeid INT NOT NULL		
	);
'''

# /*
# 	客户住房登记信息表
# */
Checkin = '''
CREATE TABLE IF NOT EXISTS Checkin
	(id INT NOT NULL auto_increment PRIMARY KEY,				       
	Cuserid INT NOT NULL,		
	Croomnum INT NOT NULL,			
	Cguestid INT NOT NULL,			
	Cstartdate DATE NOT NULL,										
	Clastdate DATE NOT NULL,										
	Cspe VARCHAR(50)												
	);
'''


class Sql:
    def __init__(self):
        self.db = pymysql.connect(host='localhost',  # 指定连接本地服务器
                                  user='root',    # 登录服务器 用的用户名
                                  password='yangning',  # 登录服务器用的密码
                                  database='AiGuesthouse',    # 指定目标数据库
                                  charset='utf8')
        # 规定返回的值为字典类型，否则默认返回元组类型
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        # 关闭数据库连接
        self.db.close()

    def add(self, table, *args):
        # value_str = '('
        # for i in args:
        #     value_str += "'%s'," % i
        # value_str += ')'
        sql = "INSERT INTO %s VALUES%s" % (table, args)
        self.cursor.execute(sql)
        self.db.commit()  # commit才生效,可以进行一堆骚操作之后再commit,节省时间

    def no_ret_execute(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        return 'success'

    def execute(self, sql):
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            return results
        except Exception as err:
            self.db.rollback()
            raise err

    def sqlstr(self, sql_str):
        try:
            # 执行sql语句
            self.cursor.execute(sql_str)
            # 提交到数据库执行
            self.db.commit()
        except Exception as err:
            # 如果发生错误则回滚
            self.db.rollback()
            raise err

    def init_table(self):
        try:
            # 执行sql语句
            self.cursor.execute(Guest)
            self.cursor.execute(Userlogin)
            self.cursor.execute(Roomtype)
            self.cursor.execute(Room)
            self.cursor.execute(Checkin)

            # 提交到数据库执行
            self.db.commit()
        except Exception as err:
            # 如果发生错误则回滚
            self.db.rollback()
            raise err


if __name__ == "__main__":
    '''
    # 建库
    '''
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            passwd='yangning',
        )
        cur = conn.cursor()
        create_database_sql = 'CREATE DATABASE IF NOT EXISTS AiGuesthouse DEFAULT CHARSET utf8 COLLATE utf8_general_ci;'
        cur.execute(create_database_sql)
        cur.close()
        print('创建数据库成功！')
    except pymysql.Error as e:
        print('pymysql.Error: ', e.args[0], e.args[1])

    s=Sql()
    s.init_table()
    s.sqlstr("INSERT INTO userlogin VALUES (1,'admin','123456','1')")
    print("建表成功！")
