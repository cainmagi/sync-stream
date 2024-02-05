# -*- coding: UTF-8 -*-
"""
Sync-stream
===========

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu

Description
-----------
A python tool for synchronizing the messages from different threads, processes, or
hosts.

This package provides 4 modes for the synchronization, including:
1. thread-sync: used when we need to capture messages among different threads.
2. process-sync: used when we need to capture messages among different processes, on
   the same device.
3. file-based-sync: used when we need to capture messages among different processes
   from different devices, but the storage is shared.
4. host-sync: used when we need to capture messages among different devices (hosts),
   and the storage could be accessed by only one host.
"""

from pkgutil import extend_path

from .version import __version__

# Import utilities
from typing import TYPE_CHECKING
from . import utils

# Import sub-modules
from . import base  # basic tools
from .base import GroupedMessage, redirect_stdout, redirect_stderr

from . import mproc  # threading and multiprocessing
from .mproc import LineBuffer, LineProcBuffer, LineProcMirror

if TYPE_CHECKING:
    from . import file  # file-based mode
    from .file import LineFileBuffer
else:
    file = utils.lazy_import(
        "file",
        package=__name__,
        dependencies="fasteners",
        required=False,
    )
    LineFileBuffer = utils.get_lazy_attribute(file, "LineFileBuffer", __name__)


if TYPE_CHECKING:
    from . import webtools
    from . import host  # file-based mode
    from .host import LineHostBuffer, LineHostMirror, LineHostReader
else:
    webtools = utils.lazy_import(
        "webtools",
        package=__name__,
        dependencies=("urllib3", "packaging"),
        required=False,
    )
    host = utils.lazy_import(
        "host",
        package=__name__,
        dependencies=("urllib3", "packaging", "flask"),
        rel_dependencies=(webtools,),
        required=False,
    )
    LineHostBuffer = utils.get_lazy_attribute(host, "LineHostBuffer", __name__)
    LineHostMirror = utils.get_lazy_attribute(host, "LineHostMirror", __name__)
    LineHostReader = utils.get_lazy_attribute(host, "LineHostReader", __name__)


__all__ = (
    "__version__",
    "utils",
    "base",
    "GroupedMessage",
    "redirect_stdout",
    "redirect_stderr",
    "mproc",
    "LineBuffer",
    "LineProcBuffer",
    "LineProcMirror",
    "file",
    "LineFileBuffer",
    "host",
    "LineHostBuffer",
    "LineHostMirror",
    "LineHostReader",
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path
