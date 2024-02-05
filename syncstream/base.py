# -*- coding: UTF-8 -*-
"""
Basic tools
===========
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
This module contains shared basic tools for different modules.
"""

import types
import traceback
import collections.abc
import contextlib

from typing import Union, Optional, Any, Generic, TypeVar, cast

try:
    from typing import Sequence
    from typing import Tuple, Type
except ImportError:
    from collections.abc import Sequence
    from builtins import tuple as Tuple, type as Type

from typing_extensions import Literal, Protocol, TypedDict, TypeGuard, Self


__all__ = (
    "is_end_line_break",
    "SerializedMessage",
    "is_serialized_grouped_message",
    "redirect_stdout",
    "redirect_stderr",
    "GroupedMessage",
)


def is_end_line_break(val_str: str) -> bool:
    """Check whether the str ends with a line break

    The checking is implemented by
        https://docs.python.org/3/library/stdtypes.html#str.splitlines

    We use this function to fix the missing final line break problem of
    `str.splitlines`.
    """
    if not val_str:
        return False
    res = str.splitlines(val_str[-1])
    return len(res) == 1 and res[0] == ""


class SerializedMessage(
    TypedDict(
        "_SerializedMessage",
        {"/is_syncsdata": Literal[True], "/type": Literal["GroupedMessage"]},
    )
):
    """Serialized message returned by `GroupedMessage`.

    This method is used for exchanging the messages in different modes, including:
    - multi-processing.
    - file
    - web-based exchanging.

    The messages are serialized as a JSON-compatible Dictionary.

    Keywords
    --------
    /is_syncsdata: `True`
        Internal value. It is always `True`. Used for validating whether the provided
        data is from this `syncstream` package.

    /type: `"GroupedMessage"`
        internal value. It is always `"GroupedMessage"`. Used for validating the type
        of the data.

    type: `"str" | "warning" | "error"`
        The type of the message data.

    data: `[str]`
        The message data content. It is always a sequence of strings.
    """

    type: Literal["str", "warning", "error"]
    data: Tuple[str, ...]


def is_serialized_grouped_message(obj: Any) -> TypeGuard[SerializedMessage]:
    """Determine whether `obj` is a serialized `GroupedMessage`.

    Arguments
    ---------
    obj: `Any`
        The object to be checked.

    Returns
    -------
    #1: `True` if `obj` is `SerializedMessage`.
    """
    return (
        isinstance(obj, collections.abc.Mapping)
        and obj.get("/is_syncsdata", False)
        and obj.get("/type", None) == "GroupedMessage"
    )


class RedirectTarget(Protocol):
    """A protocol for redirectable object"""

    def write(self, data: str) -> int: ...


_RedirectTarget = TypeVar("_RedirectTarget", bound=RedirectTarget)


class redirect_stdout(contextlib.ContextDecorator, Generic[_RedirectTarget]):
    """A wrapped version of `contextlib.redirect_stdout`

    This context allows a `syncstream.LineBuffer` or its mirror to be configured as
    the redirect target without raising typehint errors.
    """

    def __init__(self, target: _RedirectTarget) -> None:
        self.__inner = contextlib.redirect_stdout(cast(Any, target))

    def __enter__(self) -> _RedirectTarget:
        return self.__inner.__enter__()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: types.TracebackType,
    ):
        return self.__inner.__exit__(exc_type, exc_value, exc_traceback)


class redirect_stderr(contextlib.ContextDecorator, Generic[_RedirectTarget]):
    """A wrapped version of `contextlib.redirect_stderr`

    This context allows a `syncstream.LineBuffer` or its mirror to be configured as
    the redirect target without raising typehint errors.
    """

    def __init__(self, target: _RedirectTarget) -> None:
        self.__inner = contextlib.redirect_stderr(cast(Any, target))

    def __enter__(self) -> _RedirectTarget:
        return self.__inner.__enter__()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: types.TracebackType,
    ):
        self.__inner.__exit__(exc_type, exc_value, exc_traceback)


class GroupedMessage:
    """A group of messages.
    Used for wrapping the warning and error messages.
    """

    def __init__(
        self, data: Union[str, Sequence[str], Warning, BaseException, None] = None
    ) -> None:
        self.type: Literal["str", "warning", "error"] = "str"
        self.data: Tuple[str, ...] = tuple()
        if data is None:
            pass
        elif isinstance(data, str):
            self.data = (data,)
        elif isinstance(data, (BaseException, Warning)):
            if isinstance(data, Warning):
                self.type = "warning"
            else:
                self.type = "error"
            data = traceback.format_exception(type(data), data, data.__traceback__)
            data = "".join(data).splitlines()
            self.data = tuple(data)
        else:
            self.data = tuple(str(val) for val in data)

    def __repr__(self) -> str:
        return "<{0} object (type={1}) at 0x{2:x}>".format(
            self.__class__.__name__, self.type, id(self)
        )

    def __str__(self) -> str:
        return "\n".join(self.data)

    def serialize(self) -> SerializedMessage:
        """Serialize this message item into a JSON compatible dict."""
        return {
            "/is_syncsdata": True,
            "/type": "GroupedMessage",
            "type": self.type,
            "data": self.data,
        }

    @classmethod
    def deserialize(cls: Type[Self], jdata: Any) -> Self:
        """Deserialize the JSON compatible dict into this object."""
        if not is_serialized_grouped_message(jdata):
            return jdata
        new_item = cls(data=None)
        new_item.type = jdata["type"]
        new_item.data = tuple(jdata["data"])
        return new_item
