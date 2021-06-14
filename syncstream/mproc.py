#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Multiprocessing based synchronization.
# @ Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
# The base module for the message synchronization. It is totally
# based on the stdlib of python.
# This module should be only used for synchronizing messages
# between threads and processes on the same device.
################################################################
'''

import os
import io
import collections
import threading
import queue
import multiprocessing


from typing import NoReturn
try:
    from typing import Tuple, Sequence
except ImportError:
    from builtins import tuple as Tuple
    from collections.abc import Sequence

from .base import is_end_line_break, GroupedMessage


class LineBuffer:
    '''The basic line-based buffer handle.
    This buffer provides a rotating item stroage for the text-based stream. The text is stored not
    by length, but by lines. The maximal line number of the storage is limited.
    '''
    def __init__(self, maxlen: int = 20) -> None:
        '''Initialization.
        Arguments:
            maxlen: the maximal number of stored lines.
        '''
        if not isinstance(maxlen, int) or maxlen < 1:
            raise TypeError('syncstream: The argument "maxlen" should be a positive integer.')
        self.storage = collections.deque(maxlen=maxlen)
        self.last_line = io.StringIO()
        self.__last_line_lock = threading.Lock()

    def clear(self) -> None:
        '''Clear the whole buffer.
        This method would clear the storage and the last line stream of this buffer. However,
        it would not clear any mirrors or copies of this object. This method is thread-safe
        and should always success.
        '''
        with self.__last_line_lock:
            self.last_line.seek(0, os.SEEK_SET)
            self.last_line.truncate(0)
        self.storage.clear()

    def new_line(self) -> None:
        R'''Manually trigger a new line to the buffer. If the current stream is already
        a new line, do nothing.
        This method is equivalent to
        ```python
        if self.last_line.tell() > 0:
            write('\n')
        ```
        '''
        with self.__last_line_lock:
            if self.last_line.tell() > 0:
                self.__write('\n')

    def flush(self) -> None:
        '''Flush the current written line stream.
        '''
        with self.__last_line_lock:
            self.last_line.flush()

    def parse_lines(self, lines: Sequence[str]) -> None:
        '''Parse the lines.
        This method would be triggered when the new lines are written by `write()` method.
        The default behavior is adding the item into the storage.
        Users could inherit this method and override it with their customized parsing method,
        like regular expression searching.
        Arguments:
            lines: the new lines to be added into the stroage.
        '''
        self.storage.extend(lines)

    def read(self, size: int = None) -> Tuple[str]:
        '''Read the records.
        Fetch the stored record items from the buffer. Using the `read()` method is thread-safe
        and would not influence the cursor of `write()` method.
        If the current written line is not blank, the `read()` method would regard it as the
        last record item.
        Arguments:
            size: if set None, would return the whole storage.
                  if set a int value, would return the last `size` items.
        '''
        with self.__last_line_lock:
            has_last_line = self.last_line.tell() > 0
            n_lines = len(self.storage)
            if size is None:
                if has_last_line:
                    if n_lines > 0:
                        value = self.storage.popleft()
                        results = (*self.storage, self.last_line.getvalue())
                        self.storage.appendleft(value)
                    else:
                        results = (self.last_line.getvalue(), )
                    return results
                else:
                    return tuple(self.storage)
            elif size > 0:
                is_storage_popped = has_last_line and n_lines > 0
                if is_storage_popped:
                    preserved_value = self.storage.popleft()
                    size -= 1
                results = list()
                n_read = min(size, n_lines)
                if n_read > 0:
                    self.storage.rotate(n_read)
                for _ in range(n_read):
                    value = self.storage.popleft()
                    results.append(value)
                    self.storage.append(value)
                if has_last_line:
                    results.append(self.last_line.getvalue())
                    if is_storage_popped:
                        self.storage.appendleft(preserved_value)
                return tuple(results)

    def __write(self, data: str) -> int:
        '''The write() method without lock.
        This method is private and should not be used by users.
        '''
        message_lines = data.splitlines()
        n_lines = len(message_lines)
        if n_lines == 1 and message_lines[0] == '':
            self.parse_lines((self.last_line.getvalue(), ))
            self.last_line.seek(0, os.SEEK_SET)
            self.last_line.truncate(0)
            return 1
        elif is_end_line_break(data):
            message_lines.append('')
            n_lines += 1
        if n_lines > 1:
            message_lines[0] = self.last_line.getvalue() + message_lines[0]
            last_line = message_lines.pop()
            self.parse_lines(message_lines)
            self.last_line.seek(0, os.SEEK_SET)
            self.last_line.truncate(0)
            return self.last_line.write(last_line)
        elif n_lines == 1:
            return self.last_line.write(message_lines[0])

    def write(self, data: str) -> int:
        '''Write the records.
        The source data is the same as that of a text-based IO. Each time when `data` contains
        a line break, a new record item would be pushed in the storage. The `write()` method
        is thread-safe.
        Arguments:
            data: the data that would be written in the stream.
        '''
        with self.__last_line_lock:
            return self.__write(data)


class LineProcMirror:
    '''The mirror for the process-safe line-based buffer.
    This mirror is initialized by `LineProcBuffer`, and would be used for managing the lines
    written to the buffer.
    '''
    def __init__(self, q_maxsize: int = 0, aggressive: bool = False, timeout: float = None,
                 _queue: queue.Queue = None, _state: dict = None, _state_lock: threading.Lock = None) -> None:
        '''Initialization
        Arguments:
            q_maxsize: the `maxsize` of the queue. Use 0 means no limitation. A size limited
                       queue is recommended for protecting the memory.
            aggressive: the aggressive mode. If enabled, each call for the `write()` method
                        would trigger the process synchronization. Otherwise, the
                        synchronization would be triggered when a new line is written.
            timeout: the timeout of the process syncholizing events. If not set, the
                     synchronization would block the current process.
        Private arguments:
            _queue: the queue used for handling the message flow. If not set, would be
                    created by multiprocessing.Queue(). A recommended way is to set
                    this value by multiprocessing.Manager(). In this case, `q_maxsize`
                    would not be used.
            _state, _state_lock: required for getting the buffer states. If not set, would
                                 not turn on the stop signal.
        '''
        self.__buffer = io.StringIO()
        self.__buffer_lock_ = None
        self.aggressive = aggressive
        self.__timeout = timeout
        self.__block = timeout is None
        if _queue is None:
            self.__queue = multiprocessing.Queue(maxsize=q_maxsize)
        else:
            self.__queue = _queue
        if _state is not None and _state_lock is not None:
            self.__state_lock = _state_lock
            self.__state = _state
        else:
            self.__state_lock = None

    @property
    def __buffer_lock(self) -> threading.Lock:
        '''The threading lock for the buffer.
        This lock should not be exposed to users. It is used for ensuring that the
        temporary buffer of the mirror is thread-safe.
        '''
        if self.__buffer_lock_ is None:
            self.__buffer_lock_ = threading.Lock()
        return self.__buffer_lock_

    def clear(self) -> None:
        '''Clear the temporary buffer.
        This method would clear the temporary buffer of the mirror. If the mirror works
        in the `aggresive` mode, the temporary buffer would not be used. In this case,
        this method would not exert any influences to the mirror.
        This method is thread-safe. Mirrors in different processes would not share the
        temporary buffer. Note that the shared queue would not be cleared by this
        method.
        '''
        with self.__buffer_lock:
            self.__buffer.seek(0, os.SEEK_SET)
            self.__buffer.truncate(0)

    def new_line(self) -> None:
        R'''Manually trigger a new line to the buffer. If the current stream is already
        a new line, do nothing.
        '''
        with self.__buffer_lock:
            if self.__buffer.tell() > 0:
                self.__write('\n')

    @property
    def timeout(self) -> int:
        '''The time out of the process synchronization.
        '''
        return self.__timeout

    @timeout.setter
    def timeout(self, timeout: int = None) -> None:
        '''Setter for the property timeout.
        '''
        self.__timeout = timeout
        self.__block = timeout is None

    def send_eof(self) -> None:
        '''Send an EOF signal to the main buffer.
        The EOF signal is used for telling the main buffer stop to wait. Note that this
        method would not close the queue. The mirror could be reused for another program.
        '''
        self.new_line()
        self.__queue.put(
            {'type': 'close', 'data': None},
            block=self.__block, timeout=self.__timeout
        )

    def send_error(self, obj_err: Exception) -> None:
        '''Send the error object to the main buffer.
        The error object would be captured as an item of the storage in the main buffer.
        '''
        self.new_line()
        self.__queue.put(
            {'type': 'error', 'data': GroupedMessage(obj_err)},
            block=self.__block, timeout=self.__timeout
        )

    def send_warning(self, obj_warn: Warning) -> None:
        '''Send the warning object to the main buffer.
        The warning object would be captured as an item of the storage in the main buffer.
        '''
        self.new_line()
        self.__queue.put(
            {'type': 'warning', 'data': GroupedMessage(obj_warn)},
            block=self.__block, timeout=self.__timeout
        )

    def send_data(self, data: str) -> None:
        '''Send the data to the main buffer.
        This method is equivalent to call the main buffer (LineProcBuffer) by the following
        method protected by process-safe synchronization:
        ```python
        pbuf.write(data)
        ```
        This method is used by other methods implicitly, and should not be used by users.
        Arguments:
            data: a str to be sent to the main buffer.
        '''
        self.__queue.put(
            {'type': 'str', 'data': data},
            block=self.__block, timeout=self.__timeout
        )

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
        try:
            if self.__state_lock is not None:
                with self.__state_lock:
                    is_closed = self.__state.get('closed', False)
                    if is_closed:
                        raise StopIteration('syncstream: The sub-process is terminated by users.')
        except queue.Empty:
            pass
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
        The method is thread-safe, but the message synchronization is process-safe.
        Arguments:
            data: the data that would be written in the stream.
        '''
        with self.__buffer_lock:
            return self.__write(data)


