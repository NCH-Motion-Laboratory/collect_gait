# -*- coding: utf-8 -*-
"""

Utility functions.

@author: Jussi (jnu@iki.fi)
"""


from __future__ import print_function
from random import shuffle
import glob
import os
import os.path as op
from openpyxl import Workbook
from time import localtime, strftime
import logging
import json
from gaitutils import sessionutils

logger = logging.getLogger(__name__)


# read configuration JSON file from home dir
homedir = op.expanduser('~')
cfg_json = op.join(homedir, 'cp_analysis.json')
if not op.isfile(cfg_json):
    raise ValueError('must create config file %s' % cfg_json)
with open(cfg_json, 'rb') as f:
    params = json.load(f)

if not op.isdir(params['rootdir']):
    raise ValueError('configured root dir %s does not exist' % params['rootdir'])

# globs for each trial type
globs = dict()
globs['cognitive'] = ['*C?_*', '*K?_*']  # globs for cognitive trials
globs['normal'] = ['*N?_*']  # globs for normal
globs['tray'] = ['*T?_*']  # globs for tray trials

# exclude patterns - filenames including one of these will be dropped
files_exclude = ['stance', 'one', 'foam', 'hop', 'stand', 'balance',
                 'toes', 'toget', 'loitonnus', 'abduction']


def _ipython_setup():
    """Performs some IPython magic if we are running in IPython"""
    try:
        __IPYTHON__
    except NameError:
        return
    from IPython import get_ipython
    ip = get_ipython()
    ip.magic("gui qt5")  # needed for mayavi plots
    ip.magic("reload_ext autoreload")
    ip.magic("autoreload 2")


def _glob_all(globs, prefix=None, postfix=None):
    """Glob from a list, adding prefix (maybe a directory)"""
    if not isinstance(globs, list):
        globs = [globs]
    files = list()
    for g in globs:
        glob_ = op.join(prefix, g) if prefix else g
        glob_ += postfix if postfix is not None else ''
        files.extend(glob.glob(glob_))
    return files


def get_timestr():
    """ Get a second-resolution timestr (current time) that can be put into
    file names etc. """
    return strftime("%Y_%m_%d-%H%M%S", localtime())


def get_subjects(rootdir=None):
    """ Get list of all subject names, e.g. 'TD01' """
    rootdir = rootdir or params['rootdir']
    subjects = list()
    for glob_ in params['subj_globs']:
        glob_full = op.join(rootdir, glob_)
        subjects.extend(glob.glob(glob_full))
    # include dirs only
    subjects = [s for s in subjects if op.isdir(s)]
    # strip paths for get_files()
    subjects = [op.split(subj)[-1] for subj in subjects]
    # randomize order for debug purposes
    #shuffle(subjects)
    return subjects


def get_files(subject, types, ext='c3d', newer_than=None, rootdir=None):
    """ Get trial files according to given subject and trial type
    (e.g. 'normal') and file extension """

    rootdir = rootdir or params['rootdir']

    if not isinstance(types, list):
        types = [types]

    globs_ = list()

    for t in types:
        if t not in globs:
            raise Exception('Invalid trial type')
        else:
            globs_ += globs[t]

    logger.debug('finding trial files for %s, types %s' % (subject, types))
    # try to auto find data dirs under subject dir
    subjdir = op.join(rootdir, subject)
    if not op.isdir(subjdir):
        logger.warning('Subject directory not found: %s' % subjdir)
        return list()

    datadirs = [file for file in os.listdir(subjdir) if
                op.isdir(op.join(subjdir, file))]

    logger.debug('subject data dirs: %s' % datadirs)

    # try each datadir in turn (but we only return data from one per subject)
    for datadir in datadirs:

        logger.debug('trying data dir %s/%s' % (subject, datadir))
        prefix = op.join(subjdir, datadir)
        files = _glob_all(globs_, prefix=prefix, postfix=ext)

        files_exc = [it for it in files if any([exc.lower() in it.lower()
                     for exc in files_exclude])]
        files = list(set(files) - set(files_exc))
        logger.debug('excluding: %s' % files_exc)

        if not files:
            logger.debug('%s is probably not a CP data dir' % datadir)
            continue

        logger.debug('subject %s, %s trials: found %d files'
                     % (subject, '/'.join(types), len(files)))

        if newer_than is not None:
            sessiondate = sessionutils.get_session_date(prefix)
            logger.info('session %s timestamp %s' % (datadir, sessiondate))
            if sessiondate < newer_than:
                logger.info('session %s too old' % datadir)
                continue

        return files

    logger.info('no acceptable files found for %s' % subject)
    return list()


def get_static_files(subject, newer_than=None, rootdir=None):
    """ Get trial files according to given subject and trial type
    (e.g. 'normal') and file extension """

    rootdir = rootdir or params['rootdir']
    logger.debug('finding static trial files for %s' % subject)
    # try to auto find data dirs under subject dir
    subjdir = op.join(rootdir, subject)
    if not op.isdir(subjdir):
        logger.warning('Subject directory not found: %s' % subjdir)
        return list()

    datadirs = [file for file in os.listdir(subjdir) if
                op.isdir(op.join(subjdir, file))]

    logger.debug('subject data dirs: %s' % datadirs)

    for datadir in datadirs:

        logger.debug('trying data dir %s/%s' % (subject, datadir))
        sessiondir = op.join(subjdir, datadir)

        files = sessionutils.get_c3ds(sessiondir, trial_type='static',
                                      check_if_exists=True)

        if not files:
            logger.debug('%s is probably not a CP data dir' % datadir)
            continue

        if newer_than is not None:
            sessiondate = sessionutils.get_session_date(sessiondir)
            logger.info('session %s timestamp %s' % (datadir, sessiondate))
            if sessiondate < newer_than:
                logger.info('session %s too old' % datadir)
                continue

        logger.debug('subject %s, datadir %s, static trials: found %d files'
                     % (subject, sessiondir, len(files)))
        return files

    # we did not hit return
    logger.info('no acceptable static trials found for %s' % subject)
    return list()


def write_workbook(results, filename, first_col=1, first_row=1):
    """Write results into .xlsx file (filename). results must be a list of
    lists which represent the columns to write. first_col and first_row
    specify the column and row where to start writing (1-based) """
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Gait analysis parameters"
    for j, col in enumerate(results):
        for k, val in enumerate(col):
            ws1.cell(column=j+1+first_col, row=k+1+first_row, value=val)
    logger.debug('saving %s' % filename)
    wb.save(filename=filename)
