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
import matplotlib.pyplot as plt

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
alldirs = dict()  # save dirs/files here
MAX_DIRS = 5  # XXX: let's limit the number of dirs for testing purposes

for i, d in enumerate(dirs):
    print(f'reading from {d}')
    c3ds = gaitutils.sessionutils.get_c3ds(d, tags=tags, trial_type='dynamic')
    print(f'{len(c3ds)} tagged trials')
    alldirs[d] = c3ds
    if i == MAX_DIRS:
        break

print('---')
print(f'{i} gait session dirs')
allfiles = list(itertools.chain.from_iterable(alldirs.values()))
print(f'{len(allfiles)} total c3d files')


# %% load the trials and get some curves
trials = [gaitutils.trial.Trial(fn) for fn in allfiles]

# collect the data into numpy arrays
# all model variables will be normalized into gait cycles (x axis 0..100%)
data_all, ncycles, toeoff_frames = gaitutils.stats.collect_trial_data(trials)
knee_flex = data_all['model']['LKneeAnglesX']  # extract left sagittal knee angle
plt.plot(knee_flex.T)  # matplotlib plots columns by default, so transpose
