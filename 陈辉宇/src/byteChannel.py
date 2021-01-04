__author__ = "Chen, Huiyu"
__email__ = "chy126101@gmail.com"
__version__ = "20201230.1532"

from sys import argv
from byteSource import get_msg

def handleFileData(inputFileName, P):
    '''打开二进制文件(.csv)，处理数据

    读入用户输入的二进制文件的数据，将数据按列逐个写入一个列表中并返回

    Args:
        inputFileName (str): 二进制文件路径
        noiseFileName (str): 二进制噪声文件路径

    Returns:
        data (list): 
    '''
    with open(inputFileName, 'rb') as inp:
        inputData = inp.read()

    noiseData = get_msg(P, len(inputData))
        
    return inputData, noiseData


def byteChannel(inputData, noiseData):
    '''将噪声作用于输入文件

    将噪声文件中的每一位与原文件对应位进行异或运算，
    从而得到被噪声作用过的输出文件

    Args:
        inputData (list): 输入文件数据
        noiseData (list): 噪声文件数据

    Returns:
        outputData (list): 输出文件数据
    '''
    
    # 输入文件数据列表长度
    msg_len = len(inputData)

    # 生成按位异或后的列表
    outputData = [noiseData[i] ^ inputData[i] for i in range(msg_len)]
        
    return outputData


def outputResToFile(outputFileName, outputData):
    '''将信息写入文件

    将保存于msg中的信息按位写入文件中

    Args:
        outputFileName (str): 输出文件路径
        outputData (list): 噪声作用后的输出文件的数据
    '''
    with open(outputFileName, 'wb') as ofn:

        # 将列表outputData的元素按顺序写入指定二进制文件中
        for i in outputData:
            ofn.write(i.to_bytes(1, 'big'))

def main(argv):
    # 参数列表: 分别为输入文件路径、噪声文件路径以及输出文件路径
    inputFileName = argv[1]
    P = float(argv[2])
    outputFileName = argv[3]

    # 处理用户输入
    inputData, noiseData = handleFileData(inputFileName, P)

    # 输入文件数据进入指定错误概率的有噪信道
    outputData = byteChannel(inputData, noiseData)

    # 将噪声作用后的输出文件数据导入到指定路径文件中
    outputResToFile(outputFileName, outputData)

if __name__ == '__main__':
    main(argv)
