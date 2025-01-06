---
id: daemon-buffer
title: 安全关闭mirrors
sidebar_label: 安全关闭镜像（mirror）
slug: /daemon-buffer
description: 进阶教程，展示如何提前中断mirrors。
---

使用[`LineProcBuffer`](../apis/mproc/LineProcBuffer.mdx)和[`LineHostBuffer`](../apis/host/LineHostBuffer.mdx)的时候，需要使用镜像（mirror）。前文中，已经解释了如何透过继承`LineProcBuffer`来捕获进度。在那个例子中，需要透过如下做法、将`pbuf.wait`移到背景运行：

```python
...
thd = threading.Thread(target=pbuf.wait, daemon=True)
thd.start()
print('开始等待。')
while pbuf.progress < 100:
    time.sleep(0.1)
print('进度达到100%。')
thd.join()
...
```

要确保所有的子进程安全结束，需要使用`thd.join`来等待`pbuf.wait`终结。然而，某些情况下，需要在子进程完成之前，提前中断之。使用`terminate`方法固然是一种可行思路，不过，这样的中断可能不够安全。更好的做法是向子进程发送关闭信号。当子进程尝试写入新的信息时，它会检查关闭信号。若检测到了关闭信号，则会抛出`StopIteration`异常。例如，若将以上代码修改如下：

```python
thd = threading.Thread(target=pbuf.wait, daemon=True)
thd.start()
print('开始等待。')
prog = pbuf.progress
while prog < 100:
    time.sleep(0.1)
    prog = pbuf.progress
    if prog > 10:
        # highlight-next-line
        pbuf.stop_all_mirrors()
        break
print('进度未达到100%。')
thd.join()
```

则子进程会提前中断。相应地，buffer也无法接收到子进程的正常终结信息。取而代之的是，捕获到来自子进程的`StopIteration`异常。
