import re
import os

mb='0xb4'
dir = os.getcwd()+'\\ate\\'

cfgList = ( 'fn0_smbus.cfg', 'fn3_smbus.cfg', 'fn5_smbus.cfg', 'fn10_smbus.cfg', )

def binstr2int(binstr):
    bitList = list(reversed(binstr))
    n = 0
    for i in range(len(bitList)):
        n += int(bitList[i])*2**i
    return n

def conv(fname = 'fn0_smbus.cfg', verbose=False):
    pass
    f = open(dir+fname, 'r')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        if re.search('^SMB', lines[i]):
            tokens = lines[i].split(',')
            cmd = tokens[0].split('(')[0].strip()
            smb = tokens[0].split('(')[1].strip()
            func = tokens[1].strip()
            addr = tokens[2].strip()
            valexp = tokens[3].split(')')[0].strip()
            if verbose:
                #print tokens
                print cmd,smb,func,addr,valexp
            if cmd == 'SMBWRITE_DWORD':
                lines[i] = 'mr.writed(%s, 0x%s, 0x%s, 0x%s)'%(mb, func, addr, valexp) + '\n'
            elif cmd == 'SMBWRITE': # write byte
                lines[i] = 'mr.writeb(%s, 0x%s, 0x%s, 0x%s)'%(mb, func, addr, valexp) + '\n'
            elif cmd == 'SMBREAD_DWORD':
                #print binstr2int(valexp)
                lines[i] = ''
                lines[i] += 'val = mr.readd(%s, 0x%s, 0x%s)'%(mb, func, addr) + '\n'
                lines[i] += 'if %s != val:'%hex(binstr2int(valexp)) + '\n'
                lines[i] += '    print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
            elif cmd == 'SMBREAD': # read byte
                lines[i] = ''
                lines[i] += 'val = mr.readb(%s, 0x%s, 0x%s)'%(mb, func, addr) + '\n'
                lines[i] += 'if %s != val:'%hex(binstr2int(valexp)) + '\n'
                lines[i] += '    print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
            else:
                # print lines[i]
                raise Exception('unexpected pattern')
            lines[i] += 'sys.stdout.write(".")' + '\n'
            if verbose:
                print lines[i]
        else:
            pass
    f = open(dir+fname.split('.')[0] + '.py', 'w')
    f.writelines('import mr\n')
    f.writelines('import reset\n')
    f.writelines('import sys\n')
    f.writelines('reset.initSeq(freq=200)\n\n')
    f.writelines(lines)
    f.close()
            
# 10:46 2011-6-8, for Helen Chen, print all read regs.        
def conv_1(fname = 'fn0_smbus.cfg', verbose=False):
    pass
    f = open(dir+fname, 'r')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        if re.search('^SMB', lines[i]):
            tokens = lines[i].split(',')
            cmd = tokens[0].split('(')[0].strip()
            smb = tokens[0].split('(')[1].strip()
            func = tokens[1].strip()
            addr = tokens[2].strip()
            valexp = tokens[3].split(')')[0].strip()
            if verbose:
                #print tokens
                print cmd,smb,func,addr,valexp
            if cmd == 'SMBWRITE_DWORD':
                lines[i] = 'mr.writed(%s, 0x%s, 0x%s, 0x%s)'%(mb, func, addr, valexp) + '\n'
            elif cmd == 'SMBWRITE': # write byte
                lines[i] = 'mr.writeb(%s, 0x%s, 0x%s, 0x%s)'%(mb, func, addr, valexp) + '\n'
            elif cmd == 'SMBREAD_DWORD':
                lines[i] = ''
                lines[i] += 'val = mr.readd(%s, 0x%s, 0x%s)'%(mb, func, addr) + '\n'
                # lines[i] += 'if %s != val:'%hex(binstr2int(valexp)) + '\n'
                # lines[i] += '    print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
                lines[i] += 'print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
            elif cmd == 'SMBREAD': # read byte
                lines[i] = ''
                lines[i] += 'val = mr.readb(%s, 0x%s, 0x%s)'%(mb, func, addr) + '\n'
                # lines[i] += 'if %s != val:'%hex(binstr2int(valexp)) + '\n'
                # lines[i] += '    print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
                lines[i] += 'print "----- ERR -----", "func:",hex(0x%s), "addr:",hex(0x%s), "exp:",hex(%s), "got:",hex(val)'%(func, addr, hex(binstr2int(valexp))) + '\n'
            else:
                # print lines[i]
                raise Exception('unexpected pattern')
            lines[i] += 'sys.stdout.write(".")' + '\n'
            if verbose:
                print lines[i]
        else:
            pass
    f = open(dir+fname.split('.')[0] + '.py', 'w')
    f.writelines('import mr\n')
    f.writelines('import reset\n')
    f.writelines('import sys\n')
    f.writelines('reset.initSeq(freq=200)\n\n')
    f.writelines(lines)
    f.close()
            

def run():
	for fname in cfgList:
		conv(fname=fname)
