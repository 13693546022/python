import configparser
from common.log import log
class Conf: #配置文件类
    def __init__(self): #构造方法
        self.read_entry()
        self.read_server_conf()
        self.read_db_conf()
    def read_entry(self):  #读入口配置文件方法
        try:
            conf = configparser.ConfigParser()
            conf.read('../conf/entry.ini')
            self.__which_server = conf.get('entry', 'which_server')
            self.__which_db = conf.get('entry', 'which_db') #__表示禁止在类外使用__which_server和__which_db
            log().info(f'读入口配置文件../conf/entry.ini成功==接口服务器入口名：{self.__which_server}，数据库服务器入口名：{self.__which_db}')
        except BaseException as e:
            log().error(f'读入口配置文件../conf/entry.ini出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit() #退出python
    def read_server_conf(self):  #读接口服务器配置文件方法
        try:
            conf = configparser.ConfigParser()
            conf.read('../conf/server.conf', encoding='utf-8')
            which_server = self.__which_server
            ip = conf.get(which_server, 'ip')
            port = conf.get(which_server, 'port')
            self.host = 'http://%s:%s' % (ip, port) #接口地址url的一部分
            log().info(f'读接口服务器配置文件../conf/server.conf成功==接口服务器地址：{self.host}')
        except BaseException as e:
            log().error(f'读接口服务器配置文件../conf/server.conf出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def read_db_conf(self): #读数据库配置文件方法
        try:
            conf = configparser.ConfigParser()
            conf.read('../conf/db.conf')
            which_db = self.__which_db
            host = conf.get(which_db, 'host')
            db = conf.get(which_db, 'db')
            user = conf.get(which_db, 'user')
            passwd = conf.get(which_db, 'passwd')
            self.dbinfo = {'host': host, 'db': db, 'user': user, 'passwd': passwd}
            log().info(f'读数据库服务器配置文件../conf/db.conf成功==数据库信息：{self.dbinfo}')
        except BaseException as e:
            log().error(f'读数据库服务器配置文件../conf/db.conf出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def update_entry(self): #修改入口名方法
        try:
            is_update = input('是否修改入口名(y/Y表示是，其他表示否)：')
            if is_update in {'y', 'Y'}:
                new_server = input('新接口服务器入口名：')
                new_db = input('新数据库服务器入口名：')
                if {new_server, new_db}.issubset({'debug', 'formal', 'smoke', 'regress'}):
                    old_server, old_db = self.__which_server, self.__which_db
                    if new_server != old_server and new_db != old_db:
                        conf = configparser.ConfigParser()
                        conf.read('../conf/entry.ini')
                        conf.set('entry', 'which_server', new_server)
                        conf.set('entry', 'which_db', new_db)
                        file = open('../conf/entry.ini', 'w')  # w不能省略
                        conf.write(file)
                        file.close()
                        log().info('成功将入口名(%s,%s)修改为(%s,%s)' % (old_server, old_db, new_server, new_db))
                        self.__init__() #可以主动调用构造
                        # print(self.host,self.dbinfo) #调试
                    else:
                        log().info('入口名(%s,%s)未发生改变' % (old_server, old_db))
                else:
                    exit('入口名错误，只能输入debug、smoke、formal、regress之一') #exit也会抛出异常
            else:
                log().info('取消修改入口名')
        except BaseException as e:
            log().error(f'修改../conf/entry.ini出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
if __name__=='__main__':
    a=Conf()
    a.update_entry()