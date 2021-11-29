#面向过程编程之线性编码方式（线性模型）
#导入模块
import configparser, pymysql, requests, pandas
#创建配置文件解析器对象
conf=configparser.ConfigParser()
#读入口名
conf.read('entry.ini',encoding='utf-8')
which_server=conf.get('entry', 'which_server')
which_db=conf.get('entry', 'which_db')
# print(which_server, which_db)
#修改入口名（可改、可不改）
is_update=input('是否修改入口名(Y/y)：')
if is_update in ('y','Y'):
    new_server, new_db=input('新接口服务器入口名：'), input('新数据库服务器入口名：')
    if {new_server, new_db}.issubset({'debug', 'smoke', 'formal', 'regress'}):
        if new_server!=which_server and new_db!=which_db:
            conf.set('entry','which_server',new_server)
            conf.set('entry', 'which_db',new_db)
            file=open('../接口高级-Day04-1/entry.ini', 'w', encoding='utf-8')
            conf.write(file)
            file.close()
            print('成功将入口名(%s,%s)修改为(%s,%s)'%(which_server,which_db,new_server,new_db))
            which_server,which_db=new_server,new_db
        else:
            print('入口名(%s,%s)未作修改'%(which_server,which_db))
    else:
        print('入口名必须在debug、smoke、formal、regress之中')
else:
    print('取消修改入口名')
#读接口服务器信息
conf.read('server.conf', encoding='utf-8') #读文件/存文件数据对象
ip=conf.get(which_server, 'ip')
port=conf.get(which_server,'port')
address='http://%s:%s'%(ip, port) #组装数据为需要的格式
print(address) #接口服务器信息
#读数据库服务器信息
conf.read('db.conf') #文件数据会存入conf中
host=conf.get(which_db,'host')
db=conf.get(which_db,'db')
user=conf.get(which_db,'user')
passwd=conf.get(which_db,'passwd')
dbinfo={'host':host, 'db':db, 'user':user, 'passwd':passwd}
print(dbinfo) #数据库服务器信息
#初始化数据库
# conn=pymysql.connect(host='192.168.16.128',db='exam',user='root',password='123456') #老写法
conn=pymysql.connect(**dbinfo) #新写法，**dbinfo变成关键字参数形式
cursor=conn.cursor()
sqls=open('../接口高级-Day04-1/exam.sql', 'r')
for sql in sqls:
    if sql.strip() and not sql.startswith('--'):
        cursor.execute(sql)
conn.commit()
conn.close()
#执行登录接口用例、比对响应结果
data=pandas.read_excel('login_xin.xlsx')
cases=data.values.tolist()
for case in cases:
    for i in range(len(case)): #用于将{:}字符串转为字典
        if str(case[i]).startswith('{') and str(case[i]).endswith('}') and ':' in str(case[i]):
            case[i]=eval(case[i])
    case_id,case_name,api_path,method,args,expect=case
    case_info=case_id+':'+case_name
    url=address+api_path
    res=eval("requests.%s('%s',%s)"%(method, url, args))
    actual=res.text
    if expect in actual:
        print(case_info+'==响应结果比对通过')
    else:
        print(case_info+'==响应结果比对失败==预期：%s==实际：%s'%(expect,actual))
#执行注册接口用例、比对响应结果、落库检查
data=pandas.read_excel('signup_xin.xlsx')
cases=data.values.tolist()
for case in cases:
    for i in range(len(case)):
        if str(case[i]).startswith('{') and str(case[i]).endswith('}') and ':' in str(case[i]):
            case[i]=eval(case[i])
    case_id,case_name,api_path,method,args,expect,check_sql,db_expect_rows=case
    case_info=case_id+':'+case_name
    url=address+api_path
    res=eval("requests.%s('%s',%s)"%(method, url, args))
    actual=res.json()
    if expect==actual:
        print(case_info+'==响应结果比对通过==',end='')
    else:
        print(case_info+'==响应结果比对失败==预期：%s==实际：%s=='%(expect, actual),end='')
    conn=pymysql.connect(**dbinfo)
    cursor=conn.cursor()
    cursor.execute(check_sql)
    row=cursor.fetchone()
    db_actual_rows=row[0]
    if db_actual_rows==db_expect_rows:
        print('落库检查通过')
    else:
        print('落库检查失败==要检查的数据：%s==预期行数：%s==实际行数：%s'%(args, db_expect_rows, db_actual_rows))