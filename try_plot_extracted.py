# -*- coding: utf-8 -*-
"""

plot histograms from extracted values

@author: Jussi (jnu@iki.fi)
"""


# %% init
from collections import defaultdict

from collect_gait import utils
import datetime
import gaitutils
import itertools
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


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
MAX_DIRS = 15  # XXX: let's limit the number of dirs for testing purposes

for row, d in enumerate(dirs):
    print(f'reading from {d}')
    c3ds = gaitutils.sessionutils.get_c3ds(d, tags=tags, trial_type='dynamic')
    print(f'{len(c3ds)} tagged trials')
    alldirs[d] = c3ds
    if row == MAX_DIRS:
        break

print('---')
print(f'{row} gait session dirs')
allfiles = list(itertools.chain.from_iterable(alldirs.values()))
print(f'{len(allfiles)} total c3d files')


# %% load the trials and get some curves
data_all, cycles_all = gaitutils.stats.collect_trial_data(allfiles)

extr_vals = dict()
for var in list(gaitutils.models.pig_lowerbody.varnames) + list(gaitutils.models.pig_lowerbody_kinetics.varnames):
    data = data_all['model'][var]
    toeoffs = [cyc.toeoffn for cyc in cycles_all['model'][var]]
    print(var)
    if data is not None and toeoffs is not None:
        extr_vals[var] = gaitutils.stats.curve_extract_values(data, toeoffs)
    else:
        print('no data for %s' % var)


# %%

"""
halutut muuttujat:

•	nilkan asento (koukistusarvo) alkukontaktissa (IC)
•	polven asento (ojennusarvo) alkukontaktissa IC
•	lonkan koukistuskulma alkukontaktissa
•	nilkan koukistuskulman arvo tukivaiheen lopulla (stance, esim. kohta 40 tai 45% ) tai nilkan maksimi koukistusarvo tukivaiheessa
•	polven ojennus tukivaiheen lopulla (stance, esim. kohta 40 tai 45% ) tai polven maksimi ojennusarvo tukivaiheessa
•	Lonkan maksimi ojennusarvo tukivaiheessa
•	polven maksimi koukistus heilahdusvaiheessa.
•	polven ojennus heilahdusvaiheen lopulla  - KYSEENALAINEN, SAMA KUIN ALKUKONTAKTISSA?
•	lonkan maksimi koukistusarvo heilahdusvaiheessa

+ muuttujat JP:n paperista
"""


# define desired variables
# these are lists of (nested) keys into the dict returned by curve_extract_values

nested_keylist = [
['AnkleAnglesX', 'contact'],
['KneeAnglesX', 'contact'],
['HipAnglesX', 'contact'],
['AnkleAnglesX', 'peaks', 'stance', 'min'],
['KneeAnglesX', 'peaks', 'stance', 'max'],
['HipAnglesX', 'peaks', 'stance', 'min'],
['KneeAnglesX', 'peaks', 'swing', 'max'],
# ['KneeAnglesX', 'peaks', 'swing', 'max'],
['HipAnglesX', 'peaks', 'swing', 'max'],
]


def _compose_varname(nested_keys):
    """Compose a variable name for extracted variable"""
    varname = nested_keys[0]
    themodel = gaitutils.models.model_from_var(varname)
    name = themodel.varlabels_noside[varname]  # variable label
    name += ' at '
    if nested_keys[1] == 'contact':
        name += 'initial contact'
    elif nested_keys[1] in ['peaks', 'extrema']:
        phase = nested_keys[2]
        name += phase + ' phase '
        name += nested_keys[3]
    return name


def nested_get(di, keys):    
    """Get a value from a nested dict, using a list of keys"""
    for key in keys:
        di = di[key]  # iterate until we exhaust the nested keys
    return di


for ctxt in 'RL':
    print(ctxt)
    for nested_keys in nested_keylist:
        print(_compose_varname(nested_keys))
        nested_keys_context = nested_keys.copy()
        nested_keys_context[0] = ctxt + nested_keys_context[0]
        nested_get(extr_vals, nested_keys_context)




# %%
from plotly.subplots import make_subplots
import plotly.graph_objects as go

ctxts = ['Left', 'Right']
subtitles = [f'{_compose_varname(nested_keys)}' for nested_keys in nested_keylist for ctxt in ctxts]

nvars = len(nested_keylist)
fig = make_subplots(rows=nvars, cols=2, subplot_titles=subtitles)

for row, nested_keys in enumerate(nested_keylist, 1):
    varname = _compose_varname(nested_keys)
    for col, ctxt in enumerate('LR', 1):
        nested_keys_ctxt = nested_keys.copy()
        nested_keys_ctxt[0] = ctxt + nested_keys[0] 
        vals = nested_get(extr_vals, nested_keys_ctxt)
        hist = go.Histogram(x=vals, nbinsx=20, name='', opacity=.5)
        fig.append_trace(hist, row=row, col=col)

# Overlay both histograms
fig.update_layout(barmode='overlay')
# Reduce opacity to see both histograms
fig.update_traces(opacity=0.75)

gaitutils.viz.plot_misc.show_fig(fig)


# %%
a = np.array([[[1,2,3], [1,2,3]],
              [[999,5,6], [4,5,6]],
              [[999,8,9], [7,999,9]]
              ])

#for x in a:
#    print(x)

np.delete(a, np.where(a == 999)[0], axis=0)


# %%


for i in range(0,len(a)):
    if 999 in a[i]:
        np.delete(a, i, 0)