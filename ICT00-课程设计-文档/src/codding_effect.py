from sys import argv
from bitstring import Bits, BitStream
from csv import writer
from numpy import log,uint8,ceil,log2
from io import BytesIO
def H_s(BS):
    '''计算信息熵
        根据用户输入的文件计算编码前文件信息熵和编码后文件信息熵
        Args:
            BS (BitStream): 文件的比特流
        
        Returns:
            H(BS1)编码前文件的信息熵    (信息比特/字节)
            H(BS2)编码后文件的信息熵    (信息比特/字节)
    '''
    #由于一个字节由八个二进制字符组成，因此可视为二进制字符信源的八次拓展
    count = 0
    for i in range(len(BS)):
        if BS[i]==1:
            count=count+1           #数出二进制串1的个数即可
    P1=count/len(BS)
    P0=1-P1
    Hs_bit=-P1*log2(P1)-P0*log2(P0)   #计算平均1bit的信息熵
    Hs_byte=Hs_bit*8                    #乘以8即等于平均一个字节的信息熵
    return Hs_byte,P0

def compress_ratio(BS1,BS2):
    '''计算压缩比
        根据用户输入的文件计算压缩比
        Args:
            BS1 (BitStream): 文件1的比特流
            BS2 (BitStream): 文件2的比特流
        Returns:
            compress(float)压缩比
    '''
    #用编码前文件大小除以编码后文件大小即可得到压缩比
    compress = len(BS1)/len(BS2)
    return compress

def l(in_file_name,P0):
    '''计算平均码长
        根据用户输入的文件计算平均码长
        Args:
            in_file_name(string): 输入文件
     
        Returns:
            l(float)平均码长           (码字数据比特/信源字节)
    '''
    byteorder = 'little'
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
    len_code=0
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
        c=bin(symbol)[2:].rjust(8,'0')
        
        cou = 0
        for b in range(len(c)):
            if c[b]=='0':
                cou=cou+1
        len_code = len_code+word_len*pow(P0,cou)*pow(1-P0,8-cou)
        
    return len_code

def coding_efficiency(Hs,L):
    '''计算编码效率
        根据用户输入的文件计算编码效率以及编码前文件信息熵和编码后文件信息熵
        Args:
            BS1 (BitStream): 文件1的比特流
            BS2 (BitStream): 文件2的比特流
       
        Returns:
            effict(float)编码效率
    '''
    n = Hs/L
    return n



def main(argv):
    # 参数列表：
    #   - 输入文件路径1 输入文件路径2 输出数据文件路径
    INPUT1 = argv[1]
    INPUT2 = argv[2]
    RESULT = argv[3]

    BS1 = BitStream(filename=INPUT1)
    BS2 = BitStream(filename=INPUT2)
    

    H_before,P0_before = H_s(BS1)
    H_after,P0_after = H_s(BS2)
    channel_ratio = compress_ratio(BS1,BS2)
    BS2_LEN = l(INPUT2,P0_before)
    cod = coding_efficiency(H_before,BS2_LEN)

    with open(RESULT, 'a') as of:
        f_csv = writer(of)
        f_csv.writerow([INPUT1,str(H_before), INPUT2, str(H_after),str(channel_ratio),str(BS2_LEN),str(cod)])

if __name__ == '__main__':
    main(argv)
