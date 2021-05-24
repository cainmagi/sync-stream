#!python
# -*- coding: UTF-8 -*-
'''
################################################################
# Basic tools.
# @ Sync-stream
# Produced by
# Yuchen Jin @ cainmagi@gmail.com,
#              yjin4@uh.edu.
# Requirements: (Pay attention to version)
#   python 3.6+
# This module contains shared basic tools for different modules.
################################################################
'''

import traceback

from typing import Union
try:
    from typing import Sequence
except ImportError:
    from collections.abc import Sequence


def is_end_line_break(val_str: str) -> bool:
    '''Check whether the str ends with a line break
    The checking is implemented by
        https://docs.python.org/3/library/stdtypes.html#str.splitlines
    We use this function to fix the missing final line break problem of str.splitlines.
    '''
    if not val_str:
        return False
    res = str.splitlines(val_str[-1])
    return len(res) == 1 and res[0] == ''


class GroupedMessage:
    '''A group of messages.
    Used for wrapping the warning and error messages.
    '''
    def __init__(self, data: Union[Sequence[str], Warning, Exception] = None) -> None:
        if data is None:
            data = []
            self.type = 'str'
        elif isinstance(data, (Exception, Warning)):
            if isinstance(data, Warning):
                self.type = 'warning'
            else:
                self.type = 'error'
            data = traceback.format_exception(type(data), data, data.__traceback__)
            data = ''.join(data).splitlines()
        else:
            self.type = 'str'
        self.data = data

    def __repr__(self) -> str:
        return '<GroupedMessage object (type={0}) at 0x{1}>'.format(self.type, id(self))

    def __str__(self) -> str:
        return '\n'.join(self.data)

    def serialize(self) -> dict:
        '''Serialize this message item into a JSON compatible dict.'''
        return {
            '/is_syncsdata': True,
            '/type': 'GroupedMessage',
            'type': self.type,
            'data': self.data
        }

    @classmethod
    def deserialize(cls, jdata: dict):
        '''Deserialize the JSON compatible dict into this object.'''
        if not jdata.get('/is_syncsdata', False) or jdata.get('/type', None) != 'GroupedMessage':
            return jdata
        new_item = cls(data=None)
        new_item.type = jdata['type']
        new_item.data = jdata['data']
        return new_item
