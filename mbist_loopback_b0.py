#######################################################
# Montage Confidential                                #
# Copyright(c) Montage Technology, 2011               #
#                                                     #
# All rights reserved.                                #
# This is unpublished, confidential proprietary       #
# information.  Do not reproduce or redistribute      #
# without written permission.                         #
#                                                     #
# Author: Larry Chu                                   # 
# $Revision: 1.0 $                                    #
#######################################################


import mr
import v
import time
import reset
import random
import testlogging
import ana_check
import sys

logger = testlogging.Log()
mb = 0xb4 # default mb smbus address 


def printSpacePassOrFail(flag):
	if flag:
		print '.',
	else:
		print 'x',

def printDensePassOrFail(flag):
	if flag:
		sys.stdout.write('.')
	else:
		sys.stdout.write('x')

def printBytesList(aList):
	for aByte in aList:
		print '%02X\t'% aByte,
	print
	

# 2011-5-12
def getBit(aInt, bitPos):
	return aInt>>bitPos & 1

def bits2Int(bitList):
	byte = 0
	for i in range(len(bitList)):
		byte |= bitList[i]<<i
	return byte

# for data mapping
def twoNibble2TwoBurst(nib0,nib1):
	burstABits = []
	burstBBits = []
	for nib in [nib0,nib1]:
		for bitPos in (0,2,4,6):
			burstABits.append(getBit(nib,bitPos) )
		for bitPos in (1,3,5,7):
			burstBBits.append(getBit(nib,bitPos) )
	return bits2Int(burstABits), bits2Int(burstBBits)


# 2011-5-14	
def dramCaliNorm(mb=mb, freq=400):	
	if freq == 400:
		mr.wr(mb, mr.ldossel,	0 ) 
	elif freq == 533:
		mr.wr(mb, mr.ldossel,	1 ) 
	elif freq == 667:
		mr.wr(mb, mr.ldossel,	2 ) 
	else:
		raise Exception, 'freq must be 400, 533 or 667'
	mr.wr(mb, mr.mr0_cl, 	4 ) # 6 cycles
	mr.wr(mb, mr.mr2_cwl, 	1 ) # 6 cycles
	mr.wr(mb, mr.dcal_step_en, 1<<1) # dram side
	mr.wr(mb, mr.dcal_clken, 1)
	mr.wr(mb, mr.dcal_start, 1)
	# time.sleep(0.1)
	ck180NumOfSteps = mr.rd(mb, mr.dllcal_clkrx_360div2)
	# print ck180NumOfSteps
	return ck180NumOfSteps
	
def hostCali(mb=mb):	
	mr.wr(mb, mr.dcal_step_en, 1<<11) # host side
	mr.wr(mb, mr.dcal_clken, 1)
	mr.wr(mb, mr.dcal_start, 1)
	# time.sleep(0.1)
	mr.wr(mb, mr.int_hrx_lvl_fc0, mr.rd(mb, mr.int_htx_lvl_fc0) + 1)
	mr.wr(mb, mr.hrx_lvl_fc0, mr.rd(mb, mr.htx_lvl_fc0) )

# 2011-5-17		
def initMbistNorm(freq=400 ):
	ck180NumOfSteps = dramCaliNorm(mb=mb, freq=freq)
	mr.wr(mb, mr.byte_sel, 0x1ff)
	mr.wr(mb, mr.mtxdqdqs_n1_fc0, ck180NumOfSteps)
	mr.wr(mb, mr.mtxdqdqs_n0_fc0, ck180NumOfSteps)
	stepInNs = 1000.0/freq/2/ck180NumOfSteps
	tpdmInNs = 2.4
	mr.wr(mb, mr.mtx_lvl_n0_fc0, int(tpdmInNs/stepInNs) )
	mr.wr(mb, mr.mrx_lvl_n0_fc0, int(tpdmInNs/stepInNs) )
	mr.wr(mb, mr.mtx_lvl_n1_fc0, int(tpdmInNs/stepInNs) )
	mr.wr(mb, mr.mrx_lvl_n1_fc0, int(tpdmInNs/stepInNs) )		
	
	hostCali()

