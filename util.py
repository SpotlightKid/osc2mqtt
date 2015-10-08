# -*- coding: utf-8 -*-
"""Utility functions for reading osc2mqtt configuration."""

from __future__ import absolute_import, unicode_literals

import shlex


def as_bool(val):
    return str(val).lower() in ('1', 'enabled', 'on', 't', 'true', 'y', 'yes')


def parse_hostport(addr, port=9000):
    if ('::' in addr and ']:' in addr) or ('::' not in addr and ':' in addr):
        host, port = addr.rsplit(':', 1)
    else:
        host = addr

    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]

    return (host, int(port))


def parse_list(s):
    lexer = shlex.shlex(s, posix=True)
    lexer.whitespace = ','
    lexer.whitespace_split = True
    lexer.commenters = ''
    return [token.strip() for token in lexer]
