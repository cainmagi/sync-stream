# Sync-stream

This project is designed for providing the synchoronization of the stdout / stderr among different threads, processes, devices or hosts. The package could be used for the following cases:

1. Use `syncstream.LineBuffer`: Multiple threads are created. The messages (stdout) from different threads are required to be collected.
2. Use `syncstream.LineProcBuffer` in the main process, and `syncstream.LineProcMirror` in the sub-processes: Multiple sub-processes are created on the same device. The stdout / stderr of each process is redirected to a `LineProcMirror`, and the results are collected by `LineProcBuffer`.
3. Use `syncstream.LineFileBuffer`: Multiple processes are created. These processes may be deployed on different devices (even with different platforms), but all devices could get accessed to the same shared disk. In this case, the message could be shared by locked files. Each process would hold an independent `LineFileBuffer` pointing to the same log files.
4. Use `syncstream.LineHostBuffer` on the server side, and `syncstream.LineHostMirror` on the client side: Multiple processes are deployed on different devices, and they could not share the same disk. In this case, the message are synchronized by the web service. Each process would hold a `LineHostMirror`, and the results would be collected by `LineHostBuffer`.

The basic package would not contain the `file` and `host` modules. To install the package, please use the following options:

```bash
pip install syncstream[option1,option2...]
```

| Option  | Supports |
| :-----: | :------- |
| `file` | Install dependencies for the `file` module. The module provides `syncstream.LineFileBuffer`. |
| `host` | Install dependencies for the `host` module. The module provides `syncstream.LineHostBuffer`, and `syncstream.LineHostMirror`. |

## Documentation

View the documentation here: [:blue_book: https://cainmagi.github.io/sync-stream/](https://cainmagi.github.io/sync-stream/)

## Update reports

### 0.3.3 @ 6/29/2021

1. Fix small typos.
2. Bump the dependencies to the newest versions.

### 0.3.2 @ 6/14/2021

1. Fix a bug caused by stopping the mirrors.
2. Format the meta-data defined in `setup.py`.
3. Add the documentation. Currently only the tutorial is finished.

### 0.3.0 @ 6/4/2021

1. Support the stop signal for `mproc` and `host` modules.
2. Fix some bugs in the testing script.
3. Fix typos.

### 0.2.2 @ 5/25/2021

1. Add `clear()` methods for all buffers and mirrors.
2. Fix typos in the package setup and info file.
3. Fix a bug caused by writing data to the host in the testing scripts for Linux.

### 0.2.1 @ 5/24/2021

1. Add the PyPI publish workflow.

### 0.2.0 @ 5/24/2021

1. Finish the synchronization based on the file lock package `fasteners`.
2. Finish the synchronization based on the web service packages `flask`, `flask-restful` and `urllib3`.
3. Fix the compatibility of the testing scripts for `py36`, `py37`.

### 0.1.0 @ 5/22/2021

1. Finish the synchronization based on the stdlib.
2. Create this project.
