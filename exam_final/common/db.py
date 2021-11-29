import os, pymysql
from common.conf import Conf
from common.log import log
def read_sqls(*sqlfiles):  # 读sql语句文件方法
    try:
        if not sqlfiles:  # 表示sqlfiles为空
            sqlfiles = tuple([i for i in os.listdir('../initsqls') if i.endswith('.sql')]) #不要直接写()，否则结果是对象
        # print(sqlfiles) #调试
        sqls = []  # 存sql语句的列表
        for file in sqlfiles:  # file为文件名
            data = open('../initsqls/'+file, 'r')  # data表示文件中所有行
            for sql in data:  # sql是一行
                if sql.strip() and not sql.startswith('--'):
                    sqls.append(sql.strip())
        log().info(f'读sql语句文件{sqlfiles}成功')
        return sqls
    except BaseException as e:
        log().error(f'读sql语句文件{sqlfiles}出错==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
class DB:
    def __init__(self): #构造方法：连接数据库
        dbinfo = Conf().dbinfo
        try:
            self.__conn = pymysql.connect(**dbinfo) #私有成员变量
            self.__cursor = self.__conn.cursor()
            log().info(f'连接数据库{dbinfo}成功')
        except BaseException as e:
            log().error(f'连接数据库{dbinfo}出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def init_db(self, *sqlfiles): #初始化数据库方法
        conn, cursor = self.__conn, self.__cursor
        sqls = read_sqls(*sqlfiles)
        try:
            for sql in sqls:
                cursor.execute(sql)
            conn.commit()
            conn.close()
            log().info('执行造数代码，初始化数据库成功')
        except BaseException as e:
            log().error(f'执行造数代码，初始化数据库出错==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
    def check_db(self,case_info, args, check_sql, db_expect_rows): #验库方法
        conn, cursor = self.__conn,self.__cursor
        try:
            cursor.execute(check_sql)
            db_actual_rows = cursor.fetchone()[0]
            if db_actual_rows == db_expect_rows:
                log().info(f'{case_info}==落库检查通过')
                return True, '' #测试通过时，没有断言失败消息
            else:
                msg=f'{case_info}==落库检查失败==检查的数据：{args}==预期行数：{db_expect_rows}==实际行数：{db_actual_rows}'
                log().warning(msg)
                return False, msg
        except BaseException as e:
            log().error(f'{case_info}==落库检查出错==检查的数据：{args}==预期行数：{db_expect_rows}==错误类型：{type(e).__name__}，错误内容：{e}')
            exit()
if __name__=='__main__':
    # read_sqls()
    # read_sqls('login.sql')
    # read_sqls('log.sql')
    a=DB()
    # a.init_db()
    # a.init_db('login.sql')
    # a.init_db('login.sql', 'signup.sql')
    a.check_db('总行数',{'a':23},'select count(*) from user',6)
    # q=tuple(i*i for i in range(10)) #可以用元组推导式
    # print(q)