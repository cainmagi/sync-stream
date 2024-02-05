# -*- coding: UTF-8 -*-
"""
Tests: file-based synchronization
=================================
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
Test scripts of the module `file`.
"""

import os
import time
import warnings
import multiprocessing
import logging
import shutil

try:
    from typing import Tuple
except ImportError:
    from builtins import tuple as Tuple

import pytest

from syncstream import LineFileBuffer  # pylint: disable=import-error

if LineFileBuffer is None:
    pytest.skip(
        (
            "The requirements for the file lock module is not installed, the test is "
            "skipped."
        ),
        allow_module_level=True,
    )


def create_warn(catch: bool = False) -> None:
    """Create a warn message by the stdlib.

    Different from the logging module, the messages created by this way could be
    catched by the process-safe line buffer.
    """
    if catch:
        with warnings.catch_warnings(record=True):
            warnings.filterwarnings("error")
            warnings.warn("An example of python warning.", UserWarning)
    else:
        warnings.warn("An example of python warning.", UserWarning)


def worker_process(log_info: Tuple[str, int]) -> None:
    """The worker for the process-mode testing.
    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.

    Arguments
    ---------
    log_info: `(log_path, log_len)`
        - log_path: `str`, the path of the log files.
        - log_len: `str`m the maximal number of log files.
    """
    buffer = LineFileBuffer(log_info[0], maxlen=log_info[1], tmp_id=str(os.getpid()))
    with buffer:
        for i in range(10):
            time.sleep(0.01)
            print("Line", "buffer", "new", i, end="\n")
        create_warn()
        buffer.new_line()  # A final signal


def worker_process_lite(log_info: Tuple[str, int]) -> None:
    """The worker for the process-mode testing (clear).

    The process only write two lines for each process.

    Arguments
    ---------
    log_info: `(log_path, log_len)`
        - log_path: `str`, the path of the log files.
        - log_len: `str`m the maximal number of log files.
    """
    buffer = LineFileBuffer(log_info[0], maxlen=log_info[1], tmp_id=str(os.getpid()))
    with buffer:
        for i in range(2):
            time.sleep(0.01)
            print("Line", "buffer", "new", i, end="\n")
        buffer.new_line()  # A final signal


