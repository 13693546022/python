import pytest, sys
sys.path.append('..')
from common.conf import Conf
from common.db import DB
from common.case import read_case
from common.send import request,check
#测试固件
@pytest.fixture(autouse=True)
def get_host():
    global url_host
    a=Conf() #测试前，只获得一次host，存为全局变量
    url_host=a.host
@pytest.fixture() #注册接口测试函数之前执行，需要手动指定
def init_signup():
    a=DB()
    a.init_db('signup.sql')
cases=read_case('signup.xlsx',['arg_','expect_'],[4,5],col_type={'password':str, 'confirm':str})
# print(cases)
@pytest.mark.parametrize('case_id,case_name,api_path,method,args,expect,check_sql,db_expect_rows', cases)
def test_signup(init_signup,case_id,case_name,api_path,method,args,expect,check_sql,db_expect_rows): #测试注册接口的函数
    case_info=f'{case_id}:{case_name}'
    test_signup.__doc__=case_info
    url=url_host+api_path
    res_type, actual=request(method, url, args)
    res,msg=check(case_info, res_type, actual, expect)
    pytest.assume(res, msg)
    res,msg=DB().check_db(case_info, args, check_sql, db_expect_rows)
    assert res, msg
if __name__=='__main__':
    pytest.main(['--tb=short', '--html=../report/signup.html', '--self-contained-html','--log-format=%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(lineno)s]','--log-date-format=%Y-%m-%d %H:%M:%S','test_signup.py'])