# -*- coding: UTF-8 -*-
"""
Utilities
=========
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
The shared utilities for web services. This module is private and should not be
exposed to users.

The implementation of this module is mainly based on `urllib3`.
"""

import sys
import types

from typing import Union, Optional, Generic, TypeVar

try:
    from typing import Mapping
    from typing import Tuple, Type
except ImportError:
    from collections.abc import Mapping
    from builtins import tuple as Tuple, type as Type

from typing_extensions import Literal, Self

from packaging import version
from urllib3.poolmanager import PoolManager

if sys.version_info >= (3, 7):
    from urllib3._version import __version__ as urllib3_ver

    if version.parse(urllib3_ver) >= version.parse("2.0.0"):
        from urllib3.response import BaseHTTPResponse as URLLIBResponse
    else:
        from urllib3.response import HTTPResponse as URLLIBResponse
else:
    from urllib3.response import HTTPResponse as URLLIBResponse


__all__ = (
    "MethodApproved",
    "ReqLocApproved",
    "ReqFile",
    "SafeRequest",
    "SafePoolManager",
    "clean_http_manager",
    "close_request_session",
)


_TResponse = TypeVar("_TResponse", bound=URLLIBResponse)

MethodApproved = Literal[
    "get", "post", "head", "options", "delete", "put", "trace", "patch"
]
ReqLocApproved = Literal[
    "args",  # Always be in the query string
    "body",  # Usually be form
    "fields",  # Currently only used for files.
    "fields-form",  # A form that is put as a member of a field.
    "headers",  # Forwarded from headers directly.
    "cookies",  # Special headers, need to be pretreated by cookie-jars.
]
ReqFile = Union[Tuple[str, Union[str, bytes], str], Tuple[str, Union[str, bytes]]]


class SafeRequest(Generic[_TResponse]):
    """A wrapper for providing context for the urllib3.BaseHTTPResponse.
    This is a private class. Should not be used by users.
    """

    def __init__(self, request: _TResponse) -> None:
        self.request: _TResponse = request

    def __enter__(self) -> _TResponse:
        return self.request

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: types.TracebackType,
    ):
        self.request.release_conn()
        self.request.close()


class SafePoolManager(PoolManager):
    """A wrapped urllib3.PoolManager with context supported.
    This is a private class. Should not be used by users.
    """

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(
        self: Self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: types.TracebackType,
    ):
        self.clear()

    def request(
        self: Self,
        method: MethodApproved,
        url: str,
        fields: Optional[Mapping[str, Union[str, bytes, ReqFile]]] = None,
        headers: Optional[Mapping[str, str]] = None,
        **urlopen_kw
    ) -> SafeRequest[URLLIBResponse]:
        """Modified version of the `PoolManager.request(...)`
        This method provide the typehints that are not available in the original
        `urllib3` pacakge. The returned value is a wrapped `SafeRequest` ready for
        used as a context, not simply an `HTTPResponse` object.
        Arguments:
            method: The HTTP method of the request.
            url: The target URL of this request.
            fields: The multi-form fields to be sent, can be empty.
            headers: The HTTP headers of this request.
            **urlopen_kw: The other keywords will be forwarded to `urlopen(...)`.
        Returns:
            #1: A SafeRequest context object. Entering this context will provide the
                wrapped HTTPResponse returned by this method.
        """
        return SafeRequest(
            super().request(
                method=method, url=url, fields=fields, headers=headers, **urlopen_kw
            )
        )


def clean_http_manager(http: PoolManager) -> None:
    """A callback for the finializer, this function would be used for cleaning the
    http requests, if the connection does not need to exist.
    """
    http.clear()


def close_request_session(sess: URLLIBResponse) -> None:
    """A callback for the finializer, this function would be used for cleaning the
    requests session, if the connection does not need to exist.
    """
    sess.release_conn()
    sess.close()
