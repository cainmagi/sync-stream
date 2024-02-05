# -*- coding: UTF-8 -*-
"""
Tests: host-based synchronization
=================================
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
Test scripts of the module `host`.
"""

import sys
import time
import json
import warnings
import threading
import multiprocessing
import logging

from typing import Union, Any

try:
    from typing import Sequence
    from typing import Tuple, Dict
except ImportError:
    from collections.abc import Sequence
    from builtins import tuple as Tuple, dict as Dict

import pytest

from syncstream import LineHostBuffer, LineHostMirror, LineHostReader
from syncstream.base import (
    GroupedMessage,
    SerializedMessage,
    is_serialized_grouped_message,
)

if LineHostBuffer is None:
    pytest.skip(
        "The requirements for the host module is not installed, the test is skipped.",
        allow_module_level=True,
    )

try:
    from werkzeug.serving import make_server
    import urllib3.util
    import flask
except ImportError:
    pytest.skip(
        (
            "The requirements for testing the host module is not installed, the test "
            "is skipped."
        ),
        allow_module_level=True,
    )

from syncstream import webtools


def worker_writter(address: str) -> None:
    """The worker for the thread-mode testing."""
    hbuf = LineHostMirror(address=address)
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(10):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), "Line:", "buffer", "new", i, file=hbuf)
    hbuf.send_eof()


def worker_writter_lite(address: str) -> None:
    """The worker for the thread-mode testing (lite).

    This version only writes two lines.
    """
    hbuf = LineHostMirror(address=address)
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(2):
        time.sleep(0.1)
        print('Thd: "{0}";'.format(thd_id), "Line:", "buffer", "new", i, file=hbuf)
    hbuf.send_eof()


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


def worker_process(address: str) -> None:
    """The worker for the process-mode testing.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    buffer = LineHostMirror(address=address)
    for i in range(10):
        time.sleep(0.01)
        print("Line:", "buffer", "new", i, end="\n", file=buffer)
    with buffer:
        create_warn()
    try:
        with buffer:
            create_warn(catch=True)
    except Warning as warn:
        buffer.send_warning(warn)
    try:
        raise TypeError("A test error.")
    except TypeError as err:
        buffer.send_error(err)
    else:
        buffer.send_eof()


def worker_process_lite(address: str) -> None:
    """The worker for the process-mode testing (clear).

    The process only write two lines for each process.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    buffer = LineHostMirror(address=address)
    for i in range(2):
        time.sleep(0.01)
        print("Line:", "buffer", "new", i, end="\n", file=buffer)
    buffer.send_eof()


def worker_process_stop(address: str) -> None:
    """The worker for the thread-mode testing (lite).

    The process used for testing the manually terminating.

    The process should be ended by a `send_error()` or a `send_eof()`.

    Each end signal should be only sent by once.
    """
    buffer = LineHostMirror(address=address)
    try:
        for i in range(10):
            time.sleep(0.1)
            print("Line:", "buffer", "new", i, end="\n", file=buffer)
            if i > 0:
                time.sleep(10.0)
    except Exception as error:  # pylint: disable=broad-except
        buffer.send_error(error)
    else:
        buffer.send_eof()


def create_test_api(name: str = "api_name") -> flask.Flask:
    app_ = flask.Flask(name)

    # Configure APIs.
    LineHostBuffer(api_route="/sync-stream", maxlen=10).serve(app_)

    return app_


@pytest.fixture(scope="module")
def app() -> flask.Flask:
    app_ = create_test_api()

    return app_


@pytest.fixture(scope="module")
def temp_server(app: flask.Flask):
    @app.errorhandler(404)
    def page_not_found(error) -> Tuple[Dict[str, Any], int]:
        return {"message": "404 not found.", "code": "error-404"}, 404

    @app.route("/sync-stream/is-online", methods=("GET",))
    def is_online() -> Dict[str, Any]:
        return {"message": "success"}

    server = make_server("localhost", 5000, app)

    def run_app(server) -> None:
        cli = sys.modules["flask.cli"]
        setattr(cli, "show_server_banner", lambda *x: None)
        server.serve_forever()

    app_thread = threading.Thread(target=run_app, args=(server,))
    yield app_thread.start()

    server.shutdown()