def dramCaliBy4(mb=mb):
	mr.wr(mb, mr.pll_by4_en,1 ) # by4 mode
	mr.wr(mb, mr.ldossel,	3 ) # 800MHz
	mr.wr(mb, mr.mr0_cl, 	4 ) # 6 cycles
	mr.wr(mb, mr.mr2_cwl, 	1 ) # 6 cycles
	mr.wr(mb, mr.dllcal_clken, 1)
	mr.wr(mb, mr.dllcal_en, 1)
	# time.sleep(0.1)
	mr.wr(mb, mr.dllcal_res_update, 1)
	ck180NumOfSteps = mr.rd(mb, mr.dllcal_clkrx_180)
	return ck180NumOfSteps	

# 14:25 2011-6-16, Wang Yong, turn on flag ate to cover more which is the case on ATE.
def initMbistBy4(freq=200, verbose=True, ate=True):
	ck180NumOfSteps = dramCaliBy4()
	
	mr.wr(mb, mr.byte_sel, 0x1ff)
	mr.wr(mb, mr.dllcal_clkrx_360div2, ck180NumOfSteps)
	mr.wr(mb, mr.dllcal_mrxdqdqs_90, ck180NumOfSteps/2-10)
	mr.wr(mb, mr.clkrx_180_fc0,     ck180NumOfSteps)
	mr.wr(mb, mr.dcc_htx_fc0      , 0)
	mr.wr(mb, mr.dcc_hrx_fc0      , 0)
	mr.wr(mb, mr.dcc_mrx_fc0      , 0)
	mr.wr(mb, mr.dcc_mtxdq_n1_fc0 , 0)
	mr.wr(mb, mr.dcc_mtxdqs_n1_fc0, 0)
	mr.wr(mb, mr.dcc_mtxdq_n0_fc0 , 0)
	mr.wr(mb, mr.dcc_mtxdqs_n0_fc0, 0)
	
	mr.wr(mb, mr.mrxdqdqs_neg_n1_fc0, ck180NumOfSteps/2-10)
	mr.wr(mb, mr.mrxdqdqs_pos_n1_fc0, ck180NumOfSteps/2-10)
	mr.wr(mb, mr.mrxdqdqs_neg_n0_fc0, ck180NumOfSteps/2-10)
	mr.wr(mb, mr.mrxdqdqs_pos_n0_fc0, ck180NumOfSteps/2-10)

	
	mr.wr(mb, mr.mtxdqdqs_n1_fc0, ck180NumOfSteps)
	mr.wr(mb, mr.mtxdqdqs_n0_fc0, ck180NumOfSteps)
	stepInNs = 1000.0/(freq*4)/2/ck180NumOfSteps  # *4 because of by4
	tpdmInNs = 2.4
	mr.wr(mb, mr.mtx_lvl_n0_fc0, int(tpdmInNs/stepInNs) )
	mr.wr(mb, mr.mtx_lvl_n1_fc0, int(tpdmInNs/stepInNs) )
	if not ate: 
		mr.wr(mb, mr.mrx_lvl_n0_fc0, int(tpdmInNs/stepInNs) )
		mr.wr(mb, mr.mrx_lvl_n1_fc0, int(tpdmInNs/stepInNs) )
		hostCali()	
	else: # 15:12 2011-6-16
		for i in range(4):
			if i==0 or i==2:
				mr.writed(mb, 10, 0x8c, 0x10300000)
			else:
				mr.writed(mb, 10, 0x8c, 0x103c0000)
			mr.writed(mb, 10, 0x04, 0x8d010000)
			for byteNum in range(9):
				mr.wr(mb, mr.byte_sel, 1<<byteNum)
				if i==0 or i==2:
					if not( getBit(mr.readd(mb, 10, 0xb4), 0)==0 and getBit(mr.readd(mb, 10, 0xb4), 8)==0 ):
						raise Exception('mrx leveling signal error')
				# else: # don't check this if dram is X4
					# if not( getBit(mr.readd(mb, 10, 0xb4), 0)==1 and getBit(mr.readd(mb, 10, 0xb4), 8)==1 ):
						# raise Exception('mrx leveling signal error')
			mr.wr(mb, mr.byte_sel, 0x1ff)	
				
		# 13:57 2011-6-16
		if verbose:
			print 'ck180:', ck180NumOfSteps
			print 'tpdm:', int(tpdmInNs/stepInNs) 
		mr.writed(mb, 10, 0x8c, 0x00340000)
		mr.writed(mb, 10, 0x04, 0x9d010000)
		mr.writed(mb, 10, 0x60, 0x80018000)
		mr.writed(mb, 10, 0x60, 0x80018004)
		for byteNum in range(9):
			mr.wr(mb, mr.byte_sel, 1<<byteNum)
			# if not getBit(mr.rd(mb, mr.pb_step_done_n0), 2) or not getBit(mr.rd(mb, mr.pb_step_done_n1), 2) or getBit(mr.rd(mb, mr.pb_step_fail_n0), 2) or getBit(mr.rd(mb, mr.pb_step_fail_n1), 2): # when dram is X4
			if not getBit(mr.rd(mb, mr.pb_step_done_n0), 2) or getBit(mr.rd(mb, mr.pb_step_fail_n0), 2) :# when dram is X8
				raise Exception('mrx fraction leveling cali fail')
		mr.wr(mb, mr.byte_sel, 0x1ff)
		mr.writed(mb, 10, 0x70, 0x00080000)
		mr.writed(mb, 10, 0x04, 0)
		mr.writed(mb, 10, 0x8c, 0)
		mr.writed(mb, 10, 0x60, 0x80000000)
		mr.writed(mb, 10, 0x60, 0)
		for byteNum in range(9):
			mr.wr(mb, mr.byte_sel, 1<<byteNum)
			if verbose:
				print 'byte%d:'%byteNum,
				print 'mrx_lvl_n0_fc0:', mr.rd(mb, mr.mrx_lvl_n0_fc0), '|',
				print 'mrx_lvl_n1_fc0:', mr.rd(mb, mr.mrx_lvl_n1_fc0), '|'
			if mr.rd(mb, mr.mrx_lvl_n0_fc0) < (int(tpdmInNs/stepInNs) - ck180NumOfSteps):
				mr.wr(mb, mr.mrx_lvl_n0_fc0, mr.rd(mb, mr.mrx_lvl_n0_fc0) + 2*ck180NumOfSteps )
			if mr.rd(mb, mr.mrx_lvl_n1_fc0) < (int(tpdmInNs/stepInNs) - ck180NumOfSteps):
				mr.wr(mb, mr.mrx_lvl_n1_fc0, mr.rd(mb, mr.mrx_lvl_n1_fc0) + 2*ck180NumOfSteps )
		
		mr.wr(mb, mr.mbdlpbken,	1  ) # enable dram loopback
		mr.wr(mb, mr.mbhlpbken,	1  ) # 13:50 2011-6-21
		mr.writed(mb, 10, 0x18, 0x08011e40)
		mr.writed(mb, 10, 0x18, 0x88011e40)
		time.sleep(0.2)
		if verbose:
			print 'dcal_done:', mr.rd(mb, mr.dcal_done)
			print 'dcal_fail:', mr.rd(mb, mr.dcal_fail)
			for byteNum in range(9):
				mr.wr(mb, mr.byte_sel, 1<<byteNum)
				print 'byte%d'%byteNum, '-'*60
				print 'mrxdqdqs_neg_n0_fc0',	mr.rd(mb, mr.mrxdqdqs_neg_n0_fc0)
				print 'mrxdqdqs_neg_n1_fc0',	mr.rd(mb, mr.mrxdqdqs_neg_n1_fc0)
				print 'mtxdqdqs_n0_fc0',		mr.rd(mb, mr.mtxdqdqs_n0_fc0)    
				print 'mtxdqdqs_n1_fc0',		mr.rd(mb, mr.mtxdqdqs_n1_fc0)    
				print 'mrx_lvl_n0_fc0',			mr.rd(mb, mr.mrx_lvl_n0_fc0)    
				print 'mrx_lvl_n1_fc0',			mr.rd(mb, mr.mrx_lvl_n1_fc0)    
	
		mr.wr(mb, mr.byte_sel, 0x1ff)
		mr.wr(mb, mr.mtxdqdqs_n1_fc0, ck180NumOfSteps)
		mr.wr(mb, mr.mtxdqdqs_n0_fc0, ck180NumOfSteps)
		
		# 9:46 2011-6-21
		mr.wr(mb, mr.int_hrx_lvl_fc0, mr.rd(mb, mr.int_htx_lvl_fc0) + 1)
		mr.wr(mb, mr.hrx_lvl_fc0, mr.rd(mb, mr.htx_lvl_fc0) )

