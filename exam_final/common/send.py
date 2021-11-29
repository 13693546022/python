# -- coding: utf-8 --
import requests
from common.log import log
# 发送请求
def request(method,url,args): # 方法、地址、参数：返回响应类型、实际结果
    try:
        send="requests.%s('%s',%s)"%(method, url, args)
        # print(send)
        res=eval(send)
        # print(res.headers['Content-Type']) # 响应类型
        if 'text' in res.headers['Content-Type']:
            res_type='text' # 响应类型
            actual=res.text # 实际结果
        elif 'json' in res.headers['Content-Type']:
            res_type='json'
            actual=res.json()
        else:
            pass
        log().info(f'使用{method}将参数{args}发送给接口地址{url}成功')
        return res_type, actual
    except BaseException as e:
        log().error(f'使用{method}将参数{args}发送给接口地址{url}错误==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
# 比对响应结果
def check(case_info,res_type, actual, expect):
    try:
        passed=False # 预制变量，表示测试不通过
        # print(type(actual), type(expect)) # 调试，检查实际和预期的class类型
        if res_type=='text':
            if expect in actual:
                passed=True
        elif res_type=='json':
            if expect==actual:
                passed=True
        else: pass
        if passed:
            msg='' # 测试通过时，断言失败消息为空
            log().info(f'{case_info}==比对响应结果通过')
        else:
            msg=f'{case_info}==比对响应结果失败==预期：{expect}==实际：{actual}' # 给将来的assert断言使用的断言失败消息
            log().warning(msg)
        return passed, msg
    except BaseException as e:
        log().error(f'{case_info}==比对响应结果错误==预期：{expect}==实际：{actual}==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
if __name__=='__main__':
    request('post','http://192.168.40.128/exam/login/',{'username':'admin','password':'123456'})
    check('登录成功','text','登录成功','登录成功')