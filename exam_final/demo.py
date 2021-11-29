# -- coding: utf-8 --
# __doc__
def f(i,s,l):
    """i必须是int型，s必须是str型，l必须是list型"""
    if type(i)==int:print("int")
    else:print("ERROR")
    if type(s)==str:print("str")
    else:print("ERROR")
    if type(l)==list:print("list")
    else:print("ERROR")
f(10,"10",[10])
f(10,10,10)
help(f)
# print(f)
a=f.__doc__
print(a)
