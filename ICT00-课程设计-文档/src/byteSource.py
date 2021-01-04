__author__ = "Chen, Huiyu"
__email__ = "chy126101@gmail.com"
__version__ = "20201231.2334"

# 引入相关库
from numpy import random, searchsorted, zeros
from csv import reader
from sys import argv

def ganExtend(P0):
    '''获得八次扩展

    Args:
        P0 (float): 数据比特概率分布
    Returns:
        Ext (list): 字节概率分布
    '''
    Ext = []
    for i in range(256):
        a = bin(i).count('1')
        Ext.append(P0 ** (8 - a) * (1 - P0) ** a)
    return Ext

def handleFileData(inputFileName):
    '''打开CSV文件(.csv)，处理数据

    读入用户输入的CSV文件的数据，将数据按列逐个写入一个列表中并返回

    Args:
        inputFileName (str): CSV文件路径
    Returns:
        data (list): CSV文件中，指定字节符号的概率分布
    '''
    with open(inputFileName, encoding='utf-8') as f:

        # 从csv文件中读取的每一行都作为字符串列表返回
        myReader = reader(f)

        # 将reader中第1列（列数从0开始）写入列表data
        data = []
        for row in myReader:
            data.append(float(row[1]))

    return data


def getInfoSouece(symbol_prob, msgLength):
    '''生成指定大小的概率分布的数据

    通过读入指定概率分布以及信息源长度，通过蒙特卡罗法，
    生成符合输入条件的数据的数组返回

    Args:
        symbol_prob (array): 指定字节符号的概率分布
        msgLength (int): 信息源的长度

    Returns:
        msg (array): 指定字节符号的概率分布的数据
    '''

    # 计算给定概率分布 symbol_prob 的累积概率分布 symbol_cumsum
    symbol_cumsum = symbol_prob.cumsum()

    # 生成 [0,1] 之间均匀分布的随机实数 symbol_random
    symbol_random = random.uniform(size=msgLength)

    # 输出符合条件的消息符号 symbol_random,插入 symbol_cumsum 指定位置
    msg = searchsorted(symbol_cumsum, symbol_random)

    return msg


def outputResToFile(outputFileName, msg):
    '''将信息写入文件

    将保存于msg中的信息按位写入文件中

    Args:
        outputFileName (str): 输出文件路径
        msg (list): 指定字节符号的概率分布的数据
    '''
    with open(outputFileName, 'wb') as ofn:

        # 将列表msg的元素按顺序写入指定二进制文件中
        for i in msg:
            ofn.write(i.to_bytes(1, 'big'))


def get_msg(P0, msgLength):
    Ext = ganExtend(P0)

    # 初始化一个numpy的数组用于存放用户输入文件读出的的概率分布
    symbol_prob = zeros(256)
    symbol_prob[:] = Ext

    # 获得生成的符合条件的数据的数组，并将其转换成列表，便于输出到二进制文件中
    msg = getInfoSouece(symbol_prob, msgLength).tolist()
    return msg

def main(argv):
    '''处理所有函数

    将所有函数串联起来，实现随机生成任意指定大小的文件，且符合任意指定的字节符号概率分布
    '''
    # 得到数据比特概率分布，目标文件路径以及信息源长度
    if len(argv) == 4:
        P0 = float(argv[1])
        msgLength = int(argv[2])
        outputFileName = argv[3]
    else:
        return

    Ext = ganExtend(P0)

    # 初始化一个numpy的数组用于存放用户输入文件读出的的概率分布
    symbol_prob = zeros(256)
    symbol_prob[:] = Ext

    # 获得生成的符合条件的数据的数组，并将其转换成列表，便于输出到二进制文件中
    msg = getInfoSouece(symbol_prob, msgLength).tolist()

    # 将指定字节符号的概率分布的数据写入指文件(anytype)
    outputResToFile(outputFileName, msg)

# 主程序执行
if __name__ == '__main__':
    main(argv)


