# Information transmission system model

## Usage

1. `byteSource.exe`
- Basic usage

```help
  byteSource.exe P0 OUTPUT msgLength 
  P0                 信源消息概率分布
  OUTPUT             输出文件路径
  msgLength          消息序列的长度 
```

> For example:
>     `byteSource.exe 0.5 "data/output.dat" 1024`

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
  byteChannel.exe INPUT NOISE OUTPUT
  INPUT              输入文件路径
  NOISE              噪声文件路径
  OUTPUT             输出文件路径
```

> For example:
>     `byteChannel.exe "data/input.dat" "data/noise.dat" "data/output.dat"`

- Its calculation model `byteSource_calc.exe`
```help
  byteSource_calc.exe ChannelInput ChannelOutput
  ChannelInput       信道输入消息序列文件
  ChannelOutput      信道输出消息序列文件
  OUTPUT             输出文件路径
```

> For example:
>    `byteChannel_calc.exe "data/ChannelInput.dat" "data/ChannelOutput.dat" "data/output.csv"`

3. 霍夫曼编码，按上面的格式补充一下

4. `channelEncoder.exe` & `channelDecoder.exe`
- Basic usage

```help
  channelEncoder.exe method INPUT NOISE factor
  method             解码方式: 0 为重复码, 1 为线性分组码
  INPUT              输入文件路径
  OUTPUT             输出文件路径
  factor             重复码的码字长度(3, 5, 7) 或 线性分组码的奇偶校验长度(3, 4, 5)
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