---
id: sync-proc
title: 同步于进程之间
sidebar_label: 进程同步
slug: /sync-proc
description: 教程，展示了如何在进程之间同步信息。
---

在不同的子进程之间同步信息并不轻松，这是由于不同进程的`print`函数会相互干扰。此包就是为了解决这个问题而设计的。若用户的需求是、在同一程序的不同子进程之间捕获标准输出，则建议使用[`LineProcBuffer`](../apis/mproc/LineProcBuffer.mdx)。

下例捕获了来自四个不同进程的信息：

```python showLineNumbers title="sync-proc.py"
import multiprocessing
from contextlib import redirect_stdout
import syncstream


def worker_process(buffer: syncstream.LineProcMirror):
    '''定义workder_process。'''
    try:
        # highlight-next-line
        with redirect_stdout(buffer):
            print('Message', 'item')
    except Exception as err:
        buffer.send_error(err)
    else:
        buffer.send_eof()


if __name__ == '__main__':
    # highlight-next-line
    pbuf = syncstream.LineProcBuffer(10)  # 初始化。
    with multiprocessing.Pool(4) as pool:
        pool.map_async(
            worker_process,
            # highlight-next-line
            tuple(pbuf.mirror for _ in range(4))
        )  # 运行四个进程。
        # highlight-next-line
        pbuf.wait()  # 等待终结信号。

    # highlight-next-line
    messages = pbuf.read()  # 获得结果。
    for mitem in messages:
        print(mitem)
```

在基于进程的同步里，不同进程之间共享一个缓存（`LineProcBuffer`）。可以令捕获信息的最大行数设置为10：

```python
pbuf = syncstream.LineProcBuffer(10)
```

不同于用于多线程场景的[`LineBuffer`](../apis/mproc/LineBuffer.mdx)，`LineProcBuffer`自身并不直接在进程之间共享。取而代之的是，使用以下属性来获取缓存的“拷贝”。

```python
mirror = pbuf.mirror
```

值`mirror`是[`syncstream.LineProcMirror`](../apis/mproc/LineProcMirror.mdx)的实例。值`mirror`可以视为缓存的拷贝。不同于缓存本身，它只用于维护要写入缓存的当前行。当进程运行的时候，缓存本身、和它的多个镜像（mirrors）之间、属于收发信息的关系。对于不同mirror，和缓存之间的通信是进程安全的。

该方法

```python
pbuf.wait()
```

用来等待所有mirror的关闭信号。调用[`buffer.send_error`](../apis/mproc/LineProcMirror.mdx#-send_error)或[`buffer.send_eof`](../apis/mproc/LineProcMirror.mdx#-send_eof)将触发关闭信号。在上例中，`pbuf`需要等待来自不同子进程的四个关闭信号。

:::danger

任何情况下，都不应拷贝mirror，这是由于每次获取属性值[`pbuf.mirror`](../apis/mproc/LineProcBuffer.mdx#-mirror)时，`pbuf`所维护的子进程计数将会增加1。因此，将`tuple(pbuf.mirror for _ in range(4))`替换成`(pbuf.mirror, ) * 4`是不允许的。

:::

:::info

方法`buffer.send_error`是用来捕获异常信息的。若触发了异常，在`pbuf`中将会写入一个特殊的实例[`GroupedMessage`](../apis/base/GroupedMessage.mdx)。该实例可以直接打印，且内容包含了所抛出异常的回溯信息（traceback）。

:::
