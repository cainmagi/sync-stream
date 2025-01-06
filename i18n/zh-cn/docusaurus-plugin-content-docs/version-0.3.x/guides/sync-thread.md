---
id: sync-thread
title: 同步于线程之间
sidebar_label: 线程同步
slug: /sync-thread
description: 教程，展示了如何在线程之间同步信息。
---

大多情况下，其实并不需要透过本包来捕获子线程的标准输出，这是缘于标准输出在线程之间本来就是共享的，用户可以轻松地自行实现同步器。这里仅仅作为一个同步地快速接口、供用户使用。

下例捕获了来自四个不同线程的信息：

```python showLineNumbers title="sync-thread.py"
import threading
import time
from contextlib import redirect_stdout
import syncstream


def worker_thread() -> None:
    '''定义workder_thread。'''
    # 获得线程ID。
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # 用以回退到python 3.7。
    # 打印10次。
    for i in range(10):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), 'Line:', 'buffer', 'new', i)


def run_4_threads(buffer: syncstream.LineBuffer) -> None:
    '''在stdout重定向的情形下，运行四个线程。'''
    # highlight-next-line
    with redirect_stdout(buffer):
        thd_pool = list()
        for _ in range(4):
            thd = threading.Thread(target=worker_thread)
            thd_pool.append(thd)
        for thd in thd_pool:
            thd.start()
        for thd in thd_pool:
            thd.join()


if __name__ == '__main__':
    # highlight-start
    tbuf = syncstream.LineBuffer(10)  # 初始化。
    run_4_threads(tbuf)  # 运行四个线程。

    messages = tbuf.read()  # 获取结果。
    # highlight-end
    for mitem in messages:
        print(mitem)
```

由于管理stdout和stderr的是进程，同一进程的不同线程将共享同样的stdout和stderr。上例中，只需要重定向stdout一次即可。

即使如此，此例还是使用了[`syncstream.LineBuffer(10)`](../apis/mproc/LineBuffer.mdx)，这是由于该类是线程安全的。使用它、可以像在主线程里捕获stdout或stderr那样、在子线程里捕获这些信息。
