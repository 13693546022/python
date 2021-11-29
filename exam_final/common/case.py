# -- coding: utf-8 --
import pandas
from common.log import log
# 读含多个参数列的用例
def read_case(xlsfile, prefixs, dict_indexs, columns=None, col_type=None): # 把多个列组装成字典
    xlsfile='../excelcase/'+xlsfile
    try:
        data=pandas.read_excel(xlsfile, usecols=columns, dtype=col_type, keep_default_na=False)
        if type(prefixs) in (list, tuple) and type(dict_indexs) in (list, tuple):
            prefixs_and_indexs = zip(prefixs, dict_indexs)
        elif type(prefixs) == str and type(dict_indexs) == int:
            prefixs_and_indexs = ((prefixs, dict_indexs),) # 二维元组
        else:
            exit('prefixs的类型只能是列表或元组或字符串，dict_indexs的类型只能是列表或元组或整数')
        for prefix, dict_index in prefixs_and_indexs:
            cols = data.filter(regex='^' + prefix, axis=1)  # 过滤出前缀开头的列
            col_names = cols.columns.values  # 以前缀prefix开头的列名
            col_names_new = [i[len(prefix):] for i in col_names]  # 真正的参数名
            col_values = cols.values.tolist()  # 前缀开头的多行数据列表
            cols = []  # 新的存字典的列表
            for value in col_values:
                col_dict = dict(zip(col_names_new, value))
                cols.append(col_dict)
            data.drop(col_names, axis=1, inplace=True)  # drop用于删除列，inplace表示数据保存到data
            data.insert(dict_index, prefix, cols)  # 把cols列表的每个元素作为一行插入到data的dict_index列，列名为prefix
        cases=data.values.tolist()
        log().info(f'读测试用例文件{xlsfile}成功')
        return cases
    except BaseException as e:
        log().error(f'读测试用例文件{xlsfile}出错==错误类型：{type(e).__name__}，错误内容：{e}')
# 读带{:}参数的用例
def read_dict_case(xlsfile,columns=None): # excel文件名，columns用于存储列名，处理好{:}的数据为字典，返回用例列表
    xlsfile='../excelcase/'+xlsfile
    try:
        data=pandas.read_excel(xlsfile, usecols=columns)
        cases=data.values.tolist()
        # print(cases)
        for case in cases:
            for i in range(len(case)):
                if str(case[i]).startswith('{') and str(case[i]).endswith('}') and ':' in str(case[i]):
                    case[i]=eval(case[i])
        log().info(f'读测试用例文件{xlsfile}成功')
        return cases
    except BaseException as e:
        log().error(f'读测试用例文件{xlsfile}出错==错误类型：{type(e).__name__}，错误内容：{e}')

if __name__=='__main__':
    # read_case('login.xlsx','arg_',4,col_type={'arg_password':str})
    read_case('signup.xlsx',['arg_','expect_'],[4,5],col_type={'arg_password':str,'arg_confirm':str})