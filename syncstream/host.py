#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Host-based stream synchronization.
# @ Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
#   fasteners 0.16+
# This module is based on Flask and urllib3. The message is
# collected by a Flask service, and the stream is redirected
# to a web request handle.
################################################################
'''

import os
import io
import weakref
import json
import threading

from typing import NoReturn

import urllib3

from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser

from .base import is_end_line_break, GroupedMessage
from .webtools import SafePoolManager, SafeRequest, clean_http_manager
from .mproc import LineBuffer


class LineHostMirror:
    '''The mirror for the host-safe line-based buffer.
    This mirror is initialized by `LineProcBuffer`, and would be used for managing the lines
    written to the buffer.
    '''
    def __init__(self, address: str, aggressive: bool = False, timeout: int = None) -> None:
        '''Initialization
        Arguments:
            address: the address of the LineHostBuffer. The redirected stream would send
                     the messages to this address.
            aggressive: the aggressive mode. If enabled, each call for the `write()` method
                        would trigger the service synchronization. Otherwise, the
                        synchronization would be triggered when a new line is written.
            timeout: the timeout of the web syncholizing events. If not set, the
                     synchronization would block the current process.
        '''
        if not isinstance(address, str) or address == '':
            raise TypeError('The argument "address" should be a non-empty str.')
        self.address = address
        self.__buffer = io.StringIO()
        self.aggressive = aggressive
        self.__timeout = timeout

        # Default headers
        self.__headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'cainmagi/syncstream'
        }

        # To be created when the first connection is established.
        self.__buffer_lock_ = None
        self.__http_ = None
        self.__finalizer = None

    @property
    def headers(self) -> dict:
        '''Get the default headers of the mirror.'''
        return self.__headers.copy()

    @property
    def __http(self) -> SafePoolManager:
        '''The threading lock for the buffer.
        This lock should not be exposed to users. It is used for ensuring that the
        temporary buffer of the mirror is thread-safe.
        '''
        if self.__http_ is None:
            self.__http_ = SafePoolManager(
                retries=urllib3.util.Retry(connect=5, read=2, redirect=5),
                timeout=urllib3.util.Timeout(total=self.__timeout)
            )
            self.__finalizer = weakref.finalize(self, clean_http_manager, self.__http_)
        return self.__http_

    @property
    def __buffer_lock(self) -> threading.Lock:
        '''The threading lock for the buffer.
        This lock should not be exposed to users. It is used for ensuring that the
        temporary buffer of the mirror is thread-safe.
        '''
        if self.__buffer_lock_ is None:
            self.__buffer_lock_ = threading.Lock()
        return self.__buffer_lock_

    def new_line(self) -> None:
        R'''Manually trigger a new line to the buffer. If the current stream is already
        a new line, do nothing.
        '''
        with self.__buffer_lock:
            if self.__buffer.tell() > 0:
                self.__write('\n')

    def send_eof(self) -> None:
        '''Send an EOF signal to the main buffer.
        The EOF signal is used for telling the main buffer stop to wait. Note that this
        method would not close the queue. The mirror could be reused for another program.
        '''
        self.new_line()
        with SafeRequest(self.__http.request(
            url=self.address, headers=self.headers, method='POST',
            preload_content=False, body=json.dumps({'type': 'close'}).encode()
        )) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(info.get('message', 'Meet an unknown error on the service side.'))

    def send_error(self, obj_err: Exception) -> None:
        '''Send the error object to the main buffer.
        The error object would be captured as an item of the storage in the main buffer.
        '''
        self.new_line()
        with SafeRequest(self.__http.request(
            url=self.address, headers=self.headers, method='POST',
            preload_content=False, body=json.dumps({'type': 'error', 'data': GroupedMessage(obj_err).serialize()}).encode()
        )) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(info.get('message', 'Meet an unknown error on the service side.'))

    def send_warning(self, obj_warn: Warning) -> None:
        '''Send the warning object to the main buffer.
        The warning object would be captured as an item of the storage in the main buffer.
        '''
        self.new_line()
        with SafeRequest(self.__http.request(
            url=self.address, headers=self.headers, method='POST',
            preload_content=False, body=json.dumps({'type': 'warning', 'data': GroupedMessage(obj_warn).serialize()}).encode()
        )) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(info.get('message', 'Meet an unknown error on the service side.'))

    def send_data(self, data: str) -> None:
        '''Send the data to the main buffer.
        This method is equivalent to call the main buffer (LineProcBuffer) by the following
        method protected by host-safe synchronization:
        ```python
        pbuf.write(data)
        ```
        This method is used by other methods implicitly, and should not be used by users.
        Arguments:
            data: a str to be sent to the main buffer.
        '''
        with SafeRequest(self.__http.request(
            url=self.address, headers=self.headers, method='POST',
            preload_content=False, body=json.dumps({'type': 'str', 'data': {'value': data}}).encode()
        )) as req:
            if req.status < 400:
                return
            else:
                info = json.load(req)
                raise ConnectionError(info.get('message', 'Meet an unknown error on the service side.'))

    def flush(self) -> None:
        '''Flush the current written line stream.
        '''
        with self.__buffer_lock:
            self.__buffer.flush()

    def read(self) -> str:
        '''Read the current buffer.
        This method would only read the current bufferred values. If the property
        `aggressive` is `True`, the `read()` method would always return empty value.
        '''
        with self.__buffer_lock:
            return self.__buffer.getvalue()

    def __write(self, data: str) -> int:
        '''The write() method without lock.
        This method is private and should not be used by users.
        '''
        message_lines = data.splitlines()
        if self.aggressive:
            self.send_data(data=data)
            return len(data)
        n_lines = len(message_lines)
        if n_lines > 1 or (n_lines == 1 and message_lines[0] == '') or is_end_line_break(data):  # A new line is triggerred.
            res = self.__buffer.write(data)
            self.send_data(data=self.__buffer.getvalue())
            self.__buffer.seek(0, os.SEEK_SET)
            self.__buffer.truncate(0)
            return res
        elif n_lines == 1:
            return self.__buffer.write(data)

    def write(self, data: str) -> int:
        '''Write the stream.
        The source data is the same as that of a text-based IO. If `aggressive` is `True`,
        each call of `write()` would make the stream value sent to the main buffer. If not,
        each time when `data` contains a line break, the stream value would be sent to
        the main buffer.
        The method is thread-safe, but the message synchronization is host-safe.
        Arguments:
            data: the data that would be written in the stream.
        '''
        with self.__buffer_lock:
            self.__write(data)


class LineHostBuffer(LineBuffer):
    '''The host service provider for the line-based buffer.
    The rotating buffer with a maximal storage length. This buffer is the extended version of
    the basic `LineBuffer`. It is used for the case of multi-processing. Use the shared queue
    of this buffer to ensure the synchronization among processes. For example,
    ```python
    def f(address):
        buffer = LineHostMirror(address=address, timeout=5)
        sys.stdout = buffer
        print('example')
        buffer.send_eof()

    pbuf = LineHostBuffer('/sync-stream', maxlen=10)
    pbuf.serve(api)

    @app.route(...)
    def another_service():
        address = 'http://localhost:5000/sync-stream'
        with multiprocessing.Pool(4) as p:
            p.map_async(f, tuple(address for _ in range(4))))
        print(pbuf.read())

    if __name__ == '__main__':
        app.run(...)  # Run the Flask service.
    ```
    Note that the entering of the service function may reset the stdout and stderr of the
    current process. Therefore, it is not recommended to use this buffer with single-thread
    or multi-thread cases. If users insist on doing that, each time the print function is
    used, the stream needs to be set.
    '''
    def __init__(self, api_route='/sync-stream', endpoint=None, maxlen: int = 20) -> None:
        '''Initialization.
        Arguments:
            api_route: the address of the api.
            endpoint: the endpoint of the api, if set None, would be inferred from the
                      argument "api".
            maxlen: the maximal number of stored lines.
        '''
        super().__init__(maxlen=maxlen)
        if not isinstance(api_route, str) or api_route == '':
            raise TypeError('The argument "api_route" should be a non-empty str.')
        self.api_route = api_route
        if endpoint is None:
            endpoint = api_route.lstrip('/').replace('/', '.')
        self.endpoint = endpoint
        self.p_post = RequestParser()
        self.p_post.add_argument('type', type=str, required=True, help='The type of the message item should be a str.')
        self.p_post.add_argument('data', type=dict, default=dict(), help='The data of the message item should be a dict.')
        self.p_get = RequestParser()
        self.p_get.add_argument('n', type=int, default=None, help='The number of message item should be a int.')
        self.__config_lock = threading.Lock()

    def serve(self, api: Api) -> bool:
        '''Provide the service of the host buffer.
        The service would be equipped as an independent thread. Each time the request
        is received, the service would be triggered, and the thread-safe results would
        be saved.
        Arguments:
            api: an instance of the `flask_restful.Api`.
        '''
        rself = self
        super_rself = super()
        config_lock = self.__config_lock

        class BufferPost(Resource):
            '''The buffer service.'''
            def post(self):
                '''Accept the remote message item, and parse the results in the file.
                '''
                args = rself.p_post.parse_args()
                dtype = args.get('type')
                with config_lock:
                    if dtype == 'str':
                        data = args.get('data', None)
                        if data is not None:
                            data = data.get('value', None)
                            if data is not None:
                                super_rself.write(data)
                    elif dtype in ('error', 'warning'):
                        data = args.get('data', None)
                        if data is not None:
                            rself.storage.append(data)
                    elif dtype == 'close':
                        pass
                    else:
                        raise TypeError('The message type could not be recognized.')
                    return {'message': 'success'}, 202

            def get(self):
                '''Get all message items from the storage.
                '''
                args = rself.p_get.parse_args()
                number = args.get('n')
                with config_lock:
                    data = rself.read(size=number)
                return {'message': 'success', 'data': data}, 200

            def delete(self):
                '''Delete all message items.
                '''
                with config_lock:
                    rself.storage.clear()
                    rself.last_line.seek(0, os.SEEK_SET)
                    rself.last_line.truncate(0)
                return {'message': 'success'}, 200

        api.add_resource(BufferPost, self.api_route, endpoint=self.endpoint)

    def write(self, data: str) -> NoReturn:
        '''Write the records.
        This method should not be used. For instead, please use self.mirror.write().
        Arguments:
            data: the data that would be written in the stream.
        '''
        raise NotImplementedError('sync-stdout: Should not use this method, use '
                                  '`self.mirror.write()` for instead.')
