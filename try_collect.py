# -*- coding: utf-8 -*-
"""

testbench for collect_gait

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

from collect_gait import _write_workbook


logger = logging.getLogger(__name__)