# merge norm and by4	
def initMbist(freq=200, mode='by4'):
	if mode == 'by4':
		initMbistBy4(freq=freq, verbose=False, ate=True)
	elif mode == 'norm':
		initMbistNorm(freq=freq)
	else:
		raise Exception("argument mode must be 'by4' or 'norm'")

def startMbist( freq=400, dataType='fix', fixedPattern=3, userFrame=None, seed=0, \
				maskOfBytes=None ):
		
	mr.wr(mb, mr.mbdlpbken,	1  ) # enable dram loopback	
	mr.wr(mb, mr.mbhlpbken,	1  ) # enable host loopback	
	mr.wr(mb, mr.mbcseq, 	0 ) # a bug by Monica
	mr.wr(mb, mr.mbcmd, 	1 )
	
	if dataType == 'fix':
		mr.wr(mb, mr.mbdtype,	0 ) # fixed
		mr.wr(mb, mr.mbfixed,	fixedPattern ) 
	elif dataType == 'lsfr':
		mr.wr(mb, mr.mbdtype,	3 ) # lsfr
		mr.wr(mb, mr.mblfsrsed,	seed)
	elif dataType == 'user':
		mr.wr(mb, mr.mbdtype,	1 )
		def bytes2Dword(bytesList):
			dword = 0
			for i in range(len(bytesList)):
				dword |= bytesList[i]<<(i*8)
			return dword	
		udfFunc = 3
		udfAddrPerByte = ( (0x40,0x60), (0x44,0x64), (0x48,0x68), (0x4c,0x6c), (0x50,0x70), (0x54,0x74), (0x58,0x78), (0x5c,0x7c), (0xd0, 0xd4) )
		for i in range(len(udfAddrPerByte)): # write to all MB_UDF_B*B*	at func3
			mr.writed(mb, udfFunc, udfAddrPerByte[i][0], bytes2Dword(userFrame[i][0:4]) ) 	
			mr.writed(mb, udfFunc, udfAddrPerByte[i][1], bytes2Dword(userFrame[i][4:8]) ) 	
			# print '%x: %08x'%(udfAddrPerByte[i][0], mr.readd(mb, 3, udfAddrPerByte[i][0]) ),
			# print '%x: %08x'%(udfAddrPerByte[i][1], mr.readd(mb, 3, udfAddrPerByte[i][1]) )
	elif dataType == 'cir': # circular shift
		mr.wr(mb, mr.mbdtype,	2 )
		mr.wr(mb, mr.mblfsrsed,	seed)
	else:
		raise Exception, '%s data-type is not defined'%dataType
	
	# mr.wr(mb, mr.mbatype, 	3 )	# 1: single addr in mbtXXX | 2: start/end range defined in mbsXXX/mbeXXX | 3: full range of dimm
	mr.wr(mb, mr.mbatype, 	2 )	# 1: single addr in mbtXXX | 2: start/end range defined in mbsXXX/mbeXXX | 3: full range of dimm
	mr.wr(mb, mr.mbfast,	1 )
	mr.wr(mb, mr.mbscol, 	0 )
	mr.wr(mb, mr.mbecol, 	256 ) # Monica 2011-5-16
	mr.wr(mb, mr.mbalgo, 	0 )
	mr.wr(mb, mr.mbden, 	2 ) # 0: 144 bits | 1: 288 bits | 2: 572 bits
	
	if maskOfBytes != None:
		maskRegs = (mr.mb_rx_msk_b0, 
					mr.mb_rx_msk_b1, 
					mr.mb_rx_msk_b2, 
					mr.mb_rx_msk_b3, 
					mr.mb_rx_msk_b4, 
					mr.mb_rx_msk_b5, 
					mr.mb_rx_msk_b6, 
					mr.mb_rx_msk_b7, 
					mr.mb_rx_msk_b8,)
		for i in range(len(maskOfBytes)):
			mr.wr(mb, maskRegs[i], maskOfBytes[i])
	
	mr.wr(mb, mr.mbstart, 1 )
	while mr.rd(mb, mr.mbstart):
		time.sleep(0.1)
		pass
	# return 'fail' if mr.rd(mb, mr.mbpf) else 'pass' 
	return mr.rd(mb, mr.mbpf)

