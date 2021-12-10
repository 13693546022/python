import configparser
from common.log import log

class Conf:
    def __init__(self):
        self.read_entry()
        self.read_server()
        self.read_db()
    def read_entry(self):
        try:
            conf=configparser.ConfigParser()
            conf.read('../conf/entry.ini')
            self.__which_server=conf.get('entry','which_server')
            self.__which_db=conf.get('entry','which_db')
            log().info(f'读取入口配置文件成功==接口服务器名：{self.__which_server}，数据库服务器名：{self.__which_db}')
        except BaseException as e:
            log().error(f'读取入口配置文件出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def read_server(self):
        try:
            conf=configparser.ConfigParser()
            conf.read('../conf/server.conf',encoding='utf-8')
            which_server=self.__which_server
            ip=conf.get(which_server,'ip')
            port=conf.get(which_server,'port')
            self.host=f'http://{ip}:{port}'
            log().info(f'读取接口服务器配置文件成功==接口服务器地址：{self.host}')
        except BaseException as e:
            log().error(f'读取接口服务器配置文件出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def read_db(self):
        try:
            conf=configparser.ConfigParser()
            conf.read('../conf/db.conf',encoding='utf-8')
            which_db=self.__which_db
            host=conf.get(which_db,'host')
            db=conf.get(which_db,'db')
            user=conf.get(which_db,'user')
            passwd=conf.get(which_db,'passwd')
            self.dbinfo={'host':host,'db':db,'user':user,'passwd':passwd}
            log().info(f'读取数据库服务器配置文件成功==数据库信息：{self.dbinfo}')
        except BaseException as e:
            log().error(f'读取数据库服务器配置文件出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def update_entry(self):
        try:
            is_update=input('是否输入入口名（y/n）：')
            while is_update not in {'y','Y','n','N'}:
                is_update=input('输入错误，请重新输入（y/n）:')
            if is_update in {'y','Y'}:
                new_server=input('请输入接口服务器入口名（debug、formal）：')
                new_db=input('请输入数据库服务器入口名（debug、formal）：')
                while {new_server, new_db}.issubset({'debug','formal'})==False:
                    new_server=input('服务器入口名输入错误，请重新输入接口服务器入口名（debug、formal）：')
                    new_db=input('服务器入口名输入错误，请重新输入数据库服务器入口名（debug、formal）：')
                if {new_server, new_db}.issubset({'debug', 'formal'}):
                    old_server, old_db = self.__which_server, self.__which_db
                    if new_server != old_server and new_db != old_db:
                        conf=configparser.ConfigParser()
                        conf.read('../conf/entry.ini')
                        conf.set('entry','which_server',new_server)
                        conf.set('entry','which_db',new_db)
                        file=open('../conf/entry.ini','w')
                        conf.write(file)
                        file.close()
                        log().info(f'成功将服务器入口名{old_server}，{old_db}修改未{new_server}，{new_db}')
                        self.__init__()
                    else:log().warning('服务器入口名未发生变更')
            else :
                log().warning('取消修改入口名')
        except BaseException as e:
            log().error(f'修改服务器入口名出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
if __name__ == '__main__':
    a=Conf()
    a.update_entry()