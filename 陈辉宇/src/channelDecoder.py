'''
信道解码模块

这里使用的编码文件的格式规范是：
Header  |decode_method  : uint, 解码方式 0 为重复码 1 为 线性分组码
        |factor : uint, 重复码的码字长度 或 线性分组码的奇偶校验长度
  ______|source_len   : uint, 编码前序列的长度
Payload |encoded-data : many uint8
'''

__author__ = "Chen, Huiyu"
__email__ = "chy126101@gmail.com"
__version__ = "20210102.1449"

# 引入相关库
from numpy import array, hstack, dot, identity
from bitstring import Bits, BitStream
from sys import argv


def decode_repeat(BS_decode, BDRT, method='-a'):
    ''' 
    重复码解码，兼有解码文件头功能

    Args:
        BS_dncode (bitstream): 待解码的输入文件比特流
        BDRT (int): 重复码的码字长度
        method (str): -a 表示解码文件本身、-h 表示解码文件头，默认为 '-a'
    Returns:
        BS_encode_repetition (str): 解码后生成的字符串
    '''

    # 三个字符串备用
    BS_encode_repetition = '0b'
    BS = ''
    BS_decode_rep = ''

    if method == '-h':
        # 解码文件头
        BS_decode_rep = BS_decode.bin[0:144]
    else:
        # 解码文件
        BS_decode_rep = BS_decode.bin[144:]

    # 解码程序本题
    for x in BS_decode_rep:
        BS += x
        if len(BS) == BDRT:
            if BS.count('1') > BS.count('0'):
                BS_encode_repetition += '1'
            elif BS.count('1') < BS.count('0'):
                BS_encode_repetition += '0'
            BS = ''

    # 若空文件则返回 None
    if BS_encode_repetition == '0b':
        return

    return BS_encode_repetition


def decode_linear(C_decode, j):
    ''' 
    线性分组码解码

    Args:
        C_dncode (bitstream): 待解码的输入文件比特流
        j (int): 奇偶校验长度
    Returns:
        BS_info_mat_str (str): 解码后生成的字符串
    '''

    # 根据奇偶校验长度，得到(n, k)线性分组码的 n, k
    if j == 3:
        n = 7
        k = 4
    elif j == 4:
        n = 15
        k = 11
    else:
        n = 31
        k = 26

    # 去掉文件头部分开始解码
    BS_bin = C_decode.bin[144:]

    # 还原成 n列 的矩阵形式
    BS_len = len(BS_bin)
    overflow0 = BS_len % n
    if overflow0 != 0:
        BS_bin = BS_bin[:(BS_len - overflow0)]
    BS_bin_arr = array([int(BS_bin[i], 2) for i in range(len(BS_bin))])
    BS_data_mat = BS_bin_arr.reshape(-1, n)

    # 获得信息组
    BS_info_mat = BS_data_mat[:, :k]

    # 获得校验矩阵
    GT = genG(j)[:, k:].T
    H = hstack((GT, identity(GT.shape[0])))

    # 获得伴随式
    S = dot(BS_data_mat, H.T) % 2

    # 纠错
    HT = array(H.T)
    pos = []
    for i in range(len(S)):
        for j in range(len(HT)):
            if (S[i] == HT[j]).all():
                pos.append((i, j))
    BS_info_mat = linear_correct(BS_info_mat, pos, k)

    # 将矩阵转换为字符串
    BS_info_mat_ravel = BS_info_mat.ravel()
    BS_info_mat_str = ''.join(str(i) for i in BS_info_mat_ravel)

    return BS_info_mat_str


def linear_correct(BS_info_mat, pos, n):
    ''' 
    线性分组码解码
    
    Args:
        BS_info_mat (array): 信息组
        pos (liat): 误码位置
        n (int): 信息组的长度，与监督元相区别
    Returns:
        BS_info_mat (array): 纠错后的信息组
    '''
    for i in range(len(pos)):
        if pos[i][1] < n:
            BS_info_mat[pos[i]] = not(BS_info_mat[pos[i]]) + 0
    return BS_info_mat


def gen_header(headers):
    ''' 
    获取文件头信息

    Args:
        headers (bitstream): 文件头
    Returns:
        method (int): 编码方式，0 为重复码 1 为 线性分组码
        factor (int): 重复码的码字长度 或 线性分组码的奇偶校验长度
        source_length (int): 编码前序列的长度
    '''
    method = int(headers.bin[0:8], 2)
    factor = int(headers.bin[8:16], 2)
    source_length = int(headers.bin[16:], 2)
    return method, factor, source_length


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

    if method == 'I':
        return I(PATH)
    elif method == 'O':
        O(PATH, data)
    else:
        return


def main(argv):

    # 处理用户输入数据
    INPUT = argv[1]
    OUTPUT = argv[2]

    # 得到文件信息比特流
    BS_decode = IO(INPUT, method='I')

    # 获取文件头信息
    headers = BitStream(bin=decode_repeat(BS_decode, 3, method='-h'))
    method, factor, source_length = gen_header(headers)

    # 根据文件头信息解码
    if method == 0:
        R_str = decode_repeat(BS_decode, factor)
    elif method == 1:
        R_str = decode_linear(BS_decode, factor)
    else:
        return

    # 将解码后的信息流写入指定文件中
    R = BitStream(bin=R_str[0:source_length+2])
    IO(OUTPUT, method='O', data=R)

if __name__ == "__main__":
    main(argv)