# 17:54 2011-6-29
# fixed, lsfr and circular data-type. both norm and by4 mode. also add some arguments.
def run(mode='by4', freq=200, dataType='fix', resetPwr=True, verbose=False, workaround=True, burst4=False, dramX8=False, seed=None, vreg=None):
	if resetPwr: reset.initSeq(freq=freq, verbose=verbose)
	if workaround:
		mr.wr(mb, mr.dly_ck_ca, 0 ) # 14:47 2011-5-23, choose the best timing
		mr.wr(mb, mr.dq_regulator_ctrl, 1) # a bug, 14:16 2011-5-25
	if dramX8: mr.wr(mb, mr.drmx8, 1)
	if vreg != None: mr.wr(mb, mr.vreg_value, vreg)
	
	initMbist(freq=freq, mode=mode)
	
	if burst4: mr.wr(mb, mr.mr0_bl, 2) # fixed burst-length 4
	else: mr.wr(mb, mr.mr0_bl, 0) # fixed burst-length 8

	if seed == None:  seed=random.randrange(2**32)
	if dataType == 'user': raise Exception('runUser() is for user-defined mbist')
	else: pf = startMbist(freq=freq, dataType=dataType, seed=seed)

	if verbose:
		for byteNum in range(9):
			mr.wr(mb, mr.byte_sel, 1<<byteNum)
			dramBursts = [0]*8
			hostBursts = [0]*8
			nibbleSel = ( (4,20, 0,16), (5,21, 1,17), (6,22, 2,18), (7,23, 3,19), )
			def getNib(sel):
				mr.wr(mb, mr.dq_rdout_sel, sel)
				return mr.rd(mb, mr.dq_rdout)
			for j in range(len(nibbleSel)):
				dramBursts[j], dramBursts[j+4]  = twoNibble2TwoBurst(getNib(nibbleSel[j][0]),getNib(nibbleSel[j][1]))
				hostBursts[j-1], hostBursts[j+4-1]  = twoNibble2TwoBurst(getNib(nibbleSel[j][2]),getNib(nibbleSel[j][3])) # -1 to left circular shift
			print 'byte%d '%byteNum + '-'*80 
			print 'dram:',; printBytesList( dramBursts )
			print 'host:',; printBytesList( hostBursts )
			
		print 'mrxdqdqs_neg_n1_fc0',	mr.rd(mb, mr.mrxdqdqs_neg_n1_fc0), '|',
		print 'mtxdqdqs_n0_fc0',		mr.rd(mb, mr.mtxdqdqs_n0_fc0),     '|',
		print 'mtx_lvl_n0_fc0',			mr.rd(mb, mr.mtx_lvl_n0_fc0),      '|',
		print 'mrx_lvl_n0_fc0',			mr.rd(mb, mr.mrx_lvl_n0_fc0),      '|',
		print 'flag', 'x' if pf else '.'
	return pf
	
