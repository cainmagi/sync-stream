---
id: introduction
title: Introduction
description: The introduction of sync-stream. We provide 4 modes designed for different cases.
slug: /
---

This project is designed for providing the synchoronization of the stdout / stderr among different threads, processes, devices or hosts. The package could be used for the following cases:

|  Class  |  <center>Usage</center>  |
| :-----: | :------ |
| `LineBuffer` | Used when multiple threads are created. The messages (stdout) from different threads are required to be collected.
| `LineProcBuffer` | Use `syncstream.LineProcBuffer` in the main process, and `syncstream.LineProcMirror` in the sub-processes: Multiple sub-processes are created on the same device. The stdout / stderr of each process is redirected to a `LineProcMirror`, and the results are collected by `LineProcBuffer`. |
| `LineFileBuffer` | Multiple processes are created. These processes may be deployed on different devices (even with different platforms), but all devices could get accessed to the same shared disk. In this case, the message could be shared by locked files. Each process would hold an independent `LineFileBuffer` pointing to the same log files. |
| `LineHostBuffer` | Use `syncstream.LineHostBuffer` on the server side, and `syncstream.LineHostMirror` on the client side: Multiple processes are deployed on different devices, and they could not share the same disk. In this case, the message are synchronized by the web service. Each process would hold a `LineHostMirror`, and the results would be collected by `LineHostBuffer`. |
