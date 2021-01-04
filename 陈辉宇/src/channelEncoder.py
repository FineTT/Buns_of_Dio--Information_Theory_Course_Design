'''
信道编码模块

这里使用的编码文件的格式规范是：
Header  |decode_method  : uint, 解码方式 0 为重复码 1 为 线性分组码
        |factor : uint, 重复码的码字长度 或 线性分组码的奇偶校验长度
  ______|source_len   : uint, 编码前序列的长度
Payload |encoded-data : many uint8
'''

__author__ = "Chen, Huiyu"
__email__ = "chy126101@gmail.com"
__version__ = "20210102.1458"

from bitstring import Bits, BitStream
from sys import argv
from numpy import dot, array, hstack

def encode_repeat(BS_encode, n):
    '''
    重复码编码

    Args:
        BS_encode (bitstream): 输入文件比特流
        n (int): 重复码的码字长度
    Returns:
        BS_encode_repetition (bitstream): 编码后的比特流
    '''
    # 判断是否是规定的重复码的码字长度
    if (n in (3, 5, 7, 9)) == False:
        return

    # 转成二进制便于编码
    BS_encode_bin = BS_encode.bin
    BS_encode_rep = ''
    for i in BS_encode_bin:
        BS_encode_rep += n * i
    BS_encode_repetition = BitStream(bin=BS_encode_rep)

    return BS_encode_repetition

def encode_linear(BS_encode, j):
    '''
    线性分组码编码

    Args:
        BS_encode (bitstream): 输入文件比特流
        j (int): 奇偶校验码的码字长度
    Returns:
        C (array): 编码后的数组
    '''
    if (j in (3, 4, 5))== False:
        return

    # 获取生成矩阵
    G = genG(j)

    # 将比特流转换为数组形式
    BS_bin = BS_encode.bin
    BS_len = len(BS_bin)
    BS_bin_arr = array([int(BS_bin[i], 2) for i in range(BS_len)])

    # 将数组转换为指定样式（由奇偶校验长度j决定）的矩阵
    if j == 3:
        BS_bin_arr = addZero(BS_bin_arr, 4)
        BS_mat = BS_bin_arr.reshape(-1, 1).reshape(-1, 4)
    elif j == 4:
        BS_bin_arr = addZero(BS_bin_arr, 11)
        BS_mat = BS_bin_arr.reshape(-1, 1).reshape(-1, 11)
    elif j == 5:
        BS_bin_arr = addZero(BS_bin_arr, 26)
        BS_mat = BS_bin_arr.reshape(-1, 1).reshape(-1, 26)

    # 矩阵相乘相加，得到编码后的数组
    C = dot(BS_mat, G).ravel() % 2
    C = addZero(C, 8)
    C_str = ''.join(str(i) for i in C)
    C_BS = BitStream(bin=C_str)
    return C_BS

def IO(PATH, method='I', data=None):
    '''
    输入输出函数

    Args:
        PATH (str): 文件路径
        method (str): 需要使用的方法，I(输入)、O(输出)，默认为 I
        data (array): 需要输出到指定文件中的数据，若空置则无输出或生成一个空文件
    Returns:
        (BitStream): 当调用输入方法时返回输入文件的比特流
    '''

    def I(PATH):
        return BitStream(filename=PATH)
    def O(PATH, data):
        with open(PATH, 'wb') as ofs:
            data.tofile(ofs)

    if method=='I':
        return I(PATH)
    elif method=='O':
        O(PATH, data)
    else:
        return

def gen_header(method, var, BS_len, BS):
    '''
    生成文件头

    Args:
        method (int): 编码方式，0 为重复码 1 为 线性分组码
        var (int): 重复码的码字长度 或 线性分组码的奇偶校验长度
        BS_len (int): 编码前序列的长度
        BS (bitstream): 编码后文件比特流
    Returns:
        source (bitstream): 最终输出文件比特流
    '''
    method = BitStream(uint=method, length=8)
    factor = BitStream(uint=var, length=8)
    source_length = Bits(uint=BS_len, length=32)
    headers = encode_repeat(method + factor + source_length, 3)
    source = headers + BS
    return source

def genG(j):
    '''
    获取生成矩阵，共有三种供获取

    Args:
        j (int): 奇偶校验长度，分别可以是 3, 4, 5
    Returns:
        (array): 指定的生成矩阵
    '''
    G_7_4 = ((1, 0, 0, 0, 1, 1, 1),
             (0, 1, 0, 0, 1, 0, 1),
             (0, 0, 1, 0, 0, 1, 1),
             (0, 0, 0, 1, 1, 1, 0))
    G_15_11 = ((1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1),
               (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1),
               (0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0),
               (0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1),
               (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1),
               (0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0),
               (0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1),
               (0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0),
               (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1),
               (0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0),
               (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1),)
    G_31_26 = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
               [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
               [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
               [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
               [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
               [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1],
               [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0]]
    if j == 3:
        return array(G_7_4)
    elif j == 4:
        return array(G_15_11)
    elif j == 5:
        return array(G_31_26)
    else:
        return None

def addZero(arr, n):
    '''
    根据需要在数组后面补足 0

    Args：
        arr (array): 指定的数组
        n (int): 需要添加的最长长度
    '''
    lack0 = len(arr) % n
    if lack0 != 0:
        arr = hstack((arr, array([0] * (n - lack0))))
    return arr

def main(argv):

    # 处理用户输入
    method = argv[1]
    INPUT = argv[2]
    OUTPUT = argv[3]
    factor = int(argv[4])

    # 获取用户输入文件的比特流
    BS = IO(INPUT, method='I')
    BS_len = len(BS)

    # 根据用户输入的参数，调用相关信道编码方式
    M = -1
    if method == '-r':
        # 重复码 3, 5, 7
        C = encode_repeat(BS, factor)
        M = 0
    elif method == '-l':
        # 汉明码 3, 4, 5
        C = encode_linear(BS, factor)
        M = 1
    else:
        return

    C_final = gen_header(M, factor, BS_len, C)

    # 将编码后的比特流输出到指定路径中
    IO(OUTPUT, method='O', data=C_final)

if __name__ == "__main__":
    main(argv)