# user-defined mbist
# 16:48 2011-6-28, merge burst8 and burst4
def runUser(mode='by4', freq=200, resetPwr=True, verbose=False, printPf=True, workaround=True, burst4=False, dramX8=False, \
			vreg=None, valOf_hdqoi=None, valOf_mdq_vref_sel=None, valOf_mrx_lvl_n0_fc0=None, valOf_hrx_lvl_fc0=None ):
	if resetPwr: reset.initSeq(freq=freq, verbose=verbose)
	
	if workaround:
		mr.wr(mb, mr.dly_ck_ca, 0 ) # 14:47 2011-5-23, choose the best timing
		mr.wr(mb, mr.dq_regulator_ctrl, 1) # a bug, 14:16 2011-5-25
		# mr.wr(mb, mr.vreg_prcs_cmpnst, 0 ) # 17:58 2011-5-25, increase vreg by 15mV
	if dramX8: mr.wr(mb, mr.drmx8, 1)
	
	# shmooed parameters
	if vreg != None: mr.wr(mb, mr.vreg_value, vreg)
	if valOf_hdqoi != None:
		mr.wr(mb, mr.hdqoi, valOf_hdqoi) # 18:15 2011-5-25, change dq drive strength: 2 is 48ohm, 4 is 20ohm, 0 is 40ohm
		mr.wr(mb, mr.ddqoi, valOf_hdqoi)
	if valOf_mdq_vref_sel != None:
		mr.wr(mb, mr.byte_sel, 0x1ff)
		mr.wr(mb, mr.mdq_vref_sel, valOf_mdq_vref_sel) # 9:56 2011-5-26, adjust vref to the middle	
		mr.wr(mb, mr.hdq_vref_sel, valOf_mdq_vref_sel)	
	
	initMbist(freq=freq, mode=mode)
	
	# shmooed parameters
	mr.wr(mb, mr.byte_sel, 0x1ff)
	if valOf_mrx_lvl_n0_fc0 != None:
		mr.wr(mb, mr.mrx_lvl_n0_fc0, valOf_mrx_lvl_n0_fc0 )
		mr.wr(mb, mr.mrx_lvl_n1_fc0, valOf_mrx_lvl_n0_fc0 )
	if valOf_hrx_lvl_fc0 != None:
		mr.wr(mb, mr.hrx_lvl_fc0, valOf_hrx_lvl_fc0 )

	if burst4:
		mr.wr(mb, mr.mr0_bl, 2) # set burst-length to 4
		mr.wr(mb, mr.nopcnt, 0xff) # insert nop between bursts
		validStartBurst = 1		# ignore burst0 and burst3 because they are not captured correctly at host side
		validEndBurst = 2
	else:
		mr.wr(mb, mr.mr0_bl, 0) # set burst-length to 8
		validStartBurst = 0
		validEndBurst = 7
	
	userFrame = []
	for byteNum in range(9):
		byteList = []
		for burstNum in range(8):
			byteList.append(random.randrange(0x100) )
		userFrame.append(byteList)
	# for byteNum in range(9):
		# userFrame.append([0xff,0x22,0x33,0xaa] + [0]*4)
	
	pf = startMbist(freq=freq, dataType='user', userFrame=userFrame ) #, maskOfBytes=[0xff]*7 + [0,0] 
	
	dramCmpFlags = [0]*9; hostCmpFlags = [0]*9 # 9 bytes
	for byteNum in range(9):
		mr.wr(mb, mr.byte_sel, 1<<byteNum)
		dramBursts = [0]*8; hostBursts = [0]*8
		nibbleSel = ( (4,20, 0,16), (5,21, 1,17), (6,22, 2,18), (7,23, 3,19), )
		def getNib(sel):
			mr.wr(mb, mr.dq_rdout_sel, sel)
			return mr.rd(mb, mr.dq_rdout)
		for j in range(len(nibbleSel)):
			dramBursts[j], dramBursts[j+4]  = twoNibble2TwoBurst(getNib(nibbleSel[j][0]),getNib(nibbleSel[j][1]))
			hostBursts[j-1], hostBursts[j+4-1]  = twoNibble2TwoBurst(getNib(nibbleSel[j][2]),getNib(nibbleSel[j][3])) # -1 to left circular shift
		if burst4: hostBursts[3], hostBursts[7] = hostBursts[7], hostBursts[3] # bursts 4~7 are invalid
		
		if userFrame[byteNum][validStartBurst : validEndBurst+1] != dramBursts[validStartBurst : validEndBurst+1]: dramCmpFlags[byteNum] = 1
		if userFrame[byteNum][validStartBurst : validEndBurst+1] != hostBursts[validStartBurst : validEndBurst+1]: hostCmpFlags[byteNum] = 1
		
		if verbose:
			print 'byte%d '%byteNum #+ '-'*80 
			# print 'expect :',; printBytesList( userFrame[byteNum][validStartBurst : validEndBurst+1] )
			# print 'dram   :',; printBytesList( dramBursts[validStartBurst : validEndBurst+1] )
			# print 'host   :',; printBytesList( hostBursts[validStartBurst : validEndBurst+1] )
			
			dramXor = []; hostXor = []
			for k in range(8):
				dramXor.append(userFrame[byteNum][k] ^ dramBursts[k])
				hostXor.append(userFrame[byteNum][k] ^ hostBursts[k])
			def print8Bits(aListOfInt):
				for k in range(len(aListOfInt)):
					sys.stdout.write('|')
					for bitPos in range(8):
						printDensePassOrFail(not getBit(aListOfInt[k],bitPos) )
				print
			print 'dramxor:',; print8Bits(dramXor[validStartBurst : validEndBurst+1] )
			print 'hostxor:',; print8Bits(hostXor[validStartBurst : validEndBurst+1] )
			
	if verbose:
		print 'mrxdqdqs_neg_n1_fc0',	mr.rd(mb, mr.mrxdqdqs_neg_n1_fc0), '|',
		print 'mtxdqdqs_n0_fc0',		mr.rd(mb, mr.mtxdqdqs_n0_fc0),     '|',
		print 'mtx_lvl_n0_fc0',			mr.rd(mb, mr.mtx_lvl_n0_fc0),      '|',
		print 'mrx_lvl_n0_fc0',			mr.rd(mb, mr.mrx_lvl_n0_fc0),      '|'
	
	if printPf: printDensePassOrFail( not(pf or reduce(lambda a,b: a|b, dramCmpFlags) or reduce(lambda a,b: a|b, hostCmpFlags) ) )
	return pf, dramCmpFlags, hostCmpFlags

