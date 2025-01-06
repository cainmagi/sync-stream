---
id: daemon-buffer
title: Safely close mirrors
sidebar_label: Safely close mirrors
slug: /daemon-buffer
description: An advanced tutorial about the early stop of the mirrors.
---

We need to use the mirrors when using [`LineProcBuffer`](../apis/mproc/LineProcBuffer.mdx) and [`LineHostBuffer`](../apis/host/LineHostBuffer.mdx). In the previous article, we have explained how to use the derived class of `LineProcBuffer` to catch the progress. In that example, we need to move the `pbuf.wait` method to the background like this:

```python
...
thd = threading.Thread(target=pbuf.wait, daemon=True)
thd.start()
print('Start to wait.')
while pbuf.progress < 100:
    time.sleep(0.1)
print('Progress is 100%.')
thd.join()
...
```

To make sure that all sub-processes are finished safely, we need to use `thd.join` to wait the `pbuf.wait` method finishes. However, in some cases, we need to terminate the sub-processes before they are finished. Use `terminate` method of the process is a possible solution. However, such kind of termination is not safe enough. A better way is to send a closing signal to the sub-processes. When each sub-process intends to write new messages, it needs to check the closing signal. If the closing signal is detected, a `StopIteration` exception would be raised. For example, if we change the above part like this:

```python
thd = threading.Thread(target=pbuf.wait, daemon=True)
thd.start()
print('Start to wait.')
prog = pbuf.progress
while prog < 100:
    time.sleep(0.1)
    prog = pbuf.progress
    if prog > 10:
        # highlight-next-line
        pbuf.stop_all_mirrors()
        break
print('Progress is not 100%.')
thd.join()
```

The sub-process would be terminated in advance. Consequently, the buffer would not be able to receive the finishing message from the sub-process. Instead, the `StopIteration` exceptions from the sub-processes would be catched.
