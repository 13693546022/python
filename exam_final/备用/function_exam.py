#面向过程编程之函数模型
import configparser, pymysql, requests, pandas, os
#读入口配置文件函数
def read_entry(): #无参，返回本次测试用的接口服务器和数据库的入口名
    conf=configparser.ConfigParser()
    conf.read('entry.ini')
    which_server=conf.get('entry', 'which_server')
    which_db=conf.get('entry', 'which_db')
    return which_server, which_db
#读接口服务器配置文件函数
def read_server_conf(): #无参，返回http://IP:端口号
    conf=configparser.ConfigParser()
    conf.read('server.conf', encoding='utf-8')
    which_server=read_entry()[0]
    ip=conf.get(which_server, 'ip')
    port=conf.get(which_server, 'port')
    host='http://%s:%s'%(ip,port)
    return host
#读数据库配置文件函数
def read_db_conf(): #无参，返回数据库信息字典
    conf=configparser.ConfigParser()
    conf.read('db.conf')
    which_db=read_entry()[1]
    host=conf.get(which_db, 'host')
    db=conf.get(which_db, 'db')
    user=conf.get(which_db, 'user')
    passwd=conf.get(which_db, 'passwd')
    dbinfo={'host':host,'db':db,'user':user,'passwd':passwd}
    return dbinfo
#修改入口名函数
def update_entry(): #无参，无返回值
    is_update=input('是否修改入口名(y/Y表示是，其他表示否)：')
    if is_update in{'y','Y'}:
        new_server=input('新接口服务器入口名：')
        new_db=input('新数据库服务器入口名：')
        if {new_server,new_db}.issubset({'debug','formal','smoke','regress'}):
            old_server,old_db=read_entry()
            if new_server!=old_server and new_db!=old_db:
                conf=configparser.ConfigParser()
                conf.read('entry.ini')
                conf.set('entry', 'which_server', new_server)
                conf.set('entry', 'which_db', new_db)
                file=open('entry.ini', 'w') #w不能省略
                conf.write(file)
                file.close()
                print('成功将入口名(%s,%s)修改为(%s,%s)'%(old_server,old_db,new_server,new_db))
            else:
                print('入口名(%s,%s)未发生改变'%(old_server,old_db))
        else:
            print('入口名错误，只能输入debug、smoke、formal、regress之一')
    else:
        print('取消修改入口名')
#连接数据库函数
def conn_db(): #无参，返回数据库连接对象、游标
    dbinfo=read_db_conf()
    conn=pymysql.connect(**dbinfo)
    cursor=conn.cursor()
    return conn,cursor
#读sql语句文件的函数
def read_sqls(*sqlfiles): #有参（0、1、多个），返回sql语句列表，sqlsfiles=(('login.sql'))，sqlsfiles=('login.sql')
    if not sqlfiles: #表示sqlfiles为空
        sqlfiles=[i for i in os.listdir() if i.endswith('.sql')]
    # print(sqlfiles) #调试
    sqls=[] #存sql语句的列表
    for file in sqlfiles: #file为文件名
        data=open(file,'r') #data表示文件中所有行
        for sql in data: #sql是一行
            if sql.strip() and not sql.startswith('--'):
                sqls.append(sql.strip())
    return sqls
#初始化数据库函数
def init_db(*sqlfiles): #有参（用于传给read_sqls），无返回值，sqlfiles=('login.sql')
    conn,cursor=conn_db()
    # sqls=read_sqls(sqlfiles) #不能省略*，read_sqls(('login.sql'))
    sqls=read_sqls(*sqlfiles) #read_sqls('login.sql')
    # print(sqls) #调试
    for sql in sqls:
        cursor.execute(sql)
    conn.commit()
    conn.close()
#验库函数
def check_db(case_info,args,check_sql,db_expect_rows): #用例信息，检查的数据/参数、执行检查的sql语句、数据库预期行数
    conn,cursor=conn_db()
    cursor.execute(check_sql)
    db_actual_rows=cursor.fetchone()[0]
    if db_actual_rows==db_expect_rows:
        print(case_info+'==落库检查通过')
    else:
        print(case_info+'==落库检查失败==检查的数据：%s==预期行数：%s==实际行数：%s'%(args,db_expect_rows,db_actual_rows))
