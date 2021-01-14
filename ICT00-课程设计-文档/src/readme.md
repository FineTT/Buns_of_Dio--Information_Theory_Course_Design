# Information transmission system model

## Usage

1. `byteSource.exe`
- Basic usage

```help
  byteSource.exe P0 msgLength OUTPUT 
  P0                 信源消息概率分布
  msgLength          消息序列的长度 
  OUTPUT             输出文件路径
```

> For example:
>     `byteSource.exe 0.5 1024 "data/output.dat"`

- Its calculation model `byteSource_calc.exe`
```help
  byteSource_calc.exe INPUT OUTPUT
  INPUT              信源输出消息序列文件
  OUTPUT             输出文件路径
```

> For example:
>    `byteSource_calc.exe "data/input.dat" "data/output.csv"`

2. `byteChannel.exe`
- Basic usage

```help
  byteChannel.exe INPUT P OUTPUT
  INPUT              输入文件路径
  P                  错误传递概率
  OUTPUT             输出文件路径
```

> For example:
>     `byteChannel.exe "data/input.dat" P "data/output.dat"`

- Its calculation model `byteSource_calc.exe`
```help
  byteSource_calc.exe ChannelInput ChannelOutput
  ChannelInput       信道输入消息序列文件
  ChannelOutput      信道输出消息序列文件
  OUTPUT             输出文件路径
```

> For example:
>    `byteChannel_calc.exe "data/ChannelInput.dat" "data/ChannelOutput.dat" "data/output.csv"`

3.  `byteSourceEncoder.exe` & `byteSourceDecoder.exe`
- Basic usage
```help
  byteSourceEncoder.exe PMF INPUT OUTPUT
  PMF      是一个CSV（逗号分隔值）文件，给定数值0-256的概率分布，格式如下：
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
  INPUT    由byteSource按给定的PMF生成
  OUTPUT   编码后的文件输出路径
```

> For example:
>     `byteSourceEncoder.exe "..\unit-test\pmf.byte.p0=0.1.csv" "..\unit-test\source.p0=0.1.len=32KB.dat" "..\_encoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp"`

```
  help
  byteSourceDecoder.exe INPUT OUTPUT
  INPUT    编码后的文件，格式与encode中的OUTPUT文件一致
  OUTPUT   解码后的文件，原则上应与encode中的INPUT文件一致  
```

> For example:
>     `byteSourceDecoder.exe "..\_encoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp" "..\_decoded_pmf.p0=0.1_source.p0=0.1.len=32KB.tmp"`

```help
  codding_effect.exe INPUT1 INPUT2 OUTPUT 
  INPUT1             输入编码前文件路径
  INPUT2             输入编码后文件路径
  OUTPUT             指标计算后CSV文件
```

> For example:
>    `codding_effect.exe "data/FileBeforeEncoding.dat" "data/FileAfterEncoding.dat" "data/output.csv"`
4. `channelEncoder.exe` & `channelDecoder.exe`
- Basic usage

```help
  channelEncoder.exe method INPUT OUTPUT factor
  method             解码方式: -r 为重复码, -l 为线性分组码
  INPUT              输入文件路径
  OUTPUT             输出文件路径
  factor             重复码的码字长度(5, 7, 9) 或 线性分组码的奇偶校验长度(3, 4, 5)
```

> For example:
>     `channelEncoder.exe 0 "data/input.dat" "data/output.dat" 3`

```help
  channelDecoder.exe INPUT OUTPUT
  INPUT              编码后文件路径
  OUTPUT             解码后文件路径
```

> For example:
>     `channelDecoder.exe "data/input.dat" "data/output.dat"`

- Its calculation model `channelCoder_calc.exe`
```help
  byteSource_calc.exe FileBeforeEncoding FileAfterEncoding FileDecoded OUTPUT
  FileBeforeEncoding       编码前文件
  FileAfterEncoding        编码后文件
  FileDecoded              解码后文件
  OUTPUT                   输出文件路径
```

> For example:
>    `channelCoder_calc.exe "data/FileBeforeEncoding.dat" "data/FileAfterEncoding.dat" "data/FileDecoded.dat" "data/output.csv"`