# 14:34 2011-6-9, for Jianwei to print data captured at host side with different lsfr seed
def runLsfr(mode='by4', freq=200, resetPwr=True, verbose=True, workaround=True, burst4=False, dramX8=False, seed=None, vreg=None):
	if resetPwr: reset.initSeq(freq=freq, verbose=0)
	if workaround:
		mr.wr(mb, mr.dly_ck_ca, 0 ) # 14:47 2011-5-23, choose the best timing
		mr.wr(mb, mr.dq_regulator_ctrl, 1) # a bug, 14:16 2011-5-25
	if dramX8: mr.wr(mb, mr.drmx8, 1)
	if vreg != None: mr.wr(mb, mr.vreg_value, vreg)
	
	initMbist(freq=freq, mode=mode)

	if burst4: mr.wr(mb, mr.mr0_bl, 2) # fixed burst-length 4
	else: mr.wr(mb, mr.mr0_bl, 0) # fixed burst-length 8
	
	if seed == None:  seed=random.randrange(2**32)
	pf = startMbist(freq=freq, dataType='lsfr', seed=seed )
	
	if verbose:
		print '*'*50
		print 'data captured at host side is as below'
		print '-'*40
		for byteNum in range(9):
			print 'byte%d: '%byteNum,
			mr.wr(mb, mr.byte_sel, 1<<byteNum)
			nibbleSel = ( 0,1,2,3,16,17,18,19 )
			for sel in nibbleSel:
				mr.wr(mb, mr.dq_rdout_sel, sel)
				hostNib = mr.rd(mb, mr.dq_rdout)
				print '%3d'%hostNib, 
			print
		print '-'*40
		print 'mblfsrsed:', mr.rd(mb, mr.mblfsrsed)
		
		print 'flag', 'x' if pf else '.'
	return pf


