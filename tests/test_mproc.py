# -*- coding: UTF-8 -*-
"""
Tests: multi-processing-based synchronization
=============================================
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
Test scripts of the module `mproc`.
"""

import sys
import time
import warnings
import threading
import multiprocessing
import logging

from typing import Union

try:
    from typing import Sequence
except ImportError:
    from collections.abc import Sequence

from syncstream import LineBuffer, LineProcBuffer, LineProcMirror
from syncstream.base import GroupedMessage


def worker_writter() -> None:
    """The worker for the thread-mode testing."""
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(10):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), "Line:", "buffer", "new", i)


def worker_writter_lite() -> None:
    """The worker for the thread-mode testing (lite).

    This version only writes two lines.
    """
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(2):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), "Line:", "buffer", "new", i)


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


def worker_process(buffer: LineProcMirror) -> None:
    """The worker for the process-mode testing.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    with buffer:
        for i in range(10):
            time.sleep(0.01)
            print("Line:", "buffer", "new", i, end="\n")
        create_warn()
        try:
            create_warn(catch=True)
        except Warning as warn:
            buffer.send_warning(warn)
        try:
            raise TypeError("A test error.")
        except TypeError as err:
            buffer.send_error(err)
        else:
            buffer.send_eof()


def worker_process_lite(buffer: LineProcMirror) -> None:
    """The worker for the process-mode testing (clear).

    The process only write two lines for each process.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    with buffer:
        for i in range(2):
            time.sleep(0.01)
            print("Line:", "buffer", "new", i, end="\n")
        buffer.send_eof()


