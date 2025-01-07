# Sync-stream

<p><img alt="Banner" src="https://repository-images.githubusercontent.com/370331958/6ca07907-3936-444e-8d0d-39c9a0867ef3"></p>

<p align="center">
  <a href="https://github.com/cainmagi/sync-stream/releases/latest"><img alt="GitHub release (latest SemVer)" src="https://img.shields.io/github/v/release/cainmagi/sync-stream?logo=github&sort=semver&style=flat-square"></a>
  <a href="https://github.com/cainmagi/sync-stream/releases"><img alt="GitHub all releases" src="https://img.shields.io/github/downloads/cainmagi/sync-stream/total?logo=github&style=flat-square"></a>
  <a href="https://github.com/cainmagi/sync-stream/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/cainmagi/sync-stream?style=flat-square&logo=opensourceinitiative&logoColor=white"></a>
  <a href="https://pypi.org/project/syncstream"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/syncstream?style=flat-square&logo=pypi&logoColor=white&label=pypi"/></a>
</p>
<p align="center">
  <a href="https://github.com/cainmagi/sync-stream/actions/workflows/python-package.yml"><img alt="GitHub Actions (Build)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/sync-stream/python-package.yml?style=flat-square&logo=githubactions&logoColor=white&label=build"></a>
  <a href="https://github.com/cainmagi/sync-stream/actions/workflows/python-publish.yml"><img alt="GitHub Actions (Release)" src="https://img.shields.io/github/actions/workflow/status/cainmagi/sync-stream/python-publish.yml?style=flat-square&logo=githubactions&logoColor=white&label=release"></a>
</p>

This project is designed for providing the synchoronization of the stdout / stderr among different threads, processes, devices or hosts. The package could be used for the following cases:

1. Use `syncstream.LineBuffer`: Multiple threads are created. The messages (stdout) from different threads are required to be collected.
2. Use `syncstream.LineProcBuffer` in the main process, and `syncstream.LineProcMirror` in the sub-processes: Multiple sub-processes are created on the same device. The stdout / stderr of each process is redirected to a `LineProcMirror`, and the results are collected by `LineProcBuffer`.
3. Use `syncstream.LineFileBuffer`: Multiple processes are created. These processes may be deployed on different devices (even with different platforms), but all devices could get accessed to the same shared disk. In this case, the message could be shared by locked files. Each process would hold an independent `LineFileBuffer` pointing to the same log files.
4. Use `syncstream.LineHostBuffer` on the server side, and `syncstream.LineHostMirror` on the client side: Multiple processes are deployed on different devices, and they could not share the same disk. In this case, the message are synchronized by the web service. Each process would hold a `LineHostMirror`, and the results would be collected by `LineHostBuffer`.

The basic package would not contain the `file` and `host` modules. To install the package, please use the following options:

```bash
pip install syncstream[option1,option2...]
```

| Option | Supports                                                                                                                      |
| :----: | :---------------------------------------------------------------------------------------------------------------------------- |
| `file` | Install dependencies for the `file` module. The module provides `syncstream.LineFileBuffer`.                                  |
| `host` | Install dependencies for the `host` module. The module provides `syncstream.LineHostBuffer`, and `syncstream.LineHostMirror`. |
| `test` | Install dependencies for running tests.                                                                                       |
| `dev`  | Install dependencies for developers.                                                                                          |

## Documentation

View the documentation here: [:blue_book: https://cainmagi.github.io/sync-stream/](https://cainmagi.github.io/sync-stream/)

## Update reports

See the versions in the [CHANGELOG :spiral_notepad:](./CHANGELOG.md) file.
