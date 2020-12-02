# -*- coding: utf-8 -*-
"""

testbench for collect_gait

@author: Jussi (jnu@iki.fi)
"""


from collect_gait import utils
import datetime



# let's get all sessions under this dir...
rootdir = r"Z:\Userdata_Vicon_Server\1_Diplegia"
# ...newer than this date
date = datetime.datetime(2019, 3, 1)


dirs = utils.get_sessiondirs(rootdir, newer_than=date)

for d in dirs:
    print(d)