class TestFile:
    """Test the file module of the package."""

    def setup_method(self) -> None:
        """The setup stage for each test."""
        self.log_folder = "data-logs"  # pylint: disable=attribute-defined-outside-init
        if os.path.isdir(self.log_folder):
            shutil.rmtree(self.log_folder)
        os.makedirs(self.log_folder, exist_ok=True)
        self.log_path = os.path.join(
            self.log_folder, "test-file.log"
        )  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self) -> None:
        """The teardown stage for each test."""
        shutil.rmtree(self.log_folder)

    def test_file_read_buffer(self) -> None:
        """Test the `read()` functionalities of mproc.LineBuffer."""
        log = logging.getLogger("test_file")
        fbuf = LineFileBuffer(self.log_path, maxlen=3)

        fbuf.write("line1\n")
        fbuf.write("line2\nline3")

        # Read all.
        lines = fbuf.read()
        assert lines[0] == "line1" and lines[1] == "line2" and lines[2] == "line3"

        # Read one line.
        lines = fbuf.read(1)
        assert len(lines) == 1 and lines[0] == "line3"

        # Read two lines.
        lines = fbuf.read(2)
        assert len(lines) == 2 and lines[0] == "line2" and lines[1] == "line3"

        # Read three lines.
        lines = fbuf.read(3)
        assert (
            len(lines) == 3
            and lines[0] == "line1"
            and lines[1] == "line2"
            and lines[2] == "line3"
        )

        for i, item in enumerate(lines):
            log.info("%s", "{0:02d}: {1}".format(i, item))

    def test_file_buffer(self) -> None:
        """Test the file.LineFileBuffer in the single thread mode."""
        log = logging.getLogger("test_file")
        buffer = LineFileBuffer(self.log_path, maxlen=10)

        # Write buffer.
        with buffer:
            print("Hello!")
            print("Multiple", "sep", "example")
            print("An example of \n splitted message.\n")
            print("An extra message.")
            print(
                "An example of long and unicode message: I/O层次结构的顶部是抽象基类 "
                "IOBase 。它定义了流的基本接口。但是请注意，对流的读取和写入之间没有分离。如"
                "果实现不支持指定的操作，则会引发 UnsupportedOperation 。\n抽象基类 "
                "RawIOBase 是 IOBase 的子类。它负责将字节读取和写入流中。 RawIOBase 的子类 "
                "FileIO 提供计算机文件系统中文件的接口。\n抽象基类 BufferedIOBase 继承了 "
                "IOBase ，处理原始二进制流（ RawIOBase ）上的缓冲。其子类 BufferedWriter "
                "、 BufferedReader 和 BufferedRWPair 分别缓冲可读、可写以及可读写的原始二"
                "进制流。 BufferedRandom 提供了带缓冲的可随机访问流接口。 BufferedIOBase "
                "的另一个子类 BytesIO 是内存中字节流。\n抽象基类 TextIOBase 继承了 IOBase "
                "。它处理可表示文本的流，并处理字符串的编码和解码。类 TextIOWrapper 继承了 "
                "TextIOBase ，是原始缓冲流（ BufferedIOBase ）的缓冲文本接口。最后， "
                "StringIO 是文本的内存流。\n参数名不是规范的一部分，只有 open() 的参数才用"
                "作关键字参数。"
            )
            print("Multiple", "sep", "example", end="")

        # Check the validity of the buffer results.
        messages = buffer.read(4)
        assert messages[0] == (
            "抽象基类 BufferedIOBase 继承了 IOBase ，处理原始二进制流（ RawIOBase ）上的缓"
            "冲。其子类 BufferedWriter 、 BufferedReader 和 BufferedRWPair 分别缓冲可读、"
            "可写以及可读写的原始二进制流。 BufferedRandom 提供了带缓冲的可随机访问流接口。 "
            "BufferedIOBase 的另一个子类 BytesIO 是内存中字节流。"
        )
        assert messages[1] == (
            "抽象基类 TextIOBase 继承了 IOBase 。它处理可表示文本的流，并处理字符串的编码和"
            "解码。类 TextIOWrapper 继承了 TextIOBase ，是原始缓冲流（ BufferedIOBase ）"
            "的缓冲文本接口。最后， StringIO 是文本的内存流。"
        )
        assert messages[2] == (
            "参数名不是规范的一部分，只有 open() 的参数才用作关键字参数。"
        )
        assert messages[3] == "Multiple sep example"

        # Show the buffer results.
        messages = buffer.read()
        for i, item in enumerate(messages):
            log.info("%s", "{0:02d}: {1}".format(i, item))
        assert len(messages) == 10

    def test_file_process(self) -> None:
        """Test the file.LineFileBuffer in the multi-process mode."""
        log = logging.getLogger("test_file")
        fbuf = LineFileBuffer(self.log_path, maxlen=20)

        # Write buffer.
        with multiprocessing.Pool(4) as pool:
            pool.map(worker_process, tuple((self.log_path, 20) for _ in range(4)))
            log.debug("The main stdout is not influenced.")
        log.debug("Confirm: The main stdout is not influenced.")

        # Show the buffer results.
        messages = fbuf.read()
        for i, item in enumerate(messages):
            log.info("%s", "{0:02d}: {1}".format(i, item))
        assert len(messages) == 20

    def test_file_process_clear(self) -> None:
        """Test the file.LineFileBuffer.clear() in the multi-process mode."""
        log = logging.getLogger("test_file")
        fbuf = LineFileBuffer(self.log_path, maxlen=20)

        # Clear, then check message items, should be 0 now.
        fbuf.clear()
        log.debug("Clear all messages.")
        messages = fbuf.read()
        assert len(messages) == 0

        # Write buffer
        with multiprocessing.Pool(4) as pool:
            pool.map(worker_process_lite, tuple((self.log_path, 20) for _ in range(4)))
            pool.map(worker_process_lite, tuple((self.log_path, 20) for _ in range(4)))

        # Check message items, should be 16 now.
        messages = fbuf.read()
        assert len(messages) == 16

        # Clear, then check message items, should be 0 now.
        fbuf.clear()
        log.debug("Clear all messages.")
        messages = fbuf.read()
        assert len(messages) == 0

        # Write buffer with a clear
        with multiprocessing.Pool(4) as pool:
            pool.map(worker_process_lite, tuple((self.log_path, 20) for _ in range(4)))
            fbuf.clear()
            log.debug("Clear all messages.")
            pool.map(worker_process_lite, tuple((self.log_path, 20) for _ in range(4)))

        # Check message items, should be 8 now.
        messages = fbuf.read()
        assert len(messages) == 8
