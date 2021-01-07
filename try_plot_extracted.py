# -*- coding: utf-8 -*-
"""

plot histograms from extracted values

TODO:

L/R column titles
avg/stddev lines?
JP defined vars
x axis scaling

try different chart types:
strip chart: https://plotly.com/python/strip-charts/  - staggered scatterplot
    -needs px, pandas
box chart: https://plotly.com/python/box-plots/  - e.g. median and quartiles




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
import os.path as op
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from gaitutils.viz.plot_plotly import _get_plotly_axis_labels
from gaitutils.viz.plot_common import _cyclical_mapper
from gaitutils import cfg
import logging

logging.basicConfig(level=logging.DEBUG)

# let's get all sessions under this dir...
rootdir = r"Z:\Userdata_Vicon_Server"
rootdir = r"C:\Temp\D0063_RR"
rootdir = r"Y:\Userdata_Vicon_Server\1_Diplegia\D0063_RR"

# ...newer than this date
date = datetime.datetime(2018, 1, 1)
# tags for dynamic trials
tags = ['E1', 'E2', 'E3', 'T1', 'T2', 'T3']
substrings = None

sessions = list(utils.get_sessiondirs(rootdir, newer_than=date, substrings=substrings))[
    :3
]


# %% try out plotting


def _nested_get(di, keys):
    """Get a value from a nested dict, using a list of keys"""
    for key in keys:
        di = di[key]  # iterate until we exhaust the nested keys
    return di


def _compose_varname(vardef):
    """Compose a variable name for extracted variable.

    E.g. ['HipAnglesX', 'peaks', 'swing', 'max']
    -> 'Hip flexion maximum during swing phase'
    """
    varname = vardef[0]
    # get variable description from gaitutils.models
    themodel = gaitutils.models.model_from_var(varname)
    name = themodel.varlabels_noside[varname]
    if vardef[1] == 'contact':
        name += ' at initial contact'
    elif vardef[1] in ['peaks', 'extrema']:
        phase = vardef[2]  # swing, stance etc.
        valtype = vardef[3]  # min, max etc.
        val_trans = {'max': 'maximum', 'min': 'minimum'}
        if phase == 'overall':
            name += ', %s %s' % (phase, val_trans[valtype])
        else:
            name += ', %s phase %s' % (phase, val_trans[valtype])
        if vardef[1] == 'peaks':
            name += ' peak'
    return name


def _var_unit(vardef):
    """Return unit for a vardef"""
    varname = vardef[0]
    themodel = gaitutils.models.model_from_var(varname)
    return themodel.units[varname]


def box_comparison(sessions, vardefs, vals):
    """Plot comparison of extracted values as box plot"""

    subtitles = [_compose_varname(nested_keys) for nested_keys in vardefs]

    nvars = len(vardefs)
    fig = make_subplots(rows=nvars, cols=1, subplot_titles=subtitles)
    legendgroups = set()
    trace_colors = _cyclical_mapper(cfg.plot.colors)

    # y will be the concatenated vals for all sessions; x will be the corresponding session names
    # this is done separately for L/R

    for row, vardef in enumerate(vardefs):

        ctxt = 'L'
        vardef_ctxt = [ctxt + vardef[0]] + vardef[1:]
        # this looks horrible. the idea is just to get lists of values and the corresponding sessions
        lvals, sessionnames_l = list(zip(
            *itertools.chain.from_iterable(
                zip(_nested_get(session_vals, vardef_ctxt), itertools.repeat(op.split(session)[-1]))
                for session, session_vals in vals.items()
            )
        )
        )

        ctxt = 'R'
        vardef_ctxt = [ctxt + vardef[0]] + vardef[1:]
        rvals, sessionnames_r = list(zip(
            *itertools.chain.from_iterable(
                zip(_nested_get(session_vals, vardef_ctxt), itertools.repeat(op.split(session)[-1]))
                for session, session_vals in vals.items()
            )
        )
        )

        
        show_legend = 'L' not in legendgroups
        legendgroups.add('L')
        box1 = go.Box(
            x=sessionnames_l,
            y=lvals,
            # boxpoints='all',
            name='L',
            offsetgroup='L',
            legendgroup='L',
            showlegend=show_legend,
            opacity=0.5,
            # mode='lines+markers',
            marker_color=cfg.plot.context_colors['L']
        )
        fig.append_trace(box1, row=row + 1, col=1)

        show_legend = 'R' not in legendgroups
        legendgroups.add('R')
        box2 = go.Box(
            x=sessionnames_r,
            y=rvals,
            # boxpoints='all',
            name='R',
            offsetgroup='R',            
            legendgroup='R',
            showlegend=show_legend,
            opacity=0.5,
            # mode='lines+markers',
            marker_color=cfg.plot.context_colors['R']
        )
        fig.append_trace(box2, row=row + 1, col=1)

        xlabel = _var_unit(vardef_ctxt)
        xaxis, yaxis = _get_plotly_axis_labels(row, 0, ncols=1)
        fig['layout'][yaxis].update(
            title={
                'text': xlabel,
                'standoff': 0,
            }
        )

    fig.update_layout(
       boxmode='group' # group together boxes of the different traces for each value of x
    )

    gaitutils.viz.plot_misc.show_fig(fig)



# %% try it out
# kinematics vardefs

vardefs = [
    ['AnkleAnglesX', 'contact'],
    ['KneeAnglesX', 'contact'],
    ['HipAnglesX', 'contact'],
    ['AnkleAnglesX', 'extrema', 'stance', 'min'],
    ['KneeAnglesX', 'extrema', 'stance', 'max'],
    ['KneeAnglesX', 'extrema', 'swing', 'max'],
    ['HipAnglesX', 'extrema', 'stance', 'min'],
    ['HipAnglesX', 'extrema', 'swing', 'max'],
]

# find the necessary models
models = set(gaitutils.models.model_from_var(vardef[0]) for vardef in vardefs)
# extract the curve values
vals = {
    session: gaitutils.stats._extract_values(session, tags=None, from_models=models)
    for session in sessions
}

box_comparison(sessions, vardefs, vals)



# %% plot


# %% kinetics vardefs
vardefs = [
    ['HipMomentY', 'extrema', 'overall', 'max'],
    ['KneeMomentX', 'extrema', 'overall', 'max'],
    ['AnkleMomentX', 'extrema', 'overall', 'max'],
    ['AnklePowerZ', 'extrema', 'overall', 'max'],
    ['NormalisedGRFX', 'extrema', 'overall', 'min'],
    ['NormalisedGRFX', 'extrema', 'overall', 'max'],
]

# print(list(m.desc for m in plot_extracted_comparison(sessions, vardefs)))
# hist_comparison(sessions, vardefs)
box_comparison(sessions, vardefs)



# %% try go.Box

#fig = go.Figure()

fig = make_subplots(rows=2, cols=1)

for k in range(2):

    data = np.random.randn(300)
    x = ['G1'] * 100 + ['G2'] * 100 + ['G3'] * 100
    tracel = go.Box(y=data, x=x, name='L', offsetgroup='L')
    fig.append_trace(tracel, row=k+1, col=1)

    data = np.random.randn(300) + 1
    x = ['G1'] * 100 + ['G2'] * 100 + ['G3'] * 100
    tracer = go.Box(y=data, x=x, name='R', offsetgroup='R')
    fig.append_trace(tracer, row=k+1, col=1)



if True:
    fig.update_layout(
        boxmode='group'  # group together boxes of the different traces for each value of x
    )


gaitutils.viz.plot_misc.show_fig(fig)
