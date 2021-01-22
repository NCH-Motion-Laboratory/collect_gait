# -*- coding: utf-8 -*-
"""

plot histograms from extracted values

TODO:

titles are not centered
add JP defined vars
    -obtain both peaks for GRFZ?
add ylabels as in gait curve plots
extract num. values into pdf report (table format)

    plt.table
        https://towardsdatascience.com/simple-little-tables-with-matplotlib-9780ef5d0bc4
        looks bad buggy

    create html table, use weasyprint -> png, then use matplotlib image functions
        -weasyprint is hard to get working :(

    create plotly table, save into png, insert into matplotlib






halutut muuttujat:

	nilkan asento (koukistusarvo) alkukontaktissa (IC)
	polven asento (ojennusarvo) alkukontaktissa IC
	lonkan koukistuskulma alkukontaktissa
	nilkan koukistuskulman arvo tukivaiheen lopulla (stance, esim. kohta 40 tai 45% ) tai nilkan maksimi koukistusarvo tukivaiheessa
	polven ojennus tukivaiheen lopulla (stance, esim. kohta 40 tai 45% ) tai polven maksimi ojennusarvo tukivaiheessa
	Lonkan maksimi ojennusarvo tukivaiheessa
	polven maksimi koukistus heilahdusvaiheessa.
•	(polven ojennus heilahdusvaiheen lopulla  - KYSEENALAINEN, SAMA KUIN ALKUKONTAKTISSA?)
	lonkan maksimi koukistusarvo heilahdusvaiheessa

+ muuttujat JP:n paperista:

    peak hip abductor moment




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
from gaitutils.viz.plot_plotly import _get_plotly_axis_labels, plot_extracted_box
from gaitutils import cfg
import logging

# logging.basicConfig(level=logging.DEBUG)


# %% read the data
# let's get all sessions under this dir...
rootdir = r"Z:\Userdata_Vicon_Server"
rootdir = r"C:\Temp\D0063_RR"
rootdir = r"Y:\Userdata_Vicon_Server\1_Diplegia\D0063_RR"

# ...newer than this date
date = datetime.datetime(2018, 1, 1)
# tags for dynamic trials
tags = ['E1', 'E2', 'E3', 'T1', 'T2', 'T3']
substrings = None

sessions = list(utils.get_sessiondirs(rootdir, newer_than=date, substrings=substrings))

session_trials = {
    session: gaitutils.sessionutils._get_tagged_dynamic_c3ds_from_sessions(
        session, tags=cfg.eclipse.tags
    )
    for session in sessions
}


allvars = [vardef[0] for vardefs in cfg.report.vardefs.values() for vardef in vardefs]
from_models = set(gaitutils.models.model_from_var(var) for var in allvars)
curve_vals = {
    session: gaitutils.stats._trials_extract_values(trials, from_models=from_models)
    for session, trials in session_trials.items()
}

# %% box plot
for title, vardefs in cfg.web_report.vardefs.items():
    fig = plot_extracted_box(curve_vals, vardefs)
    fig['layout']['title'] = title
    gaitutils.viz.plot_misc.show_fig(fig)


# %%
import numpy as np
import matplotlib.pyplot as plt

title_text = 'Loss by Disaster'
footer_text = 'June 24, 2020'
fig_background_color = 'skyblue'
fig_border = 'steelblue'
table = [
    ['Freeze', 'Wind', 'Flood', 'Quake', 'Hail'],
    ['5 year', 66386, 174296, 75131, 577908, 32015],
    ['10 year', 58230, 381139, 78045, 99308, 160454],
    ['20 year', 89135, 80552, 152558, 497981, 603535],
    ['30 year', 78415, 81858, 150656, 193263, 69638],
    ['40 year', 139361, 331509, 343164, 781380, 52269],
]
# Pop the headers from the data array
column_headers = table.pop(0)
row_headers = [x.pop(0) for x in table]
# Table data needs to be non-numeric text. Format the data while I'm at it.
cell_text = []
for row in table:
    cell_text.append([f'{x/1000:1.1f}' for x in row])
# Get some lists of color specs for row and column headers
rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
ccolors = plt.cm.BuPu(np.full(len(column_headers), 0.1))
# Create the figure. Setting a small pad on tight_layout
# seems to better regulate white space. Sometimes experimenting
# with an explicit figsize here can produce better outcome.
plt.figure(
    linewidth=2,
    edgecolor=fig_border,
    facecolor=fig_background_color,
    tight_layout={'pad': 1},
    # figsize=(5,3)
)
# Add a table at the bottom of the axes
the_table = plt.table(
    cellText=cell_text,
    rowLabels=row_headers,
    rowColours=rcolors,
    rowLoc='right',
    colColours=ccolors,
    colLabels=column_headers,
    loc='center',
)
# Scaling is the only influence we have over top and bottom cell padding.
# Make the rows taller (i.e., make cell y scale larger).
the_table.scale(1, 1.5)  # Hide axes
ax = plt.gca()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
# Hide axes border
plt.box(on=None)  # Add title
plt.suptitle(title_text)  # Add footer
plt.figtext(
    0.95, 0.05, footer_text, horizontalalignment='right', size=6, weight='light'
)
# Force the figure to update, so backends center objects correctly within the figure.
# Without plt.draw() here, the title will center on the axes and not the figure.
plt.draw()
# Create image. plt.savefig ignores figure edge and face colors, so map them.
fig = plt.gcf()
plt.savefig(
    'pyplot-table-demo.png',
    # bbox='tight',
    edgecolor=fig.get_edgecolor(),
    facecolor=fig.get_facecolor(),
    dpi=150,
)


# %%
import numpy as np
import matplotlib.pyplot as plt


title_text = 'Loss by Disaster'
footer_text = 'June 24, 2020'
table = [
    ['Freeze', 'Wind', 'Flood', 'Quake', 'Hail'],
    ['5 year', 66386, 174296, 75131, 577908, 32015],
    ['10 year', 58230, 381139, 78045, 99308, 160454],
    ['20 year', 89135, 80552, 152558, 497981, 603535],
    ['30 year', 78415, 81858, 150656, 193263, 69638],
    ['40 year', 139361, 331509, 343164, 781380, 52269],
]
# Pop the headers from the data array
column_headers = table.pop(0)
row_headers = [x.pop(0) for x in table]
# Table data needs to be non-numeric text. Format the data while I'm at it.
cell_text = []
for row in table:
    cell_text.append([f'{x/1000:1.1f}' for x in row])
# Create the figure. Setting a small pad on tight_layout
# seems to better regulate white space. Sometimes experimenting
# with an explicit figsize here can produce better outcome.

plt.figure(
    linewidth=2,
    tight_layout={'pad': 1},
    # figsize=(5,3)
)


# %% fun

from gaitutils.viz.plot_matplotlib import _plot_tabular_data
from gaitutils import models

table = [
    ['Freeze', 'Wind', 'Flood', 'Quake', 'Hail'],
    ['5 year', 66386, 174296, 75131, 577908, 32015],
    ['10 year', 58230, 381139, 78045, 99308, 160454],
    ['20 year', 89135, 80552, 152558, 497981, 603535],
    ['30 year', 78415, 81858, 150656, 193263, 69638],
    ['40 year', 139361, 331509, 343164, 781380, 52269],
]
# Pop the headers from the data array
column_headers = table.pop(0)
row_headers = [x.pop(0) for x in table]
# Table data needs to be non-numeric text. Format the data while I'm at it.
data = []
for row in table:
    data.append([f'{x/1000:1.1f}' for x in row])


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
    themodel = models.model_from_var(varname)
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


# nvars = len(vardefs)
# subtitles = [_compose_varname(nested_keys) for nested_keys in vardefs]

# _plot_tabular_data(data, row_headers, column_headers)


# %% box plot
for title, vardefs in cfg.report.vardefs.items():
    row_labels = [_compose_varname(vardef) for vardef in vardefs]
    col_labels = [
        session + '_%s' % ctxt for session in curve_vals.keys() for ctxt in 'LR'
    ]
    _plot_tabular_data(data, row_labels, col_labels)


# %% massage curve_vals data into rows

from matplotlib.backends.backend_pdf import PdfPages

page_size = (11.69, 8.27)  # report page size = landscape A4


col_labels = [
    op.split(session)[-1] + ' / %s' % ctxt
    for session in curve_vals.keys()
    for ctxt in 'LR'
]

pdfpath = 'C:\\Temp\\foo.pdf'


def _var_unit(vardef):
    """Return unit for a vardef"""
    varname = vardef[0]
    themodel = models.model_from_var(varname)
    return themodel.units[varname]
    if unit == 'deg':
        unit = u'\u00B0'  # Unicode degree sign
    return unit


with PdfPages(pdfpath) as pdf:
    for title, vardefs in cfg.report.vardefs.items():
        row_labels = [_compose_varname(vardef) for vardef in vardefs]
        table = list()
        for vardef in vardefs:
            row = list()
            for session, session_vals in curve_vals.items():
                for ctxt in 'LR':
                    vardef_ctxt = [ctxt + vardef[0]] + vardef[1:]
                    this_vals = _nested_get(
                        session_vals, vardef_ctxt
                    )  # returns list of values for given session and context = column
                    mean, std = np.mean(this_vals), np.std(this_vals)
                    unit = _var_unit(vardef_ctxt)
                    if unit == 'deg':
                        unit = u'\u00B0'  # Unicode degree sign
                    else:
                        unit = ' ' + unit
                    row.append('%.2f±%.2f%s' % (mean, std, unit))
            table.append(row)
        fig = _plot_tabular_data(table, row_labels, col_labels)
        fig.set_size_inches(*page_size)
        pdf.savefig(fig)


# %% massage curve_vals data into rows

from matplotlib.backends.backend_pdf import PdfPages

page_size = (11.69, 8.27)  # report page size = landscape A4

fn = op.split(gaitutils.envutils._named_tempfile(suffix='.pdf'))[-1]
pdfpath = 'C:\\Temp\\%s' % fn


with PdfPages(pdfpath) as pdf:
    for title, vardefs in cfg.report.vardefs.items():
        fig = gaitutils.viz.plot_matplotlib._plot_extracted_table2(curve_vals, vardefs)
        fig.set_size_inches(*page_size)
        fig.suptitle('Curve extracted values: %s' % title)
        pdf.savefig(fig)



# %% plotly -> png bytestream -> matplotlib -> pdf 
# requires 
import plotly.graph_objects as go
import os.path as op
import gaitutils
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io


page_size = (11.69, 8.27)  # report page size = landscape A4


fig = go.Figure(data=[go.Table(header=dict(values=['A Scores', 'B Scores']),
                 cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
                     ])
fig.show()

fn = op.split(gaitutils.envutils._named_tempfile(suffix='.png'))[-1]
figpath = 'C:\\Temp\\%s' % fn

bytes = fig.to_image(format='png', engine='kaleido', width=1600, height=1200)
bio = io.BytesIO(bytes)
im = plt.imread(bio, format='png')

#mfig = plt.figure()
#mfig.figimage(im)
mfig, axes = plt.subplots()
mfig.set_size_inches(*page_size)
mfig.set_dpi(200)
axes.imshow(im)

plt.show()

fn = op.split(gaitutils.envutils._named_tempfile(suffix='.pdf'))[-1]
pdfpath = 'C:\\Temp\\%s' % fn
with PdfPages(pdfpath) as pdf:
    pdf.savefig(mfig)



