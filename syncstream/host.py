# -*- coding: UTF-8 -*-
"""
Host-based stream synchronization
=================================
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
This module is based on Flask and urllib3. The message is collected by a Flask service,
and the stream is redirected to a web request handle.
"""

import os
import sys
import io
import weakref
import json
import threading
import contextlib
import types
import collections
import collections.abc
from urllib.parse import urlencode

from typing import Union, Optional, NoReturn
from typing import TextIO

try:
    from typing import Tuple, Dict, Type
    from typing import ChainMap
except ImportError:
    from builtins import tuple as Tuple, dict as Dict, type as Type
    from collections import ChainMap

import urllib3
import urllib3.util

import flask
from flask import request
from flask.views import MethodView

from .base import is_end_line_break, GroupedMessage, SerializedMessage
from .webtools import SafePoolManager, clean_http_manager
from .mproc import _LineBuffer


class LineHostMirror(contextlib.AbstractContextManager):
    """The mirror for the host-safe line-based buffer.

    This mirror is the client of the services from LineHostBuffer. It should be
    initialized independently, and would be used for managing the lines written to
    the buffer. Different from LineProcMirror, the independent mirror does not require
    shared queue.
    """

    def __init__(
        self, address: str, aggressive: bool = False, timeout: Optional[int] = None
    ) -> None:
        """Initialization

        Arguments
        ---------
        address: `str`
            The address of the LineHostBuffer. The redirected stream would send the
            messages to this address.

        aggressive: `bool`
            The aggressive mode. If enabled, each call for the `write()` method would
            trigger the service synchronization. Otherwise, the synchronization would
            be triggered when a new line is written.

        timeout: `int | None`
            The timeout of the web syncholizing events. If not set, the synchronization
            would block the current process.
        """
        if not isinstance(address, str) or address == "":
            raise TypeError(
                'syncstream: The argument "address" should be a non-empty str.'
            )
        self.address: str = address
        self.__buffer: io.StringIO = io.StringIO()
        self.aggressive: bool = aggressive
        self.__timeout: Optional[int] = timeout

        # Default headers
        self.__headers_get: Dict[str, str] = {  # get
            "Accept": "application/json",
            "User-Agent": "cainmagi/syncstream",
        }
        self.__headers = collections.ChainMap(  # post
            {
                "Content-Type": "application/json",
            },
            self.__headers_get,
        )

        # To be created when the first connection is established.
        self.__buffer_lock_: Optional[threading.Lock] = None
        self.__http_: Optional[SafePoolManager] = None
        self.__finalizer: Optional[weakref.finalize] = None

        # stdout/stderr configs
        self.__stdout: Optional[TextIO] = None
        self.__stderr: Optional[TextIO] = None

    def __enter__(self):
        """Enter the context, where stdout/stderr will be redirected to this object."""
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: types.TracebackType,
    ) -> None:
        """Exit the context, where stdout/stderr will be retrieved."""
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        self.__stdout = None
        self.__stderr = None
        return None

    @property
    def headers(self) -> ChainMap[str, str]:
        """Get the default headers (post) of the mirror."""
        return collections.ChainMap(dict(), self.__headers)

    @property
    def headers_get(self) -> ChainMap[str, str]:
        """Get the default headers (get) of the mirror."""
        return collections.ChainMap(dict(), self.__headers_get)

    @property
    def __http(self) -> SafePoolManager:
        """The threading lock for the buffer.

        This lock should not be exposed to users. It is used for ensuring that the
        temporary buffer of the mirror is thread-safe.
        """
        if self.__http_ is None:
            self.__http_ = SafePoolManager(
                retries=urllib3.util.Retry(connect=5, read=2, redirect=5),
                timeout=urllib3.util.Timeout(total=self.__timeout),
            )
            self.__finalizer = weakref.finalize(self, clean_http_manager, self.__http_)
        return self.__http_

    @property
    def __buffer_lock(self) -> threading.Lock:
        """The threading lock for the buffer.

        This lock should not be exposed to users. It is used for ensuring that the
        temporary buffer of the mirror is thread-safe.
        """
        if self.__buffer_lock_ is None:
            self.__buffer_lock_ = threading.Lock()
        return self.__buffer_lock_

    def clear(self) -> None:
        """Clear the temporary buffer.

        This method would clear the temporary buffer of the mirror. If the mirror works
        in the `aggresive` mode, the temporary buffer would not be used. In this case,
        this method would not exert any influences to the mirror.

        This method is thread-safe. Mirrors in different processes would not share the
        temporary buffer.
        """
        with self.__buffer_lock:
            self.__buffer.seek(0, os.SEEK_SET)
            self.__buffer.truncate(0)

    def new_line(self, check: bool = True) -> None:
        R"""Manually trigger a new line to the buffer. If the current stream is already
        a new line, do nothing.
        """
        with self.__buffer_lock:
            if self.__buffer.tell() > 0:
                self.__write("\n", check=check)

    def send_eof(self) -> None:
        """Send an EOF signal to the main buffer.

        The EOF signal is used for telling the main buffer flush the temporary buffer.
        Note that this method would not close the queue. The mirror could be reused for
        another program.
        """
        self.new_line()
        with self.__http.request(
            url=self.address,
            headers=self.headers,
            method="post",
            preload_content=False,
            body=json.dumps({"type": "close"}).encode(),
        ) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(
                    info.get(
                        "message",
                        "syncstream: Meet an unknown error on the service side.",
                    )
                )

    def send_error(self, obj_err: Exception) -> None:
        """Send the error object to the main buffer.

        The error object would be captured as an item of the storage in the main buffer.
        """
        self.new_line(check=False if isinstance(obj_err, StopIteration) else True)
        with self.__http.request(
            url=self.address,
            headers=self.headers,
            method="post",
            preload_content=False,
            body=json.dumps(
                {"type": "error", "data": GroupedMessage(obj_err).serialize()}
            ).encode(),
        ) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(
                    info.get(
                        "message",
                        "syncstream: Meet an unknown error on the service side.",
                    )
                )

    def send_warning(self, obj_warn: Warning) -> None:
        """Send the warning object to the main buffer.

        The warning object would be captured as an item of the storage in the main buffer.
        """
        self.new_line()
        with self.__http.request(
            url=self.address,
            headers=self.headers,
            method="post",
            preload_content=False,
            body=json.dumps(
                {"type": "warning", "data": GroupedMessage(obj_warn).serialize()}
            ).encode(),
        ) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(
                    info.get(
                        "message",
                        "syncstream: Meet an unknown error on the service side.",
                    )
                )

    def send_data(self, data: str) -> None:
        """Send the data to the main buffer.

        This method would fire a POST service of the main buffer, and send the str
        data.

        This method is used by other methods implicitly, and should not be used by
        users.

        Arguments:
            data: a str to be sent to the main buffer.
        """
        with self.__http.request(
            url=self.address,
            headers=self.headers,
            method="post",
            preload_content=False,
            body=json.dumps({"type": "str", "data": {"value": data}}).encode(),
        ) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(
                    info.get(
                        "message",
                        "syncstream: Meet an unknown error on the service side.",
                    )
                )

    def check_states(self) -> None:
        """Check the current buffer states.

        Currently, this method in only used for checking whether the service is closed.
        """
        is_closed = False
        with self.__http.request(
            url="{0}-state?{1}".format(
                self.address, urlencode({"state": "closed"}, encoding="utf-8")
            ),
            headers=self.headers_get,
            method="get",
            preload_content=False,
        ) as req:
            if req.status < 400:
                res = json.load(req)
                is_closed = res.get("data", None)
            else:
                info = json.load(req)
                raise ConnectionError(
                    info.get(
                        "message",
                        "syncstream: Meet an unknown error on the service side.",
                    )
                )
        if is_closed is True:
            raise StopIteration("syncstream: The mirror worker is terminated by users.")
        else:
            return

    def flush(self) -> None:
        """Flush the current written line stream."""
        with self.__buffer_lock:
            self.__buffer.flush()

    def read(self) -> str:
        """Read the current buffer.

        This method would only read the current bufferred values. If the property
        `aggressive` is `True`, the `read()` method would always return empty value.
        """
        with self.__buffer_lock:
            return self.__buffer.getvalue()

    def __write(self, data: str, check: bool = True) -> int:
        """The write() method without lock.

        This method is private and should not be used by users.
        """
        if check:
            self.check_states()
        message_lines = data.splitlines()
        if self.aggressive:
            self.send_data(data=data)
            return len(data)
        n_lines = len(message_lines)
        if (
            n_lines > 1
            or (n_lines == 1 and message_lines[0] == "")
            or is_end_line_break(data)
        ):  # A new line is triggerred.
            res = self.__buffer.write(data)
            self.send_data(data=self.__buffer.getvalue())
            self.__buffer.seek(0, os.SEEK_SET)
            self.__buffer.truncate(0)
            return res
        elif n_lines == 1:
            return self.__buffer.write(data)
        else:
            return 0

    def write(self, data: str) -> int:
        """Write the stream.

        The source data is the same as that of a text-based IO. If `aggressive` is
        `True`, each call of `write()` would make the stream value sent to the main
        buffer. If not, each time when `data` contains a line break, the stream value
        would be sent to the main buffer.

        The method is thread-safe, but the message synchronization is host-safe.

        Arguments
        ---------
        data: `str`
            The data that would be written in the stream.

        Returns
        -------
        #1: `int`
            Number of lines (i.e. the record items) that are written to the storage.
        """
        with self.__buffer_lock:
            return self.__write(data)


