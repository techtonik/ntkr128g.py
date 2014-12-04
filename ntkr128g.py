# Windows 128Gb Memory Limit
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

# signature to find
signature1 = '7C 11 8B 45 FC 85 C0 74 0A'  # test for failure
signature2 = '7C 10 8B 45 FC 85 C0 74 09'  # test for license

replacemnt =       'B8 00 00 02 00 90 90'  # patch


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

def copyntkr():
  pass # [ ]

print('[*] Checking if patch is present')
if not os.path.exists(patched):
  # [ ] also check that OS is eligible
  print('    ntkr128g.exe is not found..')
  print('[*] Copying ntkrnlpa.exe to ntkr128g.exe for patching..')
  shutil.copy(original, local)
  needsaction += 1
else:
  print('[*] Checking sizes')
  print('      ntkrnlpa.exe  %s' % os.path.getsize(original))
  print('      ntkr128g.exe  %s' % os.path.getsize(patched))
  if os.path.getsize(original) != os.path.getsize(patched):
    print('    Kernel 128Gb patch needs to be updated ')
    needsaction += 1
  print('[*] Copying ntkrnlpa.exe to ntkr128g.exe for patching..')
  shutil.copy(original, local)

#print('[*] Checking signature in ntkr128g.exe')
# [ ]


sys.exit(needsaction)