#读含多个参数列的用例的函数（原来的cols_to_dict函数）
def read_cases(xlsfile, prefixs, dict_indexs, columns=None, col_type=None): #把多个列组装成字典
    data=pandas.read_excel(xlsfile, usecols=columns, dtype=col_type, keep_default_na=False)
    if type(prefixs) in(list,tuple) and type(dict_indexs) in(list,tuple):
        prefixs_and_indexs=zip(prefixs,dict_indexs)
    elif type(prefixs)==str and type(dict_indexs)==int:
        prefixs_and_indexs=((prefixs,dict_indexs),) #二维元组
    else:
        print('prefixs的类型只能是列表或元组或字符串，dict_indexs的类型只能是列表或元组或整数')
        return [] #返回空列表
    for prefix, dict_index in prefixs_and_indexs:
        cols=data.filter(regex='^'+prefix, axis=1) #过滤出前缀开头的列
        col_names=cols.columns.values #以前缀prefix开头的列名
        col_names_new=[i[len(prefix):] for i in col_names]#真正的参数名
        col_values=cols.values.tolist() #前缀开头的多行数据列表
        cols=[] #新的存字典的列表
        for value in col_values:
            col_dict=dict(zip(col_names_new, value))
            cols.append(col_dict)
        data.drop(col_names, axis=1, inplace=True)#drop删列存回data
        data.insert(dict_index, prefix, cols) #把cols列表的每个元素作为一行插入到data的dict_index列，列名为prefix
    cases=data.values.tolist()
    return cases
#读带{:}参数的用例的函数
def read_dict_cases(xlsfile,columns=None): #参数：1个excel文件名，columns用于存储列名，处理好{:}的数据为字典，返回用例列表
    data=pandas.read_excel(xlsfile, usecols=columns)
    cases=data.values.tolist()
    for case in cases:
        for i in range(len(case)):
            if str(case[i]).startswith('{') and str(case[i]).endswith('}') and ':' in str(case[i]):
                case[i]=eval(case[i])
    return cases
#发送请求
def send_request(method, url, args): #方法、地址、参数；返回返回值类型、实际结果
    send="requests.%s('%s',%s)"%(method, url, args)
    # print(send) #调试
    res=eval(send)
    # print(res.headers['Content-Type']) #响应/返回值类型
    if 'text' in res.headers['Content-Type']:
        res_type='text' #返回值类型
        actual=res.text #实际结果，类型：text/html; charset=gbk
    elif 'json' in res.headers['Content-Type']:
        res_type='json'
        actual=res.json() #实际结果，类型：application/json;charset=utf8
    else:
        pass
    return res_type, actual
#比对响应结果函数
def check(case_info, res_type, actual, expect):
    passed=False #预置变量，表示测试不通过
    if res_type=='text' and expect in actual:
        passed=True
    elif res_type=='json' and expect==actual:
        passed=True
    else: pass
    if passed:
        print(case_info + '==比对响应结果通过')
    else:
        print(case_info + '==比对响应结果失败==预期：%s==实际：%s' % (expect, actual))
#运行测试的函数
def run_test(sqlfile, xlsfile, prefixs, dict_indexs, is_checkdb, columns=None):
    init_db(sqlfile)
    cases=read_cases(xlsfile, prefixs, dict_indexs, columns)
    for case in cases:
        if not is_checkdb:
            case_id,case_name,api_path,method,args,expect=case
        else:
            case_id,case_name,api_path,method,args, expect,check_sql,db_expect_rows = case
        case_info=case_id+':'+case_name
        url = read_server_conf() + api_path
        res_type, actual = send_request(method, url, args)
        check(case_info, res_type, actual, expect)
        if is_checkdb:
            check_db(case_info, args, check_sql, db_expect_rows)
#测试登录接口的函数
def test_login():
    run_test('login.sql', 'login_xin.xlsx', 'arg_', 4, False)
#测试注册接口的函数
def test_signup():
    run_test('signup.sql','signup_xin.xlsx', ['arg_','expect_'], [4, 5], True)
if __name__=='__main__':
    # print(read_entry())
    # print(read_server_conf())
    # print(read_db_conf())
    # update_entry()
    # conn,cursor=conn_db()
    # print(os.listdir())
    # sqlfiles=[i for i in os.listdir() if i.endswith('.sql')]
    # print(sqlfiles)
    # print(read_sqls())
    # print(read_sqls('login.sql'))
    # print(read_sqls('login.sql','signup.sql'))
    # init_db()
    # init_db('login.sql')
    # init_db('login.sql', 'signup.sql')
    # check_db('用例信息',{'a':2,'b':3}, 'select count(*) from user',4)
    # print(read_cases('login_xin.xlsx','arg_',4,col_type={'arg_password':str}))
    # print(read_cases('signup_xin.xlsx',['arg_','expect_'],[4,5],col_type={'arg_password':str,'arg_confirm':str}))
    # print(send_request('post','http://192.168.150.213/exam/login/',{'username':'admin','password':'123456'}))
    # print(send_request('post', 'http://192.168.150.213/exam/signup/', {'username': 'admin', 'password': '123456','confirm':'123456','name':'管理员'}))
    # check('用例信息', 'text', '登录成功了', '登录成功')
    # check('用例信息', 'text', '登路成功了', '登录成功')
    # check('用例信息', 'json', {'a':1,'b':2}, {'b':2,'a':1})
    # check('用例信息', 'json', {'a':1},{'a':1,'b':2})
    # test_login()
    test_signup()