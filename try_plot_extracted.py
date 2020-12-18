# -*- coding: utf-8 -*-
"""

plot histograms from extracted values

TODO:

L/R column titles
avg/stddev lines?
JP defined vars
x axis scaling

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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from gaitutils.viz.plot_plotly import _get_plotly_axis_labels
from gaitutils.viz.plot_common import _cyclical_mapper
from gaitutils import cfg

# let's get all sessions under this dir...
rootdir = r"Z:\Userdata_Vicon_Server"
rootdir = r"C:\Temp\D0063_RR"
rootdir = r"C:\Users\hus20664877\vicon_data\D0063_RR"
# ...newer than this date
date = datetime.datetime(2018, 1, 1)
# tags for dynamic trials
tags = ['E1', 'E2', 'E3', 'T1', 'T2', 'T3']
substrings = None


# %% try out plotting

sessions = utils.get_sessiondirs(rootdir, newer_than=date, substrings=substrings)


def plot_extracted_comparison(sessions, vardefs):
    """Plot comparison of session extracted values as histogram"""

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
            name += ', %s phase %s' % (phase, val_trans[valtype])
        return name

    def _var_unit(vardef):
        """Return unit for a vardef"""
        varname = vardef[0]
        themodel = gaitutils.models.model_from_var(varname)
        return themodel.units[varname]

    # find the necessary models
    models = set(gaitutils.models.model_from_var(vardef[0]) for vardef in vardefs)
    # extract the curve values
    vals = {
        session: gaitutils.stats._extract_values(session, models)
        for session in sessions
    }

    ctxts = ['Left', 'Right']
    subtitles = [
        _compose_varname(nested_keys) for nested_keys in vardefs for ctxt in ctxts
    ]

    nvars = len(vardefs)
    fig = make_subplots(rows=nvars, cols=2, subplot_titles=subtitles)
    legendgroups = set()
    trace_colors = _cyclical_mapper(cfg.plot.colors)

    # plot the histogram for each session
    for session, session_vals in vals.items():
        for row, vardef in enumerate(vardefs):
            for col, ctxt in enumerate('LR'):
                vardef_ctxt = [ctxt + vardef[0]] + vardef[1:]
                hist_x = _nested_get(session_vals, vardef_ctxt)
                show_legend = session not in legendgroups
                legendgroups.add(session)
                hist = go.Histogram(
                    x=hist_x,
                    name=session,
                    legendgroup=session,
                    showlegend=show_legend,
                    opacity=0.5,
                    marker_color=trace_colors[session],
                )
                fig.append_trace(hist, row=row + 1, col=col + 1)
                ylabel = _var_unit(vardef)
                xlabel = 'N'
                xaxis, yaxis = _get_plotly_axis_labels(row, col, ncols=2)
                fig['layout'][yaxis].update(
                    title={
                        'text': xlabel,
                        'standoff': 0,
                    }
                )
                fig['layout'][xaxis].update(
                    title={
                        'text': ylabel,
                        'standoff': 0,
                    }
                )
    # Overlay both histograms
    fig.update_layout(barmode='overlay')
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.75)
    gaitutils.viz.plot_misc.show_fig(fig)


# example vardefs
vardefs = [
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

# print(list(m.desc for m in plot_extracted_comparison(sessions, vardefs)))
plot_extracted_comparison(sessions, vardefs)


