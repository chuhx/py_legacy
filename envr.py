#######################################################
# Montage Confidential                                #
# Copyright(c) Montage Technology, 2010               #
#                                                     #
# All rights reserved.                                #
# This is unpublished, confidential proprietary       #
# information.  Do not reproduce or redistribute      #
# without written permission.                         #
#                                                     #
# Author: Larry Chu                                   # 
# $Revision: 1.9 $                                    #
#######################################################

# This script initializes some environment parameters for the whole test suite after CTC is powered-up.


import sys
import os

pathNames =  []
pathNames.append(os.getcwd() + os.sep + 'analog')
pathNames.append(os.getcwd() + os.sep + 'ctcapi')
pathNames.append(os.getcwd() + os.sep + 'fpga')
pathNames.append(os.getcwd() + os.sep + 'lib')
pathNames.append(os.getcwd() + os.sep + 'mbapi')
pathNames.append(os.getcwd() + os.sep + 'mbist')
pathNames.append(os.getcwd() + os.sep + 'smbus')
pathNames.append(os.getcwd() + os.sep + 'testsuite')
pathNames.append(os.getcwd() + os.sep + 'mcu')
pathNames.append(os.getcwd() + os.sep + 'ate')

for onePath in pathNames:
	if onePath not in sys.path :
		sys.path.insert(2,onePath)
print sys.path

import ad
import cali
import mr
from mr import *
import reset
from reset import initSeq
from testlogging import logger
import time
import v
from v import pwrup
from v import pwrdn
import frequency

def rstctc():
	import USBPY
	if USBPY.open(0) == 0:
		print '\nUSB port is opened successfully.\n'
	else:
		raise Exception, 'USB port is not opened correctly.\n'
	
	reset.rstAll()	# after CTC's powered-up, the on-board fpga wrongly put reset pins to 0. So have to put them to 1.
	
	v.pwrdn()
	v.isPwrup = False

	print 'Initialize host powers to let the programm memorize their voltages'
	v.nowHostVolts = {}
	v.initHostPwr()	# let v.nowHostVolts record the voltages of host powers 
	
rstctc()

mr.rstsmb()


mb=0xb4
import mbist_loopback_b0 as ml
import misc
