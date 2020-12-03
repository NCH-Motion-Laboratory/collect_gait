# -*- coding: utf-8 -*-
"""

testbench for collect_gait

@author: Jussi (jnu@iki.fi)
"""


# %% init
from collect_gait import utils
import datetime
import gaitutils
import itertools

# let's get all sessions under this dir...
rootdir = r"Z:\Userdata_Vicon_Server"
# ...newer than this date
date = datetime.datetime(2019, 3, 1)
# tags for dynamic trials
tags = ['E1', 'E2', 'E3', 'T1', 'T2', 'T3']
# strings that must be included in dir names
substrings = ['1_Diplegia', '1_Hemiplegia', '1_Eridiagnoosit', '1_Meningomyelecele']

dirs = utils.get_sessiondirs(rootdir, newer_than=date, substrings=substrings)


# %% scan the directory tree
alldata = dict()

for d in dirs:
    print(f'reading from {d}')
    c3ds = gaitutils.sessionutils.get_c3ds(d, tags=tags, trial_type='dynamic')
    print(f'{len(c3ds)} tagged trials')
    alldata[d] = c3ds

print(f'{len(d)} gait session dirs')
allfiles = list(itertools.chain.from_iterable(alldata.values()))
print(f'{len(allfiles)} total c3d files')


