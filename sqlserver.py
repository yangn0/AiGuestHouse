import pyodbc


class Sql:
	def __init__(self):
		self.db = pyodbc.connect(
		    DRIVER='{SQL Server}', SERVER='(local)', DATABASE='AiGuesthouse', UID='sa', PWD='sa')
		self.cursor = self.db.cursor()

	def __del__(self):
		if self.cursor:
			self.cursor.close()
			self.cursor = None
		if self.db:
			self.db.close()
			self.db = None

	def add(self,table,*args):
		value_str='('
		for i in args:
			value_str+="'%s',"% i
		value_str+=')'
		sql = "INSERT INTO %s VALUES%s"% (table,args)
		r=self.cursor.execute(sql)
		self.db.commit() #commit才生效,可以进行一堆骚操作之后再commit,节省时间
	
	def no_ret_execute(self,sql):
		self.cursor.execute(sql)
		self.db.commit()
		return 'del'

	def execute(self, sql):
		count = self.cursor.execute(sql).fetchall()
		self.db.commit()
		return count

		

if __name__ == "__main__":
	s=Sql()
	# r = s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'" %
    #               'zhangshiying')

	#s.add('Room','8414','1')
	#s.add('Roomtype','双人间','400')
	
	#r=s.execute("SELECT * FROM Userlogin WHERE Uusername='%s'"%'admin')
	
	#s.add('Checkin','1','1','1','2019-12-29','2020-01-08','无')
	#s.add('Room','8415','1')
	
	#s.add('Userlogin','guest1','123456','0',)
	#s.add('Guest','guest1','男','372929','15811421752','123','1','1','1')
	#s.execute("DELETE FROM Guest")
	
	input('over')