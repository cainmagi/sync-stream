#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Tools used for web connections and services.
# @ Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
#   fasteners 0.16+
# This module contains the basic tools for the host module,
# and would be only used by the host module.
################################################################
'''

import sys
import types

import urllib3


class StdoutWrapper:
    '''A wrapper for ensuring that the stdout is always directed to the
    same position.
    '''
    def __init__(self):
        self.__stdout = sys.stdout
        self.__stderr = sys.stderr
        self.__stdout_ = None
        self.__stderr_ = None

    def __enter__(self):
        self.__stdout_ = sys.stdout
        self.__stderr_ = sys.stderr
        sys.stdout = self.__stdout
        sys.stderr = self.__stderr
        return

    def __exit__(self, exc_type: type, exc_value: Exception, exc_traceback: types.TracebackType) -> None:
        sys.stdout = self.__stdout_
        sys.stderr = self.__stderr_


class SafePoolManager(urllib3.PoolManager):
    '''A wrapped urllib3.PoolManager with context supported.
    This is a private class. Should not be used by users.
    '''
    def __enter__(self):
        return self

    def __exit__(self, exc_type: type, exc_value: Exception, exc_traceback: types.TracebackType) -> None:
        self.clear()


class SafeRequest:
    '''A wrapper for providing context for the urllib3.HTTPResponse.
    This is a private class. Should not be used by users.
    '''
    def __init__(self, request: urllib3.HTTPResponse) -> None:
        self.request = request

    def __enter__(self) -> urllib3.HTTPResponse:
        return self.request

    def __exit__(self, exc_type: type, exc_value: Exception, exc_traceback: types.TracebackType) -> None:
        self.request.release_conn()


def clean_http_manager(http: urllib3.HTTPSConnectionPool) -> None:
    '''A callback for the finializer, this function would be used for cleaning the http
    requests, if the connection does not need to exist.
    '''
    http.clear()


def close_request_session(sess: urllib3.PoolManager) -> None:
    '''A callback for the finializer, this function would be used for cleaning the requests
    session, if the connection does not need to exist.
    '''
    sess.close()