def normLoop(n=5):
	freqs = (400,533,667)
	for freq in freqs:
		reset.initSeqNoPrint(freq)
		for i in range(n):
			runUser(mode='norm', freq=freq, verbose=False, resetPwr=False)
		print
	v.pwrdn()
				
def by4Loop(n=100, freq=233, vreg=2):
	print '-'*80
	print 'freq | vreg | flag | dramcmp byte0-8 | hostcmp byte0-8 '
	print '-'*80
	for cycleId in range(n):
		print freq*4,'|', # by4 mode
		pf, dramCmpFlags, hostCmpFlags = runUser(mode='by4', freq=freq, vreg=vreg, printPf=0)
		print mr.rd(mb, mr.vreg_value),
		sys.stdout.write(' | ')
		printSpacePassOrFail(not pf)
		sys.stdout.write(' | ')
		for flag in dramCmpFlags: printSpacePassOrFail(not flag)
		sys.stdout.write(' | ')
		for flag in hostCmpFlags: printSpacePassOrFail(not flag)
		print


# 15:09 2011-6-3
def shmooVref(n=500, freq=233):
	reset.initSeq(freq)
	for valOf_vreg_value in (2,):
		for valOf_hdqoi in (0,4): # change dq drive strength: 2 is 48ohm, 4 is 20ohm, 0 is 40ohm
			for valOf_mdq_vref_sel in range(8):
				failCnt = 0
				for cycleId in range(n):
					reset.rstAll(waitTime=0, verbose=False)
					pf, dramCmpFlags, hostCmpFlags = runUser(mode='by4', freq=freq, vreg=valOf_vreg_value, printPf=False, resetPwr=False,  valOf_mdq_vref_sel=valOf_mdq_vref_sel, valOf_hdqoi=valOf_hdqoi )
					printDensePassOrFail(not pf)
					if pf: failCnt += 1
				print '| freq:', freq*4, # by4 mode
				print '| vreg_value:', mr.rd(mb, mr.vreg_value),
				print '| hdqoi:', mr.rd(mb, mr.hdqoi),
				print '| mdq_vref_sel:', mr.rd(mb, mr.mdq_vref_sel),
				print '| %3d fails in %-3d'%(failCnt, n)

