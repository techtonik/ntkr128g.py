# Windows 4Gb memory limit patcher (unlocks access to 128Gb)
# (thanks to Geoff Chappell for original research)
# http://www.geoffchappell.com/notes/windows/license/memory.htm

# Check if patch for 128Gb Windows NT extensions is up to date
#
# [x] check that size of ntkrnlpa.exe and ntkr128g.exe (patched) matches
#   [x] read File Version in .exe for reporting
#   [ ] find signature in new original file
#     [ ] show previous offsets for known File Versions and new
# [ ] find all occurences of signature
#   [ ] fail if > 2
# [ ] patch
# [ ] report

import os
import sys
import shutil

import ctypes    # using Windows API directly
import ctypes.wintypes

PY3K = sys.version_info >= (3, 0)

def dehex(hextext):
  if PY3K:
    return bytes.fromhex(hextext)
  else:
    hextext = "".join(hextext.split())
    return hextext.decode('hex')


# signature to find
signature1 = dehex('7C 11 8B 45 FC 85 C0 74 0A')  # test for failure
signature2 = dehex('7C 10 8B 45 FC 85 C0 74 09')  # test for license
replacemnt = dehex(      'B8 00 00 02 00 90 90')  # patch


needsaction = 0


def system32(name):
  """return unicode path to filename in system32 dir"""

  CSIDL_SYSTEM = 0x25       # Windows system folder
  pathbuf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
  ctypes.windll.shell32.SHGetSpecialFolderPathW(0, pathbuf, CSIDL_SYSTEM, 0)
  return pathbuf.value + '\\' + name

original = system32('ntkrnlpa.exe')
patched = system32('ntkr128g.exe')
local = 'ntkr128g.exe'


def checksum(filename):
  PTSTR = ctypes.c_char_p
  headersum  = ctypes.wintypes.DWORD()
  checksum = ctypes.wintypes.DWORD()
  ctypes.windll.imagehlp.MapFileAndCheckSumA(
    PTSTR(filename), ctypes.byref(headersum), ctypes.byref(checksum))
  return (headersum.value, checksum.value)


def getdword(filename, offset):
  bindata = open(filename, 'rb').read()

  class Memory(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
      ('value', ctypes.wintypes.DWORD),
    ]

  memdword = Memory()
  ctypes.memmove(ctypes.addressof(memdword), bindata[offset:], 4)
  #print "dword: 0x%08X" % memdword.value
  return memdword.value

def setdword(filename, offset, value):
  #memdword = Memory()
  #memdword.value = 3333
  #b = ctypes.c_uint32(0x99887766)
  #print ctypes.string_at(ctypes.pointer(b), 4)
  #print memdword.value
  #print ctypes.string_at(ctypes.pointer(memdword.value), 4)
  import struct
  bytestr = struct.pack("<L", value)
  with open(filename, 'r+b') as fw:
    fw.seek(offset)
    fw.write(bytestr)
    fw.close()


def checksumoffset(filename):
  # -- calculate offset of checksum data by parsing PE header
  ntheadoff = getdword(filename, 0x3c)  # lfanew
  # 0x18 OptionalHeader, 0x40 there is CheckSum
  offset = ntheadoff + 0x18 + 0x40
  return offset
  



def copykernel(original, local):
  print('    ..copy ntkrnlpa.exe to ntkr128g.exe')
  # [ ] preserve timestamp
  shutil.copy(original, local)

def offset(signature, local):
  return open(local, 'rb').read().find(signature)


# --- checking ---
print('[*] Checking if patch is present')
if not os.path.exists(patched):
  # [ ] also check that OS is eligible
  print('    ntkr128g.exe is not found..')
  needsaction += 1
else:
  print('[*] Checking sizes')
  print('      ntkrnlpa.exe  %s' % os.path.getsize(original))
  print('      ntkr128g.exe  %s' % os.path.getsize(patched))
  if os.path.getsize(original) != os.path.getsize(patched):
    print('    Kernel 128Gb patch needs to be updated ')
    needsaction += 1
  else:
    print('[*] Checking signature in ntkr128g.exe')
    sign1off = offset(signature1, local)
    sign2off = offset(signature2, local)
    # [ ] check that signature is present multiple times
    if sign1off == -1 and sign2off == -1:
      # [ ] explicit check for patched
      print('    signatures are not found - may be already patched')
   # [ ] check already patched

# --- patching ---
if needsaction:
  print('[*] Patching ntkr128g.exe..')
  copykernel(original, local)
  sign1off = offset(signature1, local)
  sign2off = offset(signature2, local)
  if sign1off == -1 and sign2off == -1:
    sys.exit("Error: Signatures not found. Aborting..")
  print('[*] Checking signature offsets..')
  print('    0x%08X, 0x%08X' % (sign1off, sign2off))
  with open(local, 'r+b') as fw:
    print('[*] Patching signature1..')
    fw.seek(sign1off + 2)
    fw.write(replacemnt)
    print('[*] Patching signature2..')
    fw.seek(sign2off + 2)
    fw.write(replacemnt)
    fw.close()
  sign1off = offset(signature1, local)
  sign2off = offset(signature2, local)
  if sign1off == -1 and sign2off == -1:
    print('    Patch Successful.')
  else:
    sys.exit('Error: Signatures are still there')

  print('[*] Original/New checksums:')
  newsums = checksum(local)
  print('      Header: 0x%08X, Actual: 0x%08X' % checksum(original))
  print('      Header: 0x%08X, Actual: 0x%08X' % newsums)
  offset = checksumoffset(local)
  csum = getdword(local, offset)
  print('      Header: 0x%08X' % csum)

  print('[*] Correcting checksum')
  setdword(local, offset, newsums[1])
  newsums = checksum(local)
  print('      Header: 0x%08X, Actual: 0x%08X' % newsums)
  print('Done.')

  print('\nMove the %s to %s and follow the instructions at' % (local, patched))
  print('http://www.geoffchappell.com/notes/windows/license/memory.htm (Digital Signature)')
