/*
	客户信息表
*/
CREATE TABLE Guest
	(id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,     --客户ID
	Gname VARCHAR(20)NOT NULL,						--客户姓名
	Gsex VARCHAR(2)NOT NULL,						--性别
	Gidcard VARCHAR(30)NOT NULL,                    --证件号
	Gphone VARCHAR(20)NOT NULL,                     --电话
	Gface VARCHAR(20)NOT NULL,                      --人脸信息
	Gbodybuilding INT NOT NULL,						--健身房
	Gfood INT NOT NULL,								--餐厅
	Gvip INT NOT NULL								--VIP
	);

/*
	登录信息表
*/
CREATE TABLE Userlogin
	(id  INT NOT NULL IDENTITY(1,1) PRIMARY KEY,    --用户编号
	Uusername VARCHAR(20)NOT NULL,					--用户名
	Upassword VARCHAR(20)NOT NULL,					--密码
	Uper INT NOT NULL								--权限
	);

/*
	房间类型表
*/
CREATE TABLE Roomtype
	(id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,         --类型编号
	Rtypename VARCHAR(20)NOT NULL,						--类型名
	Rprice INT NOT NULL									--价格
	);
	
/*
	房间信息表
*/
CREATE TABLE Room
	(id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,				        --房间ID
	Rroomnum INT NOT NULL,											--房间号
	Rtypeid INT NOT NULL foreign key REFERENCES Roomtype(id)		--房间类型ID
	);

/*
	客户住房登记信息表
*/
CREATE TABLE Checkin
	(id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,				        --登记ID
	Cuserid INT NOT NULL foreign key REFERENCES Userlogin(id),		--账户id
	Croomnum INT NOT NULL foreign key REFERENCES Room(id),			--房间ID
	Cguestid INT NOT NULL foreign key REFERENCES Guest(id),			--客户ID
	Cstartdate DATE NOT NULL,										--预定入住日期
	Clastdate DATE NOT NULL,										--退房日期
	Cspe VARCHAR(50)												--备注
	);