# 15:08 2011-6-3
def shmoo_mrx_lvl(freq=200, step=8):
	reset.initSeq(freq)
	for val in range(160, 272, step):
		print '| freq:', freq*4, # by4 mode
		reset.rstAll(waitTime=0, verbose=False)
		pf, dramCmpFlags, hostCmpFlags = runUser(mode='by4', resetPwr=False, freq=freq, printPf=False, valOf_mrx_lvl_n0_fc0=val )
		print '| vreg_value:', mr.rd(mb, mr.vreg_value),
		print '| mrx_lvl_n0_fc0:', mr.rd(mb, mr.mrx_lvl_n0_fc0),
		print '| flag:', 'x' if pf else '.'

def shmoo_hrx_lvl(freq=200, step=8):
	reset.initSeq(freq)
	for val in range(0, 208, step):
		print '| freq:', freq*4, # by4 mode
		reset.rstAll(waitTime=0, verbose=False)
		pf, dramCmpFlags, hostCmpFlags = runUser(mode='by4', resetPwr=False, freq=freq, printPf=False, valOf_hrx_lvl_fc0=val )
		print '| vreg_value:', mr.rd(mb, mr.vreg_value),
		print '| hrx_lvl_fc0:', mr.rd(mb, mr.hrx_lvl_fc0),
		print '| flag:', 'x' if pf else '.',
		sys.stdout.write(' | ')
		for flag in dramCmpFlags: printSpacePassOrFail(not flag)
		sys.stdout.write(' | ')
		for flag in hostCmpFlags: printSpacePassOrFail(not flag)
		print

# 16:14 2011-6-3
def errInj(mode='by4', freq=200):
	reset.initSeq(freq=freq)
	mr.wr(mb, mr.eibits_b0, 1<<0)
	mr.wr(mb, mr.eibits_b1, 1<<1)
	mr.wr(mb, mr.eibits_b2, 1<<2)
	mr.wr(mb, mr.eibits_b3, 1<<3)
	mr.wr(mb, mr.eibits_b4, 1<<4)
	mr.wr(mb, mr.eibits_b5, 1<<5)
	mr.wr(mb, mr.eibits_b6, 1<<6)
	mr.wr(mb, mr.eibits_b7, 1<<7)
	mr.wr(mb, mr.eibits_b8, 1<<0)
	runUser(mode=mode, freq=freq, resetPwr=0, verbose=1,)



