def worker_process_stop(buffer: LineProcMirror) -> None:
    """The worker for the process-mode testing (stop).

    The process used for testing the manually terminating.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    try:
        with buffer:
            for i in range(10):
                time.sleep(0.1)
                print("Line:", "buffer", "new", i, end="\n")
                if i > 0:
                    time.sleep(0.9)
    except Exception as error:  # pylint: disable=broad-except
        buffer.send_error(error)
    else:
        buffer.send_eof()


class TestMProc:
    """Test the mproc module of the package."""

    @staticmethod
    def show_messages(
        log: logging.Logger, messages: Sequence[Union[str, GroupedMessage]]
    ) -> None:
        """Show the messages from the buffer."""
        for i, item in enumerate(messages):
            if isinstance(item, GroupedMessage):
                if item.type == "error":
                    log.critical("%s", "{0:02d}: {1}".format(i, item))
                elif item.type == "warning":
                    log.warning("%s", "{0:02d}: {1}".format(i, item))
                else:
                    log.info("%s", "{0:02d}: {1}".format(i, item))
            else:
                log.info("%s", "{0:02d}: {1}".format(i, item))

    def test_mproc_read_buffer(self) -> None:
        """Test the `read()` functionalities of mproc.LineBuffer."""
        log = logging.getLogger("test_mproc")
        tbuf = LineBuffer(3)

        tbuf.write("line1\n")
        tbuf.write("line2\nline3")

        # Read all.
        lines = tbuf.read()
        assert lines[0] == "line1" and lines[1] == "line2" and lines[2] == "line3"

        # Read one line.
        lines = tbuf.read(1)
        assert len(lines) == 1 and lines[0] == "line3"

        # Read two lines.
        lines = tbuf.read(2)
        assert len(lines) == 2 and lines[0] == "line2" and lines[1] == "line3"

        # Read three lines.
        lines = tbuf.read(3)
        assert (
            len(lines) == 3
            and lines[0] == "line1"
            and lines[1] == "line2"
            and lines[2] == "line3"
        )

        self.show_messages(log, lines)

    def test_mproc_buffer(self) -> None:
        """Test the mproc.LineBuffer in the single thread mode."""
        log = logging.getLogger("test_mproc")
        tbuf = LineBuffer(10)

        # Write buffer.
        with tbuf:
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
        messages = tbuf.read(4)
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
        messages = tbuf.read()
        self.show_messages(log, messages)
        assert len(messages) == 10

    def test_mproc_with_logging(self, capsys) -> None:
        """Test the integration between mproc.LineBuffer and stdlib logging module."""
        log = logging.getLogger("test_mproc")

        # Create the testing logger.
        log_t = logging.getLogger("test_mproc_with_logging")
        log_t.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        log_t.addHandler(handler)

        # Start the test.
        tbuf = LineBuffer(10)
        with tbuf:
            log_t.debug("Test item 1.")
            log_t.debug("Test item 2.")
            log_t.debug("Test item 3.")
        # This step is not required out of pytest, because pytest always captures the
        # std stream created by log.
        tbuf.write(capsys.readouterr().err)
        messages = tbuf.read()
        self.show_messages(log, messages)
        assert len(messages) == 3

    def test_mproc_thread(self) -> None:
        """Test the mproc.LineBuffer in the multi-thread mode."""
        log = logging.getLogger("test_mproc")
        tbuf = LineBuffer(10)

        # Write buffer.
        with tbuf:
            thd_pool = list()
            for _ in range(4):
                thd = threading.Thread(target=worker_writter)
                thd_pool.append(thd)
            for thd in thd_pool:
                thd.start()
            for thd in thd_pool:
                thd.join()

        # Show the buffer results.
        messages = tbuf.read()
        self.show_messages(log, messages)
        assert len(messages) == 10

    def test_mproc_process(self) -> None:
        """Test the mproc.LineProcBuffer in the multi-process mode."""
        log = logging.getLogger("test_mproc")
        pbuf = LineProcBuffer(maxlen=20)

        # Write buffer.
        with multiprocessing.Pool(4) as pool:
            pool.map_async(worker_process, tuple(pbuf.mirror for _ in range(4)))
            log.debug("The main stdout is not influenced.")
            pbuf.wait()
        log.debug("Confirm: The main stdout is not influenced.")

        # Show the buffer results.
        messages = pbuf.read()
        assert len(messages) == 20
        self.show_messages(log, messages)

    def test_mproc_thread_clear(self) -> None:
        """Test the mproc.LineBuffer.clear() in the multi-thread mode."""
        log = logging.getLogger("test_mproc")
        tbuf = LineBuffer(20)

        def write_4_threads() -> None:
            with tbuf:
                thd_pool = list()
                for _ in range(4):
                    thd = threading.Thread(target=worker_writter_lite)
                    thd_pool.append(thd)
                for thd in thd_pool:
                    thd.start()
                for thd in thd_pool:
                    thd.join()

        # Write buffer.
        write_4_threads()
        write_4_threads()

        # Check message items, should be 16 now.
        messages = tbuf.read()
        assert len(messages) == 16

        # Clear, then check message items, should be 0 now.
        tbuf.clear()
        log.debug("Clear all messages.")
        messages = tbuf.read()
        assert len(messages) == 0

        # Write buffer with a clear.
        write_4_threads()
        tbuf.clear()
        log.debug("Clear all messages.")
        write_4_threads()

        # Check message items, should be 8 now.
        messages = tbuf.read()
        assert len(messages) == 8

    def test_mproc_process_clear(self) -> None:
        """Test the mproc.LineBuffer.clear() in the multi-process mode."""
        log = logging.getLogger("test_mproc")
        pbuf = LineProcBuffer(maxlen=20)

        # Write buffer.
        with multiprocessing.Pool(4) as pool:
            pool.map_async(worker_process_lite, tuple(pbuf.mirror for _ in range(4)))
            pbuf.wait()
            pool.map_async(worker_process_lite, tuple(pbuf.mirror for _ in range(4)))
            pbuf.wait()

        # Check message items, should be 16 now.
        messages = pbuf.read()
        assert len(messages) == 16

        # Clear, then check message items, should be 0 now.
        pbuf.clear()
        log.debug("Clear all messages.")
        messages = pbuf.read()
        assert len(messages) == 0

        # Write buffer with a clear.
        with multiprocessing.Pool(4) as pool:
            pool.map_async(worker_process_lite, tuple(pbuf.mirror for _ in range(4)))
            pbuf.wait()
            pbuf.clear()
            log.debug("Clear all messages.")
            pool.map_async(worker_process_lite, tuple(pbuf.mirror for _ in range(4)))
            pbuf.wait()

        # Check message items, should be 8 now.
        messages = pbuf.read()
        assert len(messages) == 8

    def test_mproc_process_stop(self) -> None:
        """Test the mproc.LineBuffer.stop_all_mirrors() in the multi-process mode."""
        log = logging.getLogger("test_mproc")
        pbuf = LineProcBuffer(maxlen=20)

        # Write buffer.
        log.debug("Start to write the buffer.")
        with multiprocessing.Pool(4) as pool:
            pool.map_async(worker_process_stop, tuple(pbuf.mirror for _ in range(4)))
            time.sleep(1.0)
            log.debug("Send the close signal to the sub-processes.")
            pbuf.stop_all_mirrors()
            pbuf.wait()
            pbuf.reset_states()

        # Check message items, should be 16 now.
        messages = pbuf.read()
        assert len(messages) >= 4
        # Show the buffer results.
        self.show_messages(log, messages)

    def test_mproc_process_force_stop(self) -> None:
        """Test the mproc.LineBuffer.force_stop() in the multi-process mode."""
        log = logging.getLogger("test_mproc")
        pbuf = LineProcBuffer(maxlen=20)

        # Write buffer.
        log.debug("Start to write the buffer.")
        with multiprocessing.Pool(4) as pool:
            pool.map_async(worker_process_stop, tuple(pbuf.mirror for _ in range(4)))
            time.sleep(1.0)
            log.debug("Send the close signal to the sub-processes.")
            pbuf.force_stop()
            pbuf.wait()
            pbuf.reset_states()

        # Check message items, should be 16 now.
        messages = pbuf.read()
        assert len(messages) >= 4
        # Show the buffer results.
        self.show_messages(log, messages)
