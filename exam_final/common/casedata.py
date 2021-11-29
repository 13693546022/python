import pandas
from common.log import log
def read_cases(xlsfile, prefixs, dict_indexs, columns=None, col_type=None): #读含多个参数列的用例的函数
    try:
        xlsfile='../excelcase/'+xlsfile
        data=pandas.read_excel(xlsfile, usecols=columns, dtype=col_type, keep_default_na=False)
        if type(prefixs) in(list,tuple) and type(dict_indexs) in(list,tuple):
            prefixs_and_indexs=zip(prefixs,dict_indexs)
        elif type(prefixs)==str and type(dict_indexs)==int:
            prefixs_and_indexs=((prefixs,dict_indexs),) #二维元组
        else:
            exit('prefixs的类型只能是列表或元组或字符串，dict_indexs的类型只能是列表或元组或整数')
        for prefix, dict_index in prefixs_and_indexs:
            cols=data.filter(regex='^'+prefix, axis=1) #过滤出前缀开头的列
            col_names=cols.columns.values #以前缀prefix开头的列名
            col_names_new=[i[len(prefix):] for i in col_names]#真正的参数名
            col_values=cols.values.tolist() #前缀开头的多行数据列表
            cols=[] #新的存字典的列表
            for value in col_values:
                col_dict=dict(zip(col_names_new, value))
                cols.append(col_dict)
            data.drop(col_names, axis=1, inplace=True)#drop删列存回data
            data.insert(dict_index, prefix, cols)
        cases=data.values.tolist()
        log().info(f'读测试用例文件{xlsfile}成功')
        return cases
    except BaseException as e:
        log().error(f'读测试用例文件{xlsfile}出错==错误类型：{type(e).__name__}，错误内容：{e}')
        exit()
def read_dict_cases(xlsfile,columns=None): #读带{:}参数的用例的函数
    data=pandas.read_excel(xlsfile, usecols=columns)
    cases=data.values.tolist()
    for case in cases:
        for i in range(len(case)):
            if str(case[i]).startswith('{') and str(case[i]).endswith('}') and ':' in str(case[i]):
                case[i]=eval(case[i])
    return cases
if __name__=='__main__':
    read_cases('login.xlsx','arg_',4,col_type={'arg_password':str})
    # read_cases('signup.xlsx', ['arg_','expect_'], [4,5], col_type={'arg_password': str,'arg_confirm':str})