class LineProcBuffer(LineBuffer):
    '''The process-safe line-based buffer.
    The rotating buffer with a maximal storage length. This buffer is the extended version of
    the basic `LineBuffer`. It is used for the case of multi-processing. Use the shared queue
    of this buffer to ensure the synchronization among processes. For example,
    ```python
    def f(buffer):
        sys.stdout = buffer
        print('example')
        buffer.send_eof()
    if __name__ == '__main__':
        pbuf = LineProcBuffer(maxlen=10)
        with multiprocessing.Pool(4) as p:
            p.map_async(f, tuple(pbuf.mirror for _ in range(4)))
            pbuf.wait()
        print(pbuf.read())
    ```
    '''
    def __init__(self, maxlen: int = 20) -> None:
        '''Initialization.
        Arguments:
            maxlen: the maximal number of stored lines.
        '''
        super().__init__(maxlen=maxlen)
        self.__manager = multiprocessing.Manager()
        self.__state = self.__manager.dict(closed=False)
        self.__state_lock = self.__manager.Lock()  # pylint: disable=no-member
        self.__mirror = LineProcMirror(q_maxsize=2 * maxlen, aggressive=False, timeout=None, _queue=self.__manager.Queue(), _state=self.__state, _state_lock=self.__state_lock)
        self.n_mirrors = 0
        self.__config_lock = threading.Lock()

    @property
    def mirror(self) -> LineProcMirror:
        '''Get the mirror of this buffer. The buffer should not be used in sub-processes
        directly. Use `self.mirror` to provide the process-safe mirror of the buffer.
        This property could not be modified after the initialization.
        '''
        self.n_mirrors += 1
        return self.__mirror

    def stop_all_mirrors(self) -> None:
        '''Send stop signals to all mirrors.
        This operation is used for terminating the sub-processes safely. It does not
        guarantee that the processes would be closed instantly. Each time when the new
        message is written by the sub-processes, a check would be triggered.
        If users want to use this method, please ensure that the StopIteration error
        is catched by the process. The error would not be catched automatically. If
        users do not catch the error, the main process would stuck at `wait()`.
        '''
        with self.__state_lock:
            self.__state['closed'] = True

    def reset_states(self) -> None:
        '''Reset the states of the buffer.
        This method should be used if the buffer needs to be reused.
        '''
        with self.__state_lock:
            self.__state.clear()
            self.__state['closed'] = False

    def __check_close(self) -> bool:
        '''Check whether to finish the `wait()` method.
        This method would be used when receiving a closing signal.
        This method is private and should not be used by users.
        Note that this method is always triggered in the config_lock.
        '''
        self.n_mirrors -= 1
        if self.n_mirrors > 0:
            return True
        else:
            return False

    def receive(self) -> bool:
        '''Receive one item from the mirror.
        This method would fetch one item from the process-saft queue, and write the results
        in the thread-safe buffer.
        '''
        with self.__config_lock:
            data = self.__mirror._LineProcMirror__queue.get()  # pylint: disable=protected-access
            dtype = data['type']
            if dtype == 'str':
                super().write(data['data'])
                return True
            elif dtype == 'error':
                obj = data['data']
                self.storage.append(obj)
                return self.__check_close()
            elif dtype == 'warning':
                obj = data['data']
                self.storage.append(obj)
                return True
            elif dtype == 'close':
                return self.__check_close()
            return False

    def wait(self) -> None:
        '''Wait the mirror until the close signal is received.
        '''
        while self.receive():
            pass

    def write(self, data: str) -> NoReturn:
        '''Write the records.
        This method should not be used. For instead, please use self.mirror.write().
        Arguments:
            data: the data that would be written in the stream.
        '''
        raise NotImplementedError('syncstream: Should not use this method, use '
                                  '`self.mirror.write()` for instead.')
