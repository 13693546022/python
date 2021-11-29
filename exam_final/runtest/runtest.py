#最后执行测试
import pytest, sys
sys.path.append('..')
from common.log import log
# log().info('第五次执行测试。。。。。')
pytest.main(['--tb=short', '--html=../report/exam.html', '--self-contained-html','--log-format=%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(lineno)s]','--log-date-format=%Y-%m-%d %H:%M:%S','../testcase'])