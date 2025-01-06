---
id: sync-thread
title: Synchronize among threads
sidebar_label: Sync. among threads
slug: /sync-thread
description: A tutorial about synchronizing the message among threads.
---

In most cases, we do not need this package for captureing the sub-thread's stdout, because the stdout among different threads are shared. Users could implement their own synchronizer easily. This package is only used for providing a fast interface for the synchronization.

The following example catches the messages from 4 different threads:

```python showLineNumbers title="sync-thread.py"
import threading
import time
from contextlib import redirect_stdout
import syncstream


def worker_thread() -> None:
    '''Define the workder_thread.'''
    # Get the thread ID
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    # Print for 10 times.
    for i in range(10):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), 'Line:', 'buffer', 'new', i)


def run_4_threads(buffer: syncstream.LineBuffer) -> None:
    '''Run 4 threads with stdout redirected.'''
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
    tbuf = syncstream.LineBuffer(10)  # Initialization.
    run_4_threads(tbuf)  # Run 4 threads.

    messages = tbuf.read()  # Get results.
    # highlight-end
    for mitem in messages:
        print(mitem)
```

Since stdout and stderr are maintained by the process. Different threads of the same process would share the same stdout and stderr. In the above example, we only need to redirect the stdout for one time.

We are still using [`syncstream.LineBuffer(10)`](../apis/mproc/LineBuffer.mdx), because this class is thread-safe. We could catch the stdout or stderr inside each thread like what we do in the main thread.
