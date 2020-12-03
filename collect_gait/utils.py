# -*- coding: utf-8 -*-
"""

Utility functions.

@author: Jussi (jnu@iki.fi)
"""


import glob
import os
import os.path as op
from re import sub
from time import localtime, strftime
import logging
import datetime

logger = logging.getLogger(__name__)


def get_timestr():
    """Get a second-resolution timestr (current time) that can be put into
    file names etc."""
    return strftime("%Y_%m_%d-%H%M%S", localtime())


def _get_subdirs_recursive(dirname):
    """Recursively get all subdirs under a given directory"""
    for t in os.walk(dirname):
        yield t[0]


def _is_gait_session(dirname):
    """Check if directory is a Vicon gait session"""
    # we require a session enf file and at least one x1d file
    enfglob = op.join(dirname, '*Session*.enf')
    x1dglob = op.join(dirname, '*.x1d')
    return bool(glob.glob(enfglob)) and bool(glob.glob(x1dglob))


def _get_date(sessiondir):
    """Return a datetime.datetime object representing the session date"""
    if not _is_gait_session(sessiondir):
        raise ValueError('%s is not a gait session' % sessiondir)
    x1dglob = op.join(sessiondir, '*.x1d')
    x1d = glob.glob(x1dglob)[0]
    return datetime.datetime.fromtimestamp(op.getmtime(x1d))


def _filter_newer(sessiondirs, date):
    """Filter for sessions that are newer than given datetime.datetime object"""
    for sessiondir in sessiondirs:
        if _get_date(sessiondir) > date:
            yield sessiondir


def _filter_is_gait_session(dirnames):
    """Filter for gait sessions"""
    for dirname in dirnames:
        if _is_gait_session(dirname):
            yield dirname


def _filter_substrings(dirnames, substrings):
    """Filter according to iterabe of of substrings in dir name"""
    if isinstance(substrings, str):  # accept also single str
        substrings = [substrings]
    for dirname in dirnames:
        if any(substr in dirname for substr in substrings):
            yield dirname


def get_sessiondirs(rootdir, newer_than=None, substrings=None):
    """Recursively get all gait session directories under a given directory.

    Parameters
    ----------
    rootdir : str
        The directory under which to search.
    newer_than : datetime.datetime
        If not None, return only sessions newer than given date.
        E.g. newer_than=datetime.datetime(2018, 3, 1)
    substrings : iterable of str
        If not None, specifies substrings that must be present in directory
        names.

    Yields
    -------
    str
        A session directory.
    """
    dirs = _get_subdirs_recursive(rootdir)
    if substrings is not None:
        dirs = _filter_substrings(dirs, substrings)
    sessiondirs = _filter_is_gait_session(dirs)
    if newer_than is not None:
        sessiondirs = _filter_newer(sessiondirs, newer_than)
    yield from sessiondirs
