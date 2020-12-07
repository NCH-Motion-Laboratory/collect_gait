# -*- coding: utf-8 -*-
"""

testbench for collect_gait

@author: Jussi (jnu@iki.fi)
"""


# %% init
from collections import defaultdict

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
knee_toeoffs = toeoff_frames['model']['LKneeAnglesX']
plt.plot(knee_flex.T)  # matplotlib plots columns by default, so transpose


# %% try out some curve analysis
import scipy
import numpy as np


def curve_extract_values(curves, toeoffs):
    """Extract values from gait curves.

    Parameters
    ----------
    curves : ndarray
        NxT array of gait curves. Typically T==101 for normalized data.
    toeoffs : ndarray
        Nx1 array of toeoff frame indices, one for each curve. This frame
        separates the contact phase from the swing phase.

    Returns
    -------
    tuple
        A tuple of two nested dicts (extrema, peaks) where extrema corresponds to
        simple min/max and peaks corresponds to automatically detected peaks
        (local minima/maxima). The keys for the three nested dicts are:

        1 = 'swing' / 'contact' : indicates the phase of the gait cycle
        2 = 'max' / 'min' :
        3 = 'indices' / 'values' : values at the peaks/extrema and their indices.

        Thus, to get the maximum curve values at the peaks of the swing phase,
        you can use peaks['swing']['max']['values'].
    """

    ncurves = curves.shape[0]

    # make curves for contact phase (set swing phase to nan)
    curves_contact = curves.copy()
    for k, toeoff in zip(range(ncurves), toeoffs):
        curves_contact[k, toeoff:] = np.nan

    # make curves for swing phase (set contact phase to nan)
    curves_swing = curves.copy()
    for k, toeoff in zip(range(ncurves), toeoffs):
        curves_swing[k, :toeoff] = np.nan

    # simple extrema (no peak search)
    extrema = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    extrema['overall']['min']['values'] = curves.min(axis=1)
    extrema['overall']['max']['values'] = curves.max(axis=1)
    extrema['overall']['min']['indices'] = curves.argmin(axis=1)
    extrema['overall']['max']['indices'] = curves.argmax(axis=1)

    extrema['contact']['min']['values'] = np.nanmin(curves_contact, axis=1)
    extrema['contact']['max']['values'] = np.nanmax(curves_contact, axis=1)
    extrema['contact']['min']['indices'] = np.nanargmin(curves_contact, axis=1)
    extrema['contact']['max']['indices'] = np.nanargmax(curves_contact, axis=1)

    extrema['swing']['min']['values'] = np.nanmin(curves_swing, axis=1)
    extrema['swing']['max']['values'] = np.nanmax(curves_swing, axis=1)
    extrema['swing']['min']['indices'] = np.nanargmin(curves_swing, axis=1)
    extrema['swing']['max']['indices'] = np.nanargmax(curves_swing, axis=1)

    # peaks during contact and swing phase
    peaks = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for curve in curves_contact:
        # indices of the peaks
        peaks['contact']['max']['inds'].append(
            scipy.signal.argrelextrema(curve, np.greater)[0]
        )
        peaks['contact']['min']['inds'].append(
            scipy.signal.argrelextrema(curve, np.less)[0]
        )
        # the corresponding curve values at the peaks
        peaks['contact']['max']['values'].append(
            curve[peaks['contact']['max']['inds'][-1]]
        )
        peaks['contact']['min']['values'].append(
            curve[peaks['contact']['min']['inds'][-1]]
        )

    for curve in curves_swing:
        # indices of the peaks
        peaks['swing']['max']['inds'].append(
            scipy.signal.argrelextrema(curve, np.greater)[0]
        )
        peaks['swing']['min']['inds'].append(
            scipy.signal.argrelextrema(curve, np.less)[0]
        )
        # the corresponding curve values at the peaks
        peaks['swing']['max']['values'].append(curve[peaks['swing']['max']['inds'][-1]])
        peaks['swing']['min']['values'].append(curve[peaks['swing']['min']['inds'][-1]])

    return extrema, peaks


# %% some testing
extrema, peaks = curve_extract_values(knee_flex, knee_toeoffs)


curves = np.zeros((1, 101))
curves[0, 5] = 1
curves[0, 90] = 3
curves[0, 60] 

toeoffs = [60]

extrema, peaks = curve_extract_values(curves, toeoffs)


# %%
