import requests
from common.log import log
def send_request(method, url, args): #发送请求
    try:
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
        log().info(f'使用{method}方法将参数{args}发送给接口地址{url}成功')
        return res_type, actual
    except BaseException as e:
        log().error(f'使用{method}方法将参数{args}发送给接口地址{url}出错==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
#比对响应结果函数
def check(case_info, res_type, actual, expect):
    try:
        passed=False #预置变量，表示测试不通过
        if res_type=='text':
            if expect in actual:
                passed=True
        elif res_type=='json':
            if expect==actual:
                passed=True
        else: pass
        if passed:
            msg='' #测试通过时，断言失败消息为空
            log().info(f'{case_info}==比对响应结果通过')
        else:
            msg=f'{case_info}==比对响应结果失败==预期：{expect}==实际：{actual}' #给将来的assert断言使用的断言失败消息
            log().warning(msg)
        return passed, msg
    except BaseException as e:
        log().error(f'{case_info}==比对响应结果出错==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
if __name__=='__main__':
    # send_request('post','http://192.168.237.128/exam/login/',{'username':'admin','password':'123456'})
    # send_request('post', 'http://192.168.237.128/exam/signup/', {'username': 'admin', 'password': '123456','confirm':'123456','name':'管理员'})
    check('登录成功','text','登录成功','登录成功')
    check('登录成功', 'text', '登成功', '登录成功')
    check('登录成功', 'json', {'a':1}, {'a':1})
    check('登录成功', 'json', {'a':1}, {'a':2})