__author__ = "Chen, Huiyu"
__email__ = "chy126101@gmail.com"
__version__ = "20201230.1409"

from pandas import DataFrame
from numpy import fromfile, uint8, histogram, log2
from sys import argv

def IO(PATH, method='I', data=None):
    '''输入输出函数

    Args:
        PATH (str): 文件路径
        method (str): 选择I(输入)或O(输出)，默认是输入
        data : 需要输出的数据，当method为O的时候起作用
    Returns:
        data (list): CSV文件中，指定字节符号的概率分布
    '''
    def I(PATH):
        ''' 处理输入数据 '''
        return fromfile(PATH, dtype=uint8)

    def O(PATH, data):
        ''' 处理输出数据 '''

        # 建立一个字典用于存储将要输出的数据
        csvbook = {}
        i = 0
        for header in data[0]:
            csvbook[header] = data[1][i]
            i += 1   

        # 用 pandas 的 DataFrame 方法处理输出数据
        dataframe = DataFrame(csvbook)

        # 将输出数据写入指定文件中
        dataframe.to_csv(PATH, sep=',')
            
    if method == 'I':
        return I(PATH)
    elif method == 'O':
        O(PATH, data)
    else:
        return None


def genPDistribution(Input_Data):
    '''由输入文件数据，得到两种概率分布

    Args:
        input_Data (list): 输入数据
    Returns:
        P_list (list): 字节符号的概率分布
        P0 (float): 数据比特概率分布
    '''

    # 获得字节符号的概率分布
    (hist, bin_edges) = histogram(Input_Data, bins=range(257))
    P = hist / Input_Data.size
    P_list = list(P)

    # 获得数据比特概率分布
    P0 = 1 - P_list[-1]**(1/8)

    return P_list, P0


def genEntropy(P0):
    '''由数据比特概率分布计算信息熵以及信源冗余度

    Args:
        P0 (float): 数据比特概率分布
    Returns:
        I (float): 二元DMS的信息熵（信息比特/二元消息）
        R (float): 二元DSM的信源冗余度
    '''

    # 获得二元DMS的信息熵
    I = P0 * log2(1 / P0) + (1 - P0) * log2(1 / (1 - P0))

    # 获得二元DSM的信源冗余度
    Imax = log2(1 / 0.5)
    R = I / Imax

    return I, R

def outputResToFile(PATH, P, P0, I, R):
    '''输出函数

    Args:
        PATH (str): 输出文件(.CSV)路径
        P (list): 字节符号的概率分布
        P0 (float): 数据比特概率分布
        I (float): 二元DMS的信息熵（信息比特/二元消息）
        R (float): 二元DSM的信源冗余度
    '''
    
    # 字典的键，备用
    headers = ['P(n)', 'P0', 'H(x)', 'redundancy']

    # 字典的值，备用
    containers = [P, P0, I, R]

    # 输出上述两个数据到指定文件中
    IO(PATH, method='O', data=(headers, containers))

def main(argv):
    # 获取用户输入数据
    INPUT = argv[1]
    OUTPUT = argv[2]

    # 处理输入数据
    inputData = IO(INPUT)

    # 获取字节符号的概率分布以及数据比特概率分布
    P, P0 = genPDistribution(inputData)

    # 由数据比特概率分布获取二元DMS的信息熵以及信源冗余度
    I, R = genEntropy(P0)

    # 将上面的得到的所有数据输出到指定文件(.CSV)中
    outputResToFile(OUTPUT, P, P0, I, R)

if __name__ == "__main__":
    main(argv)