def verify_online(address: str, retries: int = 5) -> None:
    """Verify the online status of the service.

    Arguments
    ---------
    address: `str`
        The service address.

    retries: `int`
        The number of retries for the verification.
    """

    with webtools.SafePoolManager(
        retries=urllib3.util.Retry(connect=retries, read=retries, redirect=retries),
        timeout=urllib3.util.Timeout(total=2.0),
    ) as _http:
        with _http.request(
            method="get",
            url="{addr}/is-online".format(addr=address),
            preload_content=False,
        ) as req:
            if req.status < 400:
                res = json.load(req)
                if res["message"] == "success":
                    return
    raise ConnectionError("test.connect: Fail to connect to the server.")


class TestHost:
    """Test the host module of the package."""

    @staticmethod
    def show_messages(
        log: logging.Logger,
        messages: Sequence[Union[SerializedMessage, GroupedMessage, str]],
    ) -> None:
        """Show the messages from the buffer."""
        for i, item in enumerate(messages):
            if is_serialized_grouped_message(item):
                item = GroupedMessage.deserialize(item)
            if isinstance(item, GroupedMessage):
                if item.type == "error":
                    log.critical("%s", "{0:02d}: {1}".format(i, item))
                elif item.type == "warning":
                    log.warning("%s", "{0:02d}: {1}".format(i, item))
                else:
                    log.info("%s", "{0:02d}: {1}".format(i, item))
            else:
                log.info("%s", "{0:02d}: {1}".format(i, item))

    def test_host_read_buffer(self, temp_server: None) -> None:
        """Test the `read()` functionalities of mproc.LineBuffer."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        hbuf = LineHostMirror(address=address)
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        hbuf.write("line1\n")
        hbuf.write("line2\nline3")

        with LineHostReader(address) as hreader:
            # Read status.
            assert hreader.closed is False
            assert hreader.maxlen == 10

            # Read all.
            lines = hreader.read()
            assert lines[0] == "line1" and lines[1] == "line2" and lines[2] == "line3"

            # Read one line.
            lines = hreader.read(1)
            assert len(lines) == 1 and lines[0] == "line3"

            # Read two lines.
            lines = hreader.read(2)
            assert len(lines) == 2 and lines[0] == "line2" and lines[1] == "line3"

            # Read three lines.
            lines = hreader.read(3)
            assert (
                len(lines) == 3
                and lines[0] == "line1"
                and lines[1] == "line2"
                and lines[2] == "line3"
            )

            self.show_messages(log, lines)

    def test_host_buffer(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer in the single thread mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        hbuf = LineHostMirror(address=address)
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        # Write buffer.
        print("Hello!", file=hbuf)
        print("Multiple", "sep", "example", file=hbuf)
        print("An example of \n splitted message.\n", file=hbuf)
        print("An extra message.", file=hbuf)
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
            "作关键字参数。",
            file=hbuf,
        )
        print("Multiple", "sep", "example", end="", file=hbuf)
        hbuf.send_eof()

        # Check the validity of the buffer results.
        with LineHostReader(address) as hreader:
            messages = hreader.read(4)
            assert len(messages) == 4
            assert messages[0] == (
                "抽象基类 BufferedIOBase 继承了 IOBase ，处理原始二进制流（ RawIOBase ）上"
                "的缓冲。其子类 BufferedWriter 、 BufferedReader 和 BufferedRWPair 分别缓"
                "冲可读、可写以及可读写的原始二进制流。 BufferedRandom 提供了带缓冲的可随机"
                "访问流接口。 BufferedIOBase 的另一个子类 BytesIO 是内存中字节流。"
            )
            assert messages[1] == (
                "抽象基类 TextIOBase 继承了 IOBase 。它处理可表示文本的流，并处理字符串的编"
                "码和解码。类 TextIOWrapper 继承了 TextIOBase ，是原始缓冲流"
                "（ BufferedIOBase ）的缓冲文本接口。最后， StringIO 是文本的内存流。"
            )
            assert messages[2] == (
                "参数名不是规范的一部分，只有 open() 的参数才用作关键字参数。"
            )
            assert messages[3] == "Multiple sep example"

        # Show the buffer results.
        with LineHostReader(address) as hreader:
            messages = hreader.read()
            self.show_messages(log, messages)
            assert len(messages) == 10

    def test_host_thread(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer in the multi-thread mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        # Write buffer.
        thd_pool = list()
        for _ in range(4):
            thd = threading.Thread(target=worker_writter, args=(address,))
            thd_pool.append(thd)
        for thd in thd_pool:
            thd.start()
        for thd in thd_pool:
            thd.join()
        sys.stdout = sys.__stdout__

        # Show the buffer results.
        with LineHostReader(address) as hreader:
            messages = hreader.read()
            self.show_messages(log, messages)
            assert len(messages) == 10

    def test_host_process(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer in the multi-process mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        # Write buffer.
        with multiprocessing.Pool(4) as pool:
            pool.map(worker_process, tuple(address for _ in range(4)))
            log.debug("The main stdout is not influenced.")
        log.debug("Confirm: The main stdout is not influenced.")

        # Show the buffer results.
        with LineHostReader(address) as hreader:
            messages = hreader.read()
            self.show_messages(log, messages)
            assert len(messages) == 10

    def test_host_thread_clear(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer.clear() in the multi-thread mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        with LineHostReader(address) as hreader:
            # Clear, then check message items, should be 0 now.
            assert hreader.clear()
            log.debug("Clear all messages.")
            messages = hreader.read()
            assert len(messages) == 0

            def write_2_threads() -> None:
                thd_pool = list()
                for _ in range(2):
                    thd = threading.Thread(target=worker_writter_lite, args=(address,))
                    thd_pool.append(thd)
                for thd in thd_pool:
                    thd.start()
                for thd in thd_pool:
                    thd.join()

            # Write buffer.
            write_2_threads()
            write_2_threads()
            sys.stdout = sys.__stdout__

            # Check message items, should be 8 now.
            messages = hreader.read()
            assert len(messages) == 8

            # Clear, then check message items, should be 0 now.
            assert hreader.clear()
            log.debug("Clear all messages.")
            messages = hreader.read()
            assert len(messages) == 0

            # Write buffer with a clear.
            write_2_threads()
            sys.stdout = sys.__stdout__
            assert hreader.clear()
            log.debug("Clear all messages.")
            write_2_threads()
            sys.stdout = sys.__stdout__

            # Check message items, should be 4 now.
            messages = hreader.read()
            assert len(messages) == 4

    def test_host_process_clear(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer.clear() in the multi-process mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        with LineHostReader(address) as hreader:
            # Clear, then check message items, should be 0 now.
            assert hreader.clear()
            log.debug("Clear all messages.")
            messages = hreader.read()
            assert len(messages) == 0

            # Write buffer.
            with multiprocessing.Pool(2) as pool:
                pool.map(worker_process_lite, tuple(address for _ in range(2)))
                pool.map(worker_process_lite, tuple(address for _ in range(2)))

            # Check message items, should be 8 now.
            messages = hreader.read()
            assert len(messages) == 8

            # Clear, then check message items, should be 0 now.
            assert hreader.clear()
            log.debug("Clear all messages.")
            messages = hreader.read()
            assert len(messages) == 0

            # Write buffer with a clear.
            with multiprocessing.Pool(2) as pool:
                pool.map(worker_process_lite, tuple(address for _ in range(2)))
                assert hreader.clear()
                log.debug("Clear all messages.")
                pool.map(worker_process_lite, tuple(address for _ in range(2)))

            # Check message items, should be 4 now.
            messages = hreader.read()
            assert len(messages) == 4

    def test_host_process_stop(self, temp_server: None) -> None:
        """Test the host.LineHostBuffer.stop_all_mirrors() in the multi-process mode."""
        log = logging.getLogger("test_host")
        address = "http://localhost:5000/sync-stream"
        verify_online(address)
        log.info("Successfully connect to the remote server.")

        with LineHostReader(address) as hreader:
            # Write buffer.
            log.debug("Start to write the buffer.")
            with multiprocessing.Pool(4) as pool:
                workers = pool.map_async(
                    worker_process_stop, tuple(address for _ in range(4))
                )
                time.sleep(1.0)
                log.debug("Send the close signal to the sub-processes.")
                assert hreader.stop_all_mirrors()
                workers.wait()

            assert hreader.reset_states

            # Show the buffer results.
            messages = hreader.read()
            self.show_messages(log, messages)
