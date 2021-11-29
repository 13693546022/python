#先执行pytest.ini，再执行conftest.py
import pytest, platform, sys, requests, pymysql, pandas, pytest_html, os, time
from py.xml import html

# 测试报告名称
def pytest_html_report_title(report):
    report.title = "自定义接口测试报告名称"

# 日志文件名和Environment部分配置
def pytest_configure(config):
    now=time.strftime('%Y%m%d%H%M%S') #以日期时间做报告文件名
    config.option.log_file = os.path.join(config.rootdir, 'log', f'{now}.log') #日志放到项目目录下的log目录
    # 删除项
    #config._metadata.pop("JAVA_HOME")
    config._metadata.pop("Packages")
    config._metadata.pop("Platform")
    config._metadata.pop("Plugins")
    config._metadata.pop("Python")

    # 添加项
    config._metadata["平台"] = platform.platform()
    config._metadata["Python版本"] = platform.python_version()
    config._metadata["包"] = f'Requests({requests.__version__})，PyMySQL({pymysql.__version__})，Pandas({pandas.__version__})，Pytest({pytest.__version__})，Pytest-html({pytest_html.__version__})'
    config._metadata["项目名称"] = "自定义项目名称"
    # from common.entry import Conf
    # config._metadata["测试地址"] = Conf().read_server_conf()

# 在result表格中添加测试描述列
@pytest.mark.optionalhook
def pytest_html_results_table_header(cells): #添加列
    cells.insert(1, html.th('测试描述')) #第2列处添加一列，列名测试描述
    cells.pop()

# 修改result表格测试描述列的数据来源
@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells): #添加数据
    cells.insert(1, html.td(report.description)) #第2列的数据
    cells.pop()

# 修改result表格测试描述列的数据
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__) #函数注释文档字符串

# # 测试统计部分添加测试部门和人员
# @pytest.mark.optionalhook
# def pytest_html_results_summary(prefix):
#     prefix.extend([html.p("所属部门: 自动化测试部")])
#     prefix.extend([html.p("测试人员: ***")])

# 解决参数化时汉字不显示问题
def pytest_collection_modifyitems(items):
    #下面3行只能解决控制台中，参数化时汉字不显示问题
    # for item in items:
    #     item.name = item.name.encode('utf-8').decode('unicode-escape')
    #     item.nodeid = item.nodeid.encode('utf-8').decode('unicode-escape')
    #下面3行只能解决测试报告中，参数化时汉字不显示问题
    outcome = yield
    report = outcome.get_result()
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
