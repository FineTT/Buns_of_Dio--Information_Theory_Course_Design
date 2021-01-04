byteSourceEncoder
一个接近实用的无失真信源编码和解码器

用法
    • 基本用法：在cmd中调用
        byteSourceEncoder.exe PMF INPUT OUTPUT
        PMF      path to probability mass function CSV file
        INPUT    path to the encoder input file
        OUTPUT   path to the encoder output file

        byteSourceDecoder.exe INPUT OUTPUT
        INPUT    path to the decoder input file
        OUTPUT   path to the decoder output file
        – encode 命令部分
            • PMF：是一个CSV（逗号分隔值）文件，给定数值0-256的概率分布，格式如下：
	         它包含256行数据，第0行表示符号“0”，第255行表示符号“255”。
	         每行有两个逗号分隔的值：<symbol>，<probability>。
	         例如：
	         0,0.1
	         1,0.3
	         2,0.0
	         3,0.2
	         4,0.4
	         5,0
	         ...
	         255,0
            • INPUT：由byteSource按给定的PMF生成
            • OUTPUT：编码后的文件，格式以exampleSourceCoder.py的注释为准
        – decode 命令部分
            • INPUT：编码后的文件，格式与encode命令的OUTPUT文件一致
            • OUTPUT：解码后的文件，原则上应与encode命令的INPUT文件一致

    • 例如：
	byteSourceEncoder.exe ..\unit-test\pmf.byte.p0=0.1.csv ..\unit-test\source.p0=0.1.len=32KB.dat ..\_encoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp
	byteSourceDecoder.exe ..\_encoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp ..\_decoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp

包含文件
    • README.txt
      本文件，程序的说明文件

    • byteSourceEncoder.py
      霍夫曼编码程序的源代码

    • byteSourceDecoder.py
      霍夫曼解码程序的源代码

    • dahuffman.py/dahuffman_no_EOF.py
      运行byteSourceCoder.py所需要的python程序