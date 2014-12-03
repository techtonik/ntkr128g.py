# Windows 128Gb Memory Limit
# (thanks to Geoff Chappell for original research)
# http://www.geoffchappell.com/notes/windows/license/memory.htm

# Check if patch for 128Gb Windows NT extensions is up to date
#
# [ ] check that size of ntkrnlpa.exe and ntkr128g.exe (patched) matches
#   [ ] read File Version in .exe for reporting
#   [ ] find if 


import ctypes    # using Windows API directly
import ctypes.wintypes

def system32(name):
  """return unicode path to filename in system32 dir"""

  CSIDL_SYSTEM = 0x25       # Windows system folder
  pathbuf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
  ctypes.windll.shell32.SHGetSpecialFolderPathW(0, pathbuf, CSIDL_SYSTEM, 0)
  return pathbuf.value + '\\' + name

original = system32('ntkrnlpa.exe')
patched = system32('ntkr128g.exe')


warnings = 0

import os

print('[*] Checking sizes')
print('      ntkrnlpa.exe  %s' % os.path.getsize(original))
print('      ntkr128g.exe  %s' % os.path.getsize(patched))
if os.path.getsize(original) != os.path.getsize(patched):
  print('WARNING: kernel 128Gb patch needs upgrading')
  warnings += 1


import sys
sys.exit(warnings)
