#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Tests: host-based synchronization.
# @ Test script for Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
#   fasterners 0.16+
# Test scripts of the module `host`.
################################################################
'''

import sys
import time
import warnings
import threading
import multiprocessing
import logging

try:
    from typing import Tuple
except ImportError:
    from builtins import tuple as Tuple

from werkzeug.serving import make_server, WSGIRequestHandler
import requests
import flask
from flask_restful import Api

import pytest

try:
    from syncstream import LineHostBuffer, LineHostMirror  # pylint: disable=import-error
except ImportError:
    pytest.skip('The requirements for the host module is not installed, the test is skipped.', allow_module_level=True)
from syncstream.base import GroupedMessage  # pylint: disable=import-error


def worker_writter(address: str) -> None:
    '''The worker for the thread-mode testing.
    '''
    hbuf = LineHostMirror(address=address)
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(10):
        time.sleep(0.1)
        sys.stdout = hbuf
        print('Thd: "{0}";'.format(thd_id), 'Line:', 'buffer', 'new', i)
    hbuf.send_eof()


def worker_writter_lite(address: str) -> None:
    '''The worker for the thread-mode testing (lite).
    This version only writes two lines.
    '''
    hbuf = LineHostMirror(address=address)
    try:
        thd_id = threading.get_native_id()
    except AttributeError:
        thd_id = threading.get_ident()  # Fall back to py37
    for i in range(2):
        time.sleep(0.1)
        sys.stdout = hbuf
        print('Thd: "{0}";'.format(thd_id), 'Line:', 'buffer', 'new', i)
    hbuf.send_eof()


def create_warn(catch: bool = False) -> None:
    '''Create a warn message by the stdlib. Different from the logging module,
    the messages created by this way could be catched by the process-safe
    line buffer.
    '''
    if catch:
        with warnings.catch_warnings(record=True):
            warnings.filterwarnings('error')
            warnings.warn('An example of python warning.', UserWarning)
    else:
        warnings.warn('An example of python warning.', UserWarning)


def worker_process(address: str) -> None:
    '''The worker for the process-mode testing.
    The process should be ended by a send_error() or a send_eof().
    Each end signal should be only sent by once.
    '''
    buffer = LineHostMirror(address=address)
    for i in range(10):
        time.sleep(0.01)
        sys.stdout = buffer
        print('Line:', 'buffer', 'new', i, end='\n')
    sys.stderr = buffer
    create_warn()
    try:
        create_warn(catch=True)
    except Warning as warn:
        buffer.send_warning(warn)
    try:
        raise TypeError('A test error.')
    except TypeError as err:
        buffer.send_error(err)
    else:
        buffer.send_eof()


def worker_process_lite(address: str) -> None:
    '''The worker for the process-mode testing (clear).
    The process only write two lines for each process.
    The process should be ended by a send_error() or a send_eof().
    Each end signal should be only sent by once.
    '''
    buffer = LineHostMirror(address=address)
    for i in range(2):
        time.sleep(0.01)
        sys.stdout = buffer
        print('Line:', 'buffer', 'new', i, end='\n')
    buffer.send_eof()


def worker_process_stop(address: str) -> None:
    '''The worker for the thread-mode testing (lite).
    The process used for testing the manually terminating.
    The process should be ended by a send_error() or a send_eof().
    Each end signal should be only sent by once.
    '''
    buffer = LineHostMirror(address=address)
    try:
        for i in range(10):
            time.sleep(0.1)
            sys.stdout = buffer
            print('Line:', 'buffer', 'new', i, end='\n')
            if i > 0:
                time.sleep(10.0)
    except Exception as error:  # pylint: disable=broad-except
        buffer.send_error(error)
    else:
        buffer.send_eof()


def create_test_api(name: str = 'api_name') -> Tuple[flask.Flask, Api]:
    app_ = flask.Flask(name)
    api = Api(app_)

    # Configure APIs.
    LineHostBuffer(api_route='/sync-stream', maxlen=10).serve(api)

    return app_, api


@pytest.fixture(scope='module')
def app() -> flask.Flask:
    app_, _ = create_test_api()

    return app_


@pytest.fixture(scope='module')
def temp_server(app: flask.Flask):
    @app.errorhandler(404)
    def page_not_found(error) -> dict:  # pylint: disable=unused-argument
        return {'message': '404 not found.', 'code': 'error-404'}, 404

    @app.route('/sync-stream/is-online', methods=('GET',))
    def is_online() -> dict:
        return {'message': 'success'}

    server = make_server('localhost', 5000, app)

    def run_app(server) -> None:
        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None
        server.serve_forever()

    app_thread = threading.Thread(target=run_app, args=(server, ))
    yield app_thread.start()

    server.shutdown()


def verify_online(address: str, retries: int = 5) -> None:
    '''Verify the online status of the service.
    Arguments:
        address: the service address.
        retries: the number of retries for the verification.
    '''
    for _ in range(retries):
        res = requests.get('{addr}/is-online'.format(addr=address), timeout=2.0)
        if res.status_code < 400:
            if res.json()['message'] == 'success':
                return
    raise ConnectionError('test.connect: Fail to connect to the server.')


class TestHost:
    '''Test the host module of the package.'''

    @staticmethod
    def show_messages(log: logging.Logger, messages: dict) -> None:
        '''Show the messages from the buffer.'''
        for i, item in enumerate(messages):
            if isinstance(item, dict) and item.get('/is_syncsdata', False):
                item = GroupedMessage.deserialize(item)
                if item.type == 'error':
                    log.critical('%s', '{0:02d}: {1}'.format(i, item))
                elif item.type == 'warning':
                    log.warning('%s', '{0:02d}: {1}'.format(i, item))
                else:
                    log.info('%s', '{0:02d}: {1}'.format(i, item))
            else:
                log.info('%s', '{0:02d}: {1}'.format(i, item))

    def test_host_buffer(self, temp_server) -> None:
        '''Test the host.LineHostBuffer in the single thread mode.'''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        hbuf = LineHostMirror(address=address)
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Write buffer.
        sys.stdout = hbuf
        print('Hello!')
        sys.stdout = hbuf
        print('Multiple', 'sep', 'example')
        sys.stdout = hbuf
        print('An example of \n splitted message.\n')
        sys.stdout = hbuf
        print('An extra message.')
        sys.stdout = hbuf
        print('An example of long and unicode message: I/O???????????????????????????????????? IOBase ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????? UnsupportedOperation ???\n???????????? RawIOBase ??? IOBase ?????????????????????????????????????????????????????? RawIOBase ????????? FileIO ????????????????????????????????????????????????\n???????????? BufferedIOBase ????????? IOBase ?????????????????????????????? RawIOBase ??????????????????????????? BufferedWriter ??? BufferedReader ??? BufferedRWPair ?????????????????????????????????????????????????????????????????? BufferedRandom ???????????????????????????????????????????????? BufferedIOBase ?????????????????? BytesIO ????????????????????????\n???????????? TextIOBase ????????? IOBase ?????????????????????????????????????????????????????????????????????????????? TextIOWrapper ????????? TextIOBase ???????????????????????? BufferedIOBase ???????????????????????????????????? StringIO ????????????????????????\n?????????????????????????????????????????? open() ????????????????????????????????????')
        sys.stdout = hbuf
        print('Multiple', 'sep', 'example', end='')
        hbuf.send_eof()
        sys.stdout = sys.__stdout__

        # Check the validity of the buffer results.
        res = requests.get(url=address, params={'n': 4})
        messages = res.json()['data']
        assert messages[0] == '???????????? BufferedIOBase ????????? IOBase ?????????????????????????????? RawIOBase ??????????????????????????? BufferedWriter ??? BufferedReader ??? BufferedRWPair ?????????????????????????????????????????????????????????????????? BufferedRandom ???????????????????????????????????????????????? BufferedIOBase ?????????????????? BytesIO ????????????????????????'
        assert messages[1] == '???????????? TextIOBase ????????? IOBase ?????????????????????????????????????????????????????????????????????????????? TextIOWrapper ????????? TextIOBase ???????????????????????? BufferedIOBase ???????????????????????????????????? StringIO ????????????????????????'
        assert messages[2] == '?????????????????????????????????????????? open() ????????????????????????????????????'
        assert messages[3] == 'Multiple sep example'

        # Show the buffer results.
        res = requests.get(url=address)
        messages = res.json()['data']
        self.show_messages(log, messages)
        assert len(messages) == 10

    def test_host_thread(self, temp_server) -> None:
        '''Test the host.LineHostBuffer in the multi-thread mode.'''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Write buffer.
        thd_pool = list()
        for _ in range(4):
            thd = threading.Thread(target=worker_writter, args=(address, ))
            thd_pool.append(thd)
        for thd in thd_pool:
            thd.start()
        for thd in thd_pool:
            thd.join()
        sys.stdout = sys.__stdout__

        # Show the buffer results.
        res = requests.get(url=address)
        messages = res.json()['data']
        self.show_messages(log, messages)
        assert len(messages) == 10

    def test_host_process(self, temp_server) -> None:
        '''Test the host.LineHostBuffer in the multi-process mode.'''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Write buffer.
        with multiprocessing.Pool(4) as pool:
            pool.map(worker_process, tuple(address for _ in range(4)))
            log.debug('The main stdout is not influenced.')
        log.debug('Confirm: The main stdout is not influenced.')

        # Show the buffer results.
        res = requests.get(url=address)
        messages = res.json()['data']
        self.show_messages(log, messages)
        assert len(messages) == 10

    def test_host_thread_clear(self, temp_server) -> None:
        '''Test the host.LineHostBuffer.clear() in the multi-thread mode.
        '''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Clear, then check message items, should be 0 now.
        res = requests.delete(url=address)
        assert res.json()['message'] == 'success'
        log.debug('Clear all messages.')
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 0

        def write_2_threads() -> None:
            thd_pool = list()
            for _ in range(2):
                thd = threading.Thread(target=worker_writter_lite, args=(address, ))
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
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 8

        # Clear, then check message items, should be 0 now.
        res = requests.delete(url=address)
        assert res.json()['message'] == 'success'
        log.debug('Clear all messages.')
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 0

        # Write buffer with a clear.
        write_2_threads()
        sys.stdout = sys.__stdout__
        res = requests.delete(url=address)
        assert res.json()['message'] == 'success'
        log.debug('Clear all messages.')
        write_2_threads()
        sys.stdout = sys.__stdout__

        # Check message items, should be 4 now.
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 4

    def test_host_process_clear(self, temp_server) -> None:
        '''Test the host.LineHostBuffer.clear() in the multi-process mode.
        '''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Clear, then check message items, should be 0 now.
        res = requests.delete(url=address)
        assert res.json()['message'] == 'success'
        log.debug('Clear all messages.')
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 0

        # Write buffer.
        with multiprocessing.Pool(2) as pool:
            pool.map(worker_process_lite, tuple(address for _ in range(2)))
            pool.map(worker_process_lite, tuple(address for _ in range(2)))

        # Check message items, should be 8 now.
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 8

        # Clear, then check message items, should be 0 now.
        res = requests.delete(url=address)
        assert res.json()['message'] == 'success'
        log.debug('Clear all messages.')
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 0

        # Write buffer with a clear.
        with multiprocessing.Pool(2) as pool:
            pool.map(worker_process_lite, tuple(address for _ in range(2)))
            res = requests.delete(url=address)
            assert res.json()['message'] == 'success'
            log.debug('Clear all messages.')
            pool.map(worker_process_lite, tuple(address for _ in range(2)))

        # Check message items, should be 4 now.
        res = requests.get(url=address)
        messages = res.json()['data']
        assert len(messages) == 4

    def test_host_process_stop(self, temp_server) -> None:
        '''Test the host.LineHostBuffer.stop_all_mirrors() in the multi-process mode.'''
        log = logging.getLogger('test_host')
        address = 'http://localhost:5000/sync-stream'
        verify_online(address)
        log.info('Successfully connect to the remote server.')

        # Write buffer.
        log.debug('Start to write the buffer.')
        with multiprocessing.Pool(4) as pool:
            workers = pool.map_async(worker_process_stop, tuple(address for _ in range(4)))
            time.sleep(1.0)
            log.debug('Send the close signal to the sub-processes.')
            res = requests.post(url=address + '-state', json={'state': 'closed', 'value': 'true'})
            assert res.status_code < 400
            workers.wait()

        res = requests.delete(url=address + '-state')
        assert res.status_code < 400

        # Show the buffer results.
        res = requests.get(url=address)
        messages = res.json()['data']
        log.critical(messages)
        self.show_messages(log, messages)
