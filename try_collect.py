# -*- coding: utf-8 -*-
"""

testbench for collect_gait

@author: Jussi (jnu@iki.fi)
"""


from collect_gait import utils
import datetime




# %%

date = datetime.datetime(2018, 3, 1)
rootdir = r"Z:\Userdata_Vicon_Server\1_Diplegia"


dirs = utils.get_sessiondirs(rootdir, newer_than=date)

for d in dirs:
    print(d)


