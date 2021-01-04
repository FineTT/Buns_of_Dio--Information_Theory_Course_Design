from bitstring import BitStream
from sys import argv
from numpy import log2
from channelDecoder import gen_header, decode_repeat
import csv
from pathlib import Path

def gen_BER(FBE, FD):
    '''获取误码率

    Args:
        FBE (str): 编码前文件比特流转换的字符串
        FD (str): 解码后文件比特流转换的字符串

    Returns:
        error_rate (float): 误码率
    '''

    error_bit = list(map(lambda x, y: x == y, FBE, FD)).count(False)
    error_rate = error_bit / len(FBE)
    return error_rate

def gen_Rs(method, factor):
    '''获取编码前信息传输率以及编码后信息传输率

    Args:
        method (str): 解码方式 0 为重复码 1 为 线性分组码
        factor (str): 重复码的码字长度 或 线性分组码的奇偶校验长度

    Returns:
        R_before (float): 编码前信息传输率
        R_after (float): 编码后信息传输率
    '''
    R_before = log2(2) / 1
    if method == 0:
        R_after = log2(2) / factor
    elif method == 1:
        if factor == 3:
            R_after = 4 * log2(2) / 7
        elif factor == 4:
            R_after = 11 * log2(2) / 15
        elif factor == 5:
            R_after = 26 * log2(2) / 31
        else:
            return
    else:
        return

    return R_before, R_after

def gen_compression_ratio(source_length, FAE):
    '''获取编码前信息传输率以及编码后信息传输率

    Args:
        source_length (int): 编码前文件长度
        FAE (str): 编码后文件比特流转换的字符串

    Returns:
        (float): 压缩比
    '''
    return source_length / len(FAE)


def output_ratios_to_file(out_file_name, data):
    '''获取编码前信息传输率以及编码后信息传输率

    Args:
        out_file_name (str): 输出文件(.CSV) 的路径
        data (list): 所有计算得到的数据及文件信息
    '''

    # Write the header for all columns, if the output file does not exist.
    if not Path(out_file_name).is_file():
        with open(out_file_name, 'w', newline='') as out_file:
            csvwriter = csv.writer(out_file, quoting=csv.QUOTE_ALL)
            csvwriter.writerow(
                ['file before encoding', 'file after encoding', 'file after decoding', 'Bit Error Rate', 'Information Transfer Efficiency of Source', 'Information Transfer Efficiency of Channel', 'Compression Ratio'])

    with open(out_file_name, 'a', newline='') as out_file:
        csvwriter = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        csvwriter.writerow(data)


def main(argv):
    # 处理用户输入数据
    file_before_encode_path = argv[1]
    file_after_encode_path = argv[2]
    file_decode_path = argv[3]
    file_output_path = argv[4]

    # 得到输入文件的比特流
    file_before_encode = BitStream(filename=file_before_encode_path)
    file_after_encode = BitStream(filename=file_after_encode_path)
    file_decode = BitStream(filename=file_decode_path)

    # 将输入文件的比特流转化为字符串
    FBE = file_before_encode.bin
    FAE = file_after_encode.bin
    FD = file_decode.bin

    # 获得编码后文件的头文件信息
    headers = BitStream(bin=decode_repeat(file_after_encode, 3, method='-h'))
    method, factor, source_length = gen_header(headers)

    # 获取 误码率、编码前后信道传输率、压缩比
    BER = gen_BER(FBE, FD)
    R_b, R_a = gen_Rs(method, factor)
    CR = gen_compression_ratio(source_length, FAE)

    # 将以上计算所得的信息输入到指定的文件(.CSV)中
    data = [file_before_encode_path, file_after_encode_path, file_decode_path, BER, R_b, R_a, CR]

    output_ratios_to_file(file_output_path, data)

if __name__ == '__main__':
    main(argv)
