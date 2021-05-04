# -*- coding: utf-8 -*-
"""

Calculate GDI for multiple c3d files.

@author: Jussi (jnu@iki.fi)
"""


# %% init
import gaitutils
import matplotlib.pyplot as plt
import numpy as np


vicon = gaitutils.nexus.viconnexus()


def _compute_gdi(c3dfile):
    """Compute GDI in Nexus for a given c3d file"""
    gdi_pipeline = 'Calculate GDI'  # Nexus pipeline name
    gaitutils.nexus._open_trial(c3dfile)
    gaitutils.nexus._run_pipelines(gdi_pipeline)


def _read_gdi():
    """Read GDI values from current Nexus trial"""
    gdi = dict()
    subj = gaitutils.nexus.get_subjectnames()
    for context in ['Left', 'Right']:
        this_gdi, exists = vicon.GetAnalysisParam(subj, f'{context}GDI')
        if not exists:
            raise RuntimeError('GDI value not available in Nexus')
        gdi[context] = this_gdi
    return gdi


# %% try it out

testdir = r"C:\Temp\D0061_VH\2019_2_11_PostOp10kk_VH"
c3dfiles = gaitutils.sessionutils.get_c3ds(testdir, trial_type='dynamic')

for c3dfile in c3dfiles:
    _compute_gdi(c3dfile)
    gdi = _read_gdi()
    print(c3dfile)
    print(gdi)
