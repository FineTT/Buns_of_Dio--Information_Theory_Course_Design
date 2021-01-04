""" A basic source coder API.

This program is a API adapted from a basic demo showing a real-world example of source coding.
The key point here is how to handle meta-data, such codebook, so that decoder can get all necessary information to properly decode.

The format specification of the encoded file used here is:

Header  |header_size  : uint16, number of bytes for header
        |symbol_count : uint8, (number of symbols in codebook)-1
  ______|source_len   : uint32, number of symbols in source
  Code-1|symbol       : uint8, symbol
        |word_len     : uint8, number of bits for codeword
  ______|word         : ceil(word_len/8)*uint8, codeword
    ....|...
  ______|
  Code-n|symbol
        |word_len
________|word
Payload |encoded-data : many unit8

"""

from csv import reader
from io import BytesIO
from sys import argv

# Non-standard library
from numpy import uint8,ceil,asarray,fromfile
from dahuffman_no_EOF import HuffmanCodec


def encode(pmf_file_name, in_file_name, out_file_name):
    """
    @description: use to encode
    @param: pmf_file_name: the path of pmf file
    @param: in_file_name: the path of input file
    @param: out_file_name: the path of output file
    @return: (len(source), len(encoded)): (the length of source, the length of encoded source)
    """

    '''
    打开 CSV 文件并读取，然后保存为字典，
    将第一列以 uint8 保存为键，
    第二列以 float 保存为值
    '''
    with open(pmf_file_name, newline='') as csv_file:
        pmf = dict([(uint8(row[0]), float(row[1]))
                    for row in reader(csv_file)])

    # 构建赫夫曼树
    # 将EOF符号设置为“frequencies”中的第一个符号，
    # 这样“dahuffman”在构建Huffman树时不会添加新的EOF符号
    # 递归实现
    codec = HuffmanCodec.from_frequencies(pmf)
    # 以 uint8 读取输入文件中的数据
    source = fromfile(in_file_name, dtype='uint8')
    # 使用source作为编码方案编码
    # str.encode(encoding=source, errors='strict')
    encoded = codec.encode(source)

    # 返回编码后的码书
    codebook = codec.get_code_table()
    # 高低位标志，little 表示反序，左边为低位右边为高位
    byteorder = 'little'
    # 返回一个字节数组，
    # 对应 header_size，头部字节数，uint16格式
    header = bytearray(2)
    # 使用尾插法向字节数组 header 添加元素 len(codebook)-1
    # 对应 symbol_count，码书中符号个数减一，uint8 格式
    header.append(len(codebook)-1)
    # 扩展列表，追加序列 len(source).to_bytes(4, byteorder)
    # 对应 source_len，信源符号个数，uint32 格式
    header.extend(len(source).to_bytes(4, byteorder))
    # 向字节数组追加符号、码字长度以及码字
    for symbol, (word_len, word) in codebook.items():
        (word_len, word) = codebook[symbol]
        # 返回 word_len/8 向上取整的值，用于指定保存这个码字所需的字节数
        word_bytes = int(ceil(word_len / 8))
        header.append(symbol)
        header.append(word_len)
        # 将码字转为二进制追加到 header
        header.extend(word.to_bytes(word_bytes, byteorder))
    # 将 header 首部三位转为二进制，即 Header 部分
    header[0:2] = len(header).to_bytes(2, byteorder)

    '''
    以二进制方式把数据写入输出文件
    首先写入首部
    然后写入霍夫曼编码
    '''
    with open(out_file_name, 'wb') as out_file:
        out_file.write(header)
        out_file.write(encoded)

    # 返回信源长度，编码后的信源长度
    return (len(source), len(encoded))


def decode(in_file_name, out_file_name):
    """
    @description: use to decode
    @param: in_file_name: the path of input file
    @param: out_file_name: the path of output file
    @return: (len(encoded), len(decoded)): (the length of encoded source, the length of decoded source)
    """

    # 高低位标志，little 表示反序，左边为低位右边为高位
    byteorder = 'little'

    '''
    以二进制读取文件
    '''
    with open(in_file_name, 'rb') as in_file:
        # 第二位是首部长度(header_size)，以反序读取，转为 int
        header_size = int.from_bytes(in_file.read(2), byteorder)
        # 操作二进制数据，需使用BytesIO
        # 以二进制读取首部(Header) header_size-2 位部分
        header = BytesIO(in_file.read(header_size-2))
        # 读取全部文件数据
        encoded = in_file.read()

    codebook = {}
    # 获取 symbol_count，位于header第一位的第零位
    symbol_count = header.read(1)[0]
    # 获取 source_len，位于header第四位，以反序读取后转为int
    source_len = int.from_bytes(header.read(4), byteorder)
    # 将编码放入字典 codebook 中
    for k in range(symbol_count+1):
        # 读取符号
        symbol = uint8(header.read(1)[0])
        # 读取码字长度
        word_len = header.read(1)[0]
        # 码字字节数
        word_bytes = int(ceil(word_len / 8))
        # 码字
        word = int.from_bytes(header.read(word_bytes), byteorder)
        # 将码字长度、码字存入字典codebook中
        codebook[symbol] = (word_len, word)

    # 将字典作为参数初始化一个HuffmanCodec类用于译码
    codec = HuffmanCodec(codebook)
    # 译码
    # np.asarray()，将数据转化为ndarray但不占用新内存
    decoded = asarray(codec.decode(encoded))[:source_len]
    # 存入输出文件
    decoded.tofile(out_file_name)

    # 返回编码后长度，译码后长度
    return (len(encoded), len(decoded))


def main(argv):
    # 参数列表：
    
    encoded_file_name = argv[1]
    decoded_file_name = argv[2]

    # 接收到解码指令，调用decode函数进行对输入文件进行解码
    decode(encoded_file_name, decoded_file_name)


if __name__ == '__main__':
    main(argv)

