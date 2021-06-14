---
id: sync-proc
title: Synchronize among processes
sidebar_label: Sync. among processes
slug: /sync-proc
description: A tutorial about synchronizing the message among processes.
---

Synchronizing the messages from different sub-processes is not a easy task. Because the `print` functions from different processes could interfere each other. This package is designed for solving this problem. If users need to catch the stdout from the sub-processes of the same program, it is suitable to use `LineProcBuffer`.

The following example catches the messages from 4 different processes:

```python {9,18,22,24,26}
import multiprocessing
from contextlib import redirect_stdout
import syncstream


def worker_process(buffer: syncstream.LineProcMirror):
    '''Define the workder_process'''
    try:
        with redirect_stdout(buffer):
            print('Message', 'item')
    except Exception as err:
        buffer.send_error(err)
    else:
        buffer.send_eof()


if __name__ == '__main__':
    pbuf = syncstream.LineProcBuffer(10)  # Initialization.
    with multiprocessing.Pool(4) as pool:
        pool.map_async(
            worker_process,
            tuple(pbuf.mirror for _ in range(4))
        )  # Run 4 procs.
        pbuf.wait()  # Wait the eof signals.

    messages = pbuf.read()  # Get results.
    for mitem in messages:
        print(mitem)
```

In process-based synchronization, there is a shared buffer (`LineProcBuffer`) among all processes. We still let the maximal number of catched lines be 10:

```python
pbuf = syncstream.LineProcBuffer(10)
```

Different from the `LineBuffer` used for the multi-thread case, the `LineProcBuffer` itself is not directly shared by the processes. Instead, we use the following property to get a "copy" of the buffer.

```python
mirror = pbuf.mirror
```

The value `mirror` is an instance of `syncstream.LineProcMirror`. The `mirror` could be viewed as a copy of the buffer. Different form the buffer, it only maintains the current line to be written in the buffer. When the processes are running, the buffer and multiple mirrors play the roles of the receiver and sender respectively. The message synchronization between the mirrors and the buffer is process-safe.

The method

```python
pbuf.wait()
```

is used for waiting the closing signal from each mirror. The method `buffer.send_error` or `buffer.send_eof` would trigger a closing singal. In the above example, the `pbuf` needs to wait for 4 closing signal from the sub-processes.

:::danger

The mirror should not be copied in any case, because each time the property `pbuf.mirror` is accessed, the counter of the sub-process in `pbuf` would increase by 1. Therefore, it is not allowed to replace `tuple(pbuf.mirror for _ in range(4))` by `(pbuf.mirror, ) * 4`.

:::

:::info

The method `buffer.send_error` is used for catching the exception message. If an exception is triggered, there would be a special instance of `GroupedMessage` written in `pbuf`. This instance could be printed directly. The contents of the instance is the traceback of the raised exception.

:::
