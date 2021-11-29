import logging #1、导入模块logging
def log():
    logger=logging.getLogger() #2、创建（获得）日志对象（只创建一次对象）
    return logger
#调试：输出日志
if __name__=='__main__':
    log().info('成功的消息')
    log().warning('警告信息')
    log().error('错误信息')