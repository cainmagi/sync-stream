#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
#   fasteners 0.16+
# A python tool for synchronizing the messages from different
# threads, processes, or hosts.
# This package provides 4 modes for the synchronization,
# including:
# 1. thread-sync: used when we need to capture messages among
#                 different threads.
# 2. process-sync: used when we need to capture messages among
#                  different processes, on the same device.
# 3. file-based-sync: used when we need to capture messages
#                     among different processes from different
#                     devices, but the storage is shared.
# 4. host-sync: used when we need to capture messages among
#               different devices (hosts), and the storage could
#               be accessed by only one host.
################################################################
# Update reports:
# ---------------
# 0.3.2 @ 6/14/2021
#   1. Fix a bug caused by stopping the mirrors.
#   2. Format the meta-data defined in `setup.py`.
#   3. Add the documentation. Currently only the tutorial is
#      finished.
# 0.3.0 @ 6/4/2021
#   1. Support the stop signal for `mproc` and `host` modules.
#   2. Fix some bugs in the testing script.
#   3. Fix typos.
# 0.2.2 @ 5/25/2021
#   1. Add `clear()` methods for all buffers and mirrors.
#   2. Fix typos in the package setup and info file.
#   3. Fix a bug caused by writing data to the host in the
#      testing scripts for Linux.
# 0.2.1 @ 5/24/2021
#   1. Add the PyPI publish workflow.
# 0.2.0 @ 5/24/2021
#   1. Finish the synchronization based on the file lock package
#      `fasteners`.
#   2. Finish the synchronization based on the web service
#      packages `flask`, `flask-restful` and `urllib3`.
# 0.1.0 @ 5/22/2021
#   1. Finish the synchronization based on the stdlib
#      `multiprocessing` and `threading`.
#   2. Create this project.
################################################################
'''

from pkgutil import extend_path

# Import sub-modules
from . import base  # basic tools
from . import mproc  # threading and multiprocessing

try:
    from . import file  # file-based mode
    IS_FILE_ENABLED = True
except ImportError:
    IS_FILE_ENABLED = False

try:
    from . import host  # host-based mode
    IS_HOST_ENABLED = True
except ImportError:
    IS_HOST_ENABLED = False


__version__ = '0.3.2'

__all__ = (
    'base', 'mproc',
    'LineBuffer', 'LineProcBuffer', 'LineProcMirror',
    *(('file', 'LineFileBuffer') if IS_FILE_ENABLED else tuple()),
    *(('host', 'LineHostBuffer', 'LineHostMirror') if IS_HOST_ENABLED else tuple()),
)

# Set this local module as the prefered one
__path__ = extend_path(__path__, __name__)

# Delete private sub-modules and objects
del extend_path

# Aliases
LineBuffer = mproc.LineBuffer
LineProcBuffer = mproc.LineProcBuffer
LineProcMirror = mproc.LineProcMirror

if IS_FILE_ENABLED:
    LineFileBuffer = file.LineFileBuffer

if IS_HOST_ENABLED:
    LineHostBuffer = host.LineHostBuffer
    LineHostMirror = host.LineHostMirror
