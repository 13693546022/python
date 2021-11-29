#面向对象编程
import configparser, pymysql, requests, pandas, os
class Conf: #配置文件类，向类外提供数据：接口地址一部分url，提供数据库信息dbinfo，类外没必要使用which_server和which_db（所以封装起来）
    def __init__(self): #构造方法
        self.read_entry()
        self.read_server_conf()
        self.read_db_conf()
    def read_entry(self):  #读入口配置文件方法
        conf = configparser.ConfigParser()
        conf.read('entry.ini')
        self.__which_server = conf.get('entry', 'which_server')
        self.__which_db = conf.get('entry', 'which_db') #__表示禁止在类外使用__which_server和__which_db
    def read_server_conf(self):  #读接口服务器配置文件方法
        conf = configparser.ConfigParser()
        conf.read('server.conf', encoding='utf-8')
        which_server = self.__which_server
        ip = conf.get(which_server, 'ip')
        port = conf.get(which_server, 'port')
        self.host = 'http://%s:%s' % (ip, port) #接口地址url的一部分
    def read_db_conf(self): #读数据库配置文件方法
        conf = configparser.ConfigParser()
        conf.read('db.conf')
        which_db = self.__which_db
        host = conf.get(which_db, 'host')
        db = conf.get(which_db, 'db')
        user = conf.get(which_db, 'user')
        passwd = conf.get(which_db, 'passwd')
        self.dbinfo = {'host': host, 'db': db, 'user': user, 'passwd': passwd}
    def update_entry(self): #修改入口名方法
        is_update = input('是否修改入口名(y/Y表示是，其他表示否)：')
        if is_update in {'y', 'Y'}:
            new_server = input('新接口服务器入口名：')
            new_db = input('新数据库服务器入口名：')
            if {new_server, new_db}.issubset({'debug', 'formal', 'smoke', 'regress'}):
                old_server, old_db = self.__which_server, self.__which_db
                if new_server != old_server and new_db != old_db:
                    conf = configparser.ConfigParser()
                    conf.read('entry.ini')
                    conf.set('entry', 'which_server', new_server)
                    conf.set('entry', 'which_db', new_db)
                    file = open('entry.ini', 'w')  # w不能省略
                    conf.write(file)
                    file.close()
                    print('成功将入口名(%s,%s)修改为(%s,%s)' % (old_server, old_db, new_server, new_db))
                    self.__init__() #可以主动调用构造
                    # print(self.host,self.dbinfo) #调试
                else:
                    print('入口名(%s,%s)未发生改变' % (old_server, old_db))
            else:
                print('入口名错误，只能输入debug、smoke、formal、regress之一')
        else:
            print('取消修改入口名')
class DB:
    def __init__(self): #构造方法：连接数据库
        dbinfo = Conf().dbinfo
        self.__conn = pymysql.connect(**dbinfo) #私有成员变量
        self.__cursor = self.__conn.cursor()
    def read_sqls(self, *sqlfiles): #读sql语句文件方法
        if not sqlfiles:  # 表示sqlfiles为空
            sqlfiles = [i for i in os.listdir() if i.endswith('.sql')]
        # print(sqlfiles) #调试
        sqls = []  # 存sql语句的列表
        for file in sqlfiles:  # file为文件名
            data = open(file, 'r')  # data表示文件中所有行
            for sql in data:  # sql是一行
                if sql.strip() and not sql.startswith('--'):
                    sqls.append(sql.strip())
        return sqls
    def init_db(self, *sqlfiles): #初始化数据库方法
        conn, cursor = self.__conn, self.__cursor
        sqls = self.read_sqls(*sqlfiles)
        for sql in sqls:
            cursor.execute(sql)
        conn.commit()
        conn.close()
    def check_db(self,case_info, args, check_sql, db_expect_rows): #验库方法
        conn, cursor = self.__conn,self.__cursor
        cursor.execute(check_sql)
        db_actual_rows = cursor.fetchone()[0]
        if db_actual_rows == db_expect_rows:
            print(case_info + '==落库检查通过')
        else:
            print(case_info + '==落库检查失败==检查的数据：%s==预期行数：%s==实际行数：%s' % (args, db_expect_rows, db_actual_rows))
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
    DB().init_db(sqlfile)
    cases=read_cases(xlsfile, prefixs, dict_indexs, columns)
    for case in cases:
        if not is_checkdb:
            case_id,case_name,api_path,method,args,expect=case
        else:
            case_id,case_name,api_path,method,args, expect,check_sql,db_expect_rows = case
        case_info=case_id+':'+case_name
        url = Conf().host + api_path
        res_type, actual = send_request(method, url, args)
        check(case_info, res_type, actual, expect)
        if is_checkdb:
            DB().check_db(case_info, args, check_sql, db_expect_rows)
#测试登录接口的函数
def test_login():
    run_test('login.sql', 'login.xlsx', 'arg_', 4, False)
#测试注册接口的函数
def test_signup():
    run_test('signup.sql','signup.xlsx', ['arg_','expect_'], [4, 5], True)
if __name__ == '__main__':
    # a=Conf()
    # # a.read_entry()
    # # print(a.__which_server, a.__which_db) #错，因为封装了
    # # print(a.host, a.dbinfo)
    # a.update_entry()
    # a=DB()
    # print(a.read_sqls())
    # print(a.read_sqls('login.sql'))
    # print(a.read_sqls('login.sql', 'signup.sql'))
    # a.init_db()
    # a.init_db('login.sql')
    # a.check_db('检查总行数',{'a':2},'select count(*) from user',5)
    test_login()
    test_signup()