class LineHostBuffer(_LineBuffer[GroupedMessage]):
    R"""The host service provider for the line-based buffer.

    The rotating buffer with a maximal storage length. This buffer is the extended
    version of the basic `LineBuffer`. It is used in the case of multi-devices. It
    supports the one-host-multi-clients mode, and supports the syncholization by the
    web services. For example,
    ```python
    def f(address: str) -> None:
        buffer = LineHostMirror(address=address, timeout=5)
        with buffer:
            print('example')
        buffer.send_eof()

    pbuf = LineHostBuffer('/sync-stream', maxlen=10)
    pbuf.serve(api)

    @app.route(...)
    def another_service() -> None:
        address = 'http://localhost:5000/sync-stream'
        with multiprocessing.Pool(4) as p:
            p.map(f, tuple(address for _ in range(4)))
        print(pbuf.read())

    if __name__ == '__main__':
        app.run(...)  # Run the Flask service.
    ```

    Note that the entering of the service function may reset the stdout and stderr of
    the current process. Therefore, it is not recommended to use this buffer with
    single-thread or multi-thread cases. If users insist on doing that, each time the
    print function is used, the stream needs to be set.
    """

    def __init__(
        self,
        api_route: str = "/sync-stream",
        endpoint: Optional[str] = None,
        maxlen: int = 20,
    ) -> None:
        """Initialization.

        Arguments
        ---------
        api_route: `str`
            The address of the api.

        endpoint: `str | None`
            The endpoint of the api, if set None, would be inferred from the argument
            `"api"`.

        maxlen: `int`
            The maximal number of stored lines.
        """
        super().__init__(maxlen=maxlen, _data_type=GroupedMessage)
        if not isinstance(api_route, str) or api_route == "":
            raise TypeError(
                'syncstream: The argument "api_route" should be a non-empty str.'
            )
        self.api_route = api_route
        if endpoint is None:
            endpoint = api_route.lstrip("/").replace("/", ".")
        self.endpoint = endpoint
        self.__config_lock = threading.Lock()
        self.__state_lock = threading.Lock()
        self.__state = dict(closed=False)

    def read_serialized(
        self, size: Optional[int] = None
    ) -> Tuple[Union[str, SerializedMessage], ...]:
        """Read the records (serialized).

        It has the same functionalities of `read(...)`. However, all the data returned
        by this method has been serialized and compatible with jsonifying.

        This method should be used for providing query services.

        Arguments
        ---------
        size: `int | None`
            If set None, would return the whole storage.

            If set a int value, would return the last `size` items.

        Returns
        -------
        #1: `[str | SerializedMessage]`
            A sequence of fetched record items. Results are sorted in the FIFO order.
        """
        return tuple(
            (val if isinstance(val, str) else GroupedMessage.serialize(val))
            for val in self.read(size=size)
        )

    def serve(self, app: flask.Flask) -> None:
        """Provide the service of the host buffer.

        The service would be equipped as an independent thread. Each time the request
        is received, the service would be triggered, and the thread-safe results would
        be saved.

        Arguments:
            api: an instance of the `flask_restful.Api`.
        """
        rself = self
        super_rself = super()
        config_lock = self.__config_lock
        state_lock = self.__state_lock
        state = self.__state

        class BufferPost(MethodView):
            """The buffer service."""

            def post(self):
                """Accept the remote message item, and parse the results in the file."""
                if not request.is_json:
                    raise TypeError(
                        "syncstream: The request type of BufferPost.post needs to be "
                        "json."
                    )
                args = request.get_json()
                if not isinstance(args, collections.abc.Mapping):
                    raise TypeError(
                        "syncstream: The request data of BufferPost.post needs to be "
                        "mapping-like."
                    )
                dtype = str(args.get("type", "")).strip()
                with config_lock:
                    if dtype == "str":
                        data = args.get("data", None)
                        if isinstance(data, collections.abc.Mapping):
                            data = data.get("value", None)
                            if data is not None:
                                super_rself.write(str(data))
                    elif dtype in ("error", "warning"):
                        data = args.get("data", None)
                        if isinstance(data, collections.abc.Mapping):
                            rself.new_line()
                            data = GroupedMessage.deserialize(dict(data))
                    elif dtype == "close":
                        rself.new_line()
                    else:
                        raise TypeError(
                            "syncstream: The message type could not be recognized."
                        )
                    return {"message": "success"}, 201

            def get(self):
                """Get all message items from the storage."""
                args = request.args
                _number = args.get("n", None)
                if _number is None:
                    number = _number
                else:
                    try:
                        number = int(_number)
                    except ValueError as err:
                        raise ValueError(
                            "syncstream: The request data of BufferPost.get is not a "
                            "valid number. Given: {0}".format(_number)
                        ) from err
                with config_lock:
                    data = rself.read_serialized(size=number)
                return {"message": "success", "data": data}, 200

            def delete(self):
                """Delete all message items."""
                with config_lock:
                    rself.clear()
                return {"message": "success"}, 200

        class BufferStatePost(MethodView):
            """The service used for checking the buffer state."""

            def get(self):
                """Get the states of the buffer."""
                args = request.args
                name = str(args.get("state", "")).strip()
                if not name:
                    raise TypeError(
                        "syncstream: The request data of BufferStatePost.get does "
                        "not exist."
                    )
                with config_lock:
                    with state_lock:
                        res = state.get(name, None)
                return {"message": "success", "data": res}, 200

            def post(self):
                """Change the state of the buffer."""
                if not request.is_json:
                    raise TypeError(
                        "syncstream: The request type of BufferStatePost.post needs "
                        "to be json."
                    )
                args = request.get_json()
                if not isinstance(args, collections.abc.Mapping):
                    raise TypeError(
                        "syncstream: The request data of BufferStatePost.post needs "
                        "to be mapping-like."
                    )
                name = str(args.get("state", "")).strip()
                if not name:
                    raise TypeError(
                        "syncstream: The request data of BufferStatePost.get does "
                        "not exist."
                    )
                with config_lock:
                    with state_lock:
                        if name == "closed":
                            value = str(args.get("value")).casefold().strip()
                            state[name] = True if value == "true" else False
                return {"message": "success"}, 201

            def delete(self):
                """Reset the state of the buffer."""
                rself.reset_states()
                return {"message": "success"}, 200

        app.add_url_rule(
            self.api_route,
            endpoint=self.endpoint,
            view_func=BufferPost.as_view("buffer_post"),
        )
        app.add_url_rule(
            self.api_route + "-state",
            endpoint=self.endpoint + "-state",
            view_func=BufferStatePost.as_view("buffer_post"),
        )

    def write(self, data: str) -> NoReturn:
        """Write the records.

        This method should not be used. For instead, please use `self.mirror.write()`.

        Arguments
        ---------
        data: `str`
            The data that would be written in the stream.
        """
        raise NotImplementedError(
            "syncstream: Should not use this method, use "
            "`self.mirror.write()` for instead."
        )

    def stop_all_mirrors(self) -> None:
        """Send stop signals to all mirrors.

        This operation is used for terminating the mirrors safely. It does not
        guarantee that the processes would be closed instantly. Each time when the new
        message is written by the mirrors, a check would be triggered.

        If users want to use this method, please ensure that the `StopIteration` error
        is catched by the process. The error would not be sent back to the buffer.
        """
        with self.__state_lock:
            self.__state["closed"] = True

    def reset_states(self) -> None:
        """Reset the states of the buffer.

        This method should be used if the buffer needs to be reused.
        """
        with self.__state_lock:
            self.__state.clear()
            self.__state["closed"] = False
