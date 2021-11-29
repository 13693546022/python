import pytest, sys
sys.path.append('..')
from common.conf import Conf
from common.db import DB
from common.case import read_case
from common.send import request, check
#测试固件
@pytest.fixture(autouse=True)
def get_host():
    global url_host
    a=Conf() #测试前，只获得一次host，存为全局变量
    url_host=a.host
@pytest.fixture() #登录接口测试函数之前执行，需要手动指定
def init_login():
    a=DB()
    a.init_db('login.sql')
#pytest测试用例
cases=read_case('login.xlsx', 'arg_', 4)
@pytest.mark.parametrize('case_id,case_name,api_path,method,args,expect', cases)
def test_login(init_login,case_id,case_name,api_path,method,args,expect):
    case_info=f'{case_id}:{case_name}'
    test_login.__doc__=case_info
    # print(case_info)
    url=url_host+api_path
    res_type, actual=request(method, url, args)
    res,msg=check(case_info, res_type, actual, expect)
    # print(res)
    assert res, msg
if __name__=='__main__':
    pytest.main(['--tb=short', '--html=../report/login.html', '--self-contained-html','--log-format=%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(lineno)s]','--log-date-format=%Y-%m-%d %H:%M:%S','test_login.py'])