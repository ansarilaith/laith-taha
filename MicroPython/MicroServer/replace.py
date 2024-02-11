#!/usr/bin/python3

#-----------------------
# what is this?
#-----------------------

# This is a newer, smaller version of Clayton's REPLace.py.
# This loads dirs/files to a Micropython device using the default REPL.
# 
# This works from the working dir all the way down.
# It will build the same dir/file structure on the device.
# 
# This will remove Python comment lines (replace with single newline) to save space.
# This will stop reading Python files when it finds a "# end" comment line.
# 
# If mpy-cross is installed, it will pre-compile to .mpy first.
# Try "python3 -m pip install mpy-cross" or similar to install.

#-----------------------
# important variables
#-----------------------

# These files don't get loaded.
exclude_files = '''
replace.py
REPLace.py
*.md
*.bin
'''.split()

# These dirs are not loaded.
exclude_dirs = '''
__pycache__
archive*
hidden*
.*
'''.split()

#-----------------------
# clayton's to-do list 
#-----------------------

# make an option to run different versions of mpy-cross
# pipx install mpy-cross==1.18
# can be run normally as mpy-cross
# pipx install --suffix=_1.17 mpy-cross==1.17
# can be also run from command line as mpy-cross_1.17

#-----------------------
# imports
#-----------------------

import os
import sys
import time
import shutil
import argparse
import serial
import traceback
try:
    import mpy_cross
except:
    mpy_cross = None
    print()
    print('ERROR: mpy-cross NOT installed. No pre-compile.')
    print('IMPORTANT: Install mpy-cross.')
    print('Try "python3 -m pip install mpy-cross" or similar.')
    print()

# -----------------------
# default variables
# -----------------------

version = 3.0
port = '/dev/ttyUSB0'
verbose = False
use_mpy = True
make_mpy = True
delpy = False
dry_run = False
keeptemp = False
wdir = os.getcwd()
tempdir = 'replace_temp'
load_all = False
includes = []
excludes = exclude_files+exclude_dirs+[tempdir]
fileblocksize = 1024

#-----------------------
# handle command line
#-----------------------

epilog = f'''
examples:
  ./replace.py -p /dev/ttyUSB0 -a
  ./replace.py -p /dev/ttyUSB0 -i main.py test.py
  ./replace.py -p /dev/ttyUSB0 --xmpy -a

notes:
  "./REPLace.py" works the same as "python3 replace.py" for Linux.
  All options can be used together (they logically cancel each other).
  Either -a or -i must be used to load files (-a has precedence).
  This works from the working dir all the way down (recursive).
  It will build the same dir/file structure on the device.
  If mpy-cross is installed, it will pre-compile to .mpy first.
  The "main.py" and "boot.py" files are never compiled.
  This will remove comment lines (replace with \\n) to save space.
  This will stop reading when it finds a "# end" comment line.
  Buy beer for Clayton.
_
'''.strip()

parser = argparse.ArgumentParser(description='Load files to an ESP32 via the REPL',
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 epilog=epilog)
parser.add_argument('--version', action='version',version=f'replace.py {version}')
parser.add_argument('-p', dest='port', help='set the REPL port name')
parser.add_argument('-d', dest='wdir', help='set working dir (root) for files')
parser.add_argument('-v', action='store_true', help='flag: verbose, show loaded bytes')
parser.add_argument('-a', action='store_true', help='flag: load ALL non-exclude files')
parser.add_argument('-i', nargs='*', help='give filenames to INCLUDE in load')
parser.add_argument('-e', nargs='*', help='give filenames to EXCLUDE from load (add to defaults)')
parser.add_argument('-x', nargs='*', help='give filenames to NOT EXCLUDE (remove from defaults)')
parser.add_argument('-k', action='store_true', help='flag: keep (don\'t delete) temp files')
parser.add_argument('--xmpy', action='store_true', help="flag: don't compile to .mpy files")
parser.add_argument('--zmpy', action='store_true', help="flag: don't make/remake .mpy files")
parser.add_argument('--delpy', action='store_true', help="flag: delete .py files on device before .mpy load")
parser.add_argument('--dryrun', action='store_true', help="flag: don't load files, just test")

args = parser.parse_args()
if args.port:
    port = args.port
if args.wdir:
    wdir = os.path.abspath(args.wdir)
if args.a:
    load_all = True
if args.v:
    verbose = True
if args.k:
    keeptemp = True
if args.xmpy:
    use_mpy = False
if args.zmpy:
    make_mpy = False
if args.delpy:
    delpy = True
if args.dryrun:
    dry_run = True
if args.i:
    includes = [os.path.basename(f) for f in args.i]
includes = list(set(includes))
if args.e:
    excludes += [os.path.basename(f) for f in args.e]
excludes = list(set(excludes))
if args.x:
    for f in args.x:
        f = os.path.basename(f)
        if f in excludes:
            excludes.pop(excludes.index(f))

# -----------------------
# print basics
# -----------------------

div = '-'*64

print()
print(f'REPLace.py {version}')
print(div)
print('PORT:',port)
print('LOAD_ALL:',load_all)
print('FILE_ROOT:',wdir)

# -----------------------
# print excludes
# -----------------------

if excludes:
    excludes.sort()
    print(div)
    for f in excludes:
        print('EXCLUDE:',f)

# -----------------------
# iter over working dir
# -----------------------

if load_all:
    includes = set()
else:
    includes = set(includes)
loads = []
alldirs = set()

if load_all or includes:
    for root,dirs,files in os.walk(wdir):

        # drop bad dirs
        for d in dirs[:]:
            for x in excludes:
                if d == x:
                    dirs.remove(d)
                elif x.startswith('*') and d.endswith(x[1:]):
                    dirs.remove(d)
                elif x.endswith('*') and d.startswith(x[:-1]):
                    dirs.remove(d)

        # save good files
        files_saved_from_this_dir = set()
        for file in files:

            keepit = False

            # no specific excludes
            if excludes:
                excluded = False
                for x in excludes:
                    if file == x:
                        excluded = True
                        break
                    elif x.startswith('*') and file.endswith(x[1:]):
                        excluded = True
                        break
                    elif x.endswith('*') and file.startswith(x[:-1]):
                        excluded = True
                        break
                if excluded:
                    continue

            # all
            if load_all:
                keepit = True

            # specific include
            elif file in includes:
                keepit = True

            # save
            if keepit:

                # conditional select of mpy
                name,ext = os.path.splitext(file)
                
                # mpy file
                if ext.lower() == '.mpy':
                    if not use_mpy:
                        file = None

                # python file
                elif ext.lower() == '.py':

                    # don't use mpy
                    if not use_mpy:
                        pass

                    # don't make mpy (but use what you have)
                    elif not make_mpy:
                        if os.path.isfile(os.path.join(root,name+'.mpy')):
                            file = name+'.mpy'

                    # can't make mpy (so use what you have)
                    elif not mpy_cross:
                        if os.path.isfile(os.path.join(root,name+'.mpy')):
                            file = name+'.mpy'

                    # mpy already in list
                    elif name+'.mpy' in files_saved_from_this_dir:
                        file = None

                # make/save paths
                if file and file not in files_saved_from_this_dir:
                    path1 = os.path.join(root,file)
                    path2 = os.path.normpath(path1.replace(wdir,'').strip(os.sep))
                    loads.append((path2,path1))
                    alldirs.add(os.path.dirname(path2))
                    files_saved_from_this_dir.add(file)

alldirs = list(alldirs)
alldirs.sort()

# -----------------------
# print loads (includes)
# -----------------------

if loads:
    loads.sort()
    print(div)
    for p1,p2 in loads:
        print('INCLUDE:',p1)

# -----------------------
# dry run
# -----------------------

if dry_run:
    print(div)
    print(f'DRY RUN: 0 files loaded')
    print()
    exit(0)

# -----------------------
# serial
# -----------------------

if verbose:
    print(div)

rbuffer = ''

def recv():
    # clear recv into rbuffer
    global rbuffer
    while 1:
        data = connection.read(1024)
        if not data:
            break
        else:
            rbuffer += data.decode(encoding='utf-8', errors='?')

def send(line='',show=False,validate=None):
    global rbuffer
    connection.write([ord(x) for x in line+'\r'])
    time.sleep(0.1)
    recv()
    if validate and not rbuffer.rstrip().endswith(validate.strip()):
        print('VALIDATE:',[validate.strip()])
        print('R_BUFFER:',[rbuffer.rstrip()[-64:]])
        raise IOError('RECV buffer FAILED validation.')
    if show:
        print('BLOCK:', [' '.join(rbuffer.split(' '))])
    rbuffer = ''

# make connection
connection = serial.Serial(port=port,baudrate=115200,timeout=0.1)
if connection == None:
    raise Exception('SERIAL POER ERROR: Use -p PORT to specify a serial port.')

# prep REPL
connection.flush()
connection.write([3])  # clear = ctrl-c = 0x03
time.sleep(0.2)
send(show=verbose)
send('import os',show=verbose)
send('os.chdir("/")',show=verbose)

# -----------------------
# load dirs/files
# -----------------------

dc = 0
fc = 0

if loads:

    # make dirs
    if alldirs:
        print(div)
        dirsmade = set()
        for d in alldirs:
            subdirs = [x.strip() for x in d.split(os.sep) if x.strip()]
            if subdirs:
                for x in range(len(subdirs)):
                    d2 = os.path.join(*subdirs[:x+1])
                    if d2 in dirsmade:
                        continue
                    else:
                        print('MAKE DIR:',d2)
                        dirname,basename = os.path.split(d2)
                        if dirname:
                            send(f"if '{basename}' not in os.listdir('{dirname}'): os.mkdir('{dirname}/{basename}')\r\n",show=verbose)
                            send(f"'{basename}' in os.listdir('{dirname}')",show=verbose,validate='True\r\n>>>')
                        else:
                            send(f"if '{basename}' not in os.listdir(): os.mkdir('{basename}')\r\n",show=verbose)
                            send(f"'{basename}' in os.listdir()",show=verbose,validate='True\r\n>>>')
                        send()
                        dirsmade.add(d2)
                        dc += 1

    # make temp dir
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)
        
    # send files
    for p1,p2 in loads:

        # p1 is device path
        # p2 is local path

        print(div)
        print('LOADING:',p1)

        # make temp file
        temp = os.path.join(tempdir,os.path.basename(p1))

        # ext
        ext = os.path.splitext(p2)[1].lower()

        # clean all python files
        if ext == '.py':
            with open(p2) as infile:
                with open(temp,mode='w',newline='\n') as outfile:
                    for line in infile:
                        line2 = line.strip() # also removes \r
                        if not line2:
                            outfile.write('\n')
                        elif line2 == '# end':
                            break
                        elif line2.startswith('#'):
                            outfile.write('\n')
                        else:
                            outfile.write(line.rstrip()+'\n')
                    outfile.close()
                infile.close()

        # or just copy other files
        else:
            shutil.copyfile(p2,temp)

        # mpy-cross
        if ext == '.py' and use_mpy and make_mpy and mpy_cross and os.path.basename(p2) not in ('boot.py','main.py'):
            print('Cross Compile:',os.path.basename(p2),end=' ')
            base = temp[:] # local clean python file
            temp = temp.replace('.py','.mpy') # local mpy file
            p1 = p1.replace('.py','.mpy') # device mpy file
            if os.path.isfile(temp):
                os.remove(temp)
            mpy_cross.run('-o',temp,base).wait() # doesn't raise errors, use file existence
            print('done')
            if not os.path.isfile(temp):
                print('ERROR:',os.path.basename(p2),'does not compile.')
                print()
                print('COMPILE ERROR! replace.py STOPPED.')
                print()
                break

        # remove .py file from device if loading .mpy
        if delpy and temp.endswith('.mpy'):
            try:
                dirname,basename = os.path.split(p1.replace('.mpy','.py'))
                if dirname:
                    send(f"if '{basename}' in os.listdir('{dirname}'): os.remove('{dirname}/{basename}')\r\n",show=verbose)
                    send(f"'{basename}' not in os.listdir('{dirname}')",show=verbose,validate='True\r\n>>>')
                else:
                    send(f"if '{basename}' in os.listdir(): os.remove('{basename}')\r\n",show=verbose)
                    send(f"'{basename}' not in os.listdir()",show=verbose,validate='True\r\n>>>')
                send()
            except:
                print('ERROR: Unable to remove .py file from device.')

        # send temp file
        send_error = False
        for x in range(3):
            try:
                bc = 0
                send(f"outfile = open('{p1}',mode='wb')", show=verbose)
                infile = open(temp, mode='rb')
                while 1:
                    data = infile.read(fileblocksize)
                    if not data:
                        break
                    bc += len(data)
                    send(f"outfile.write({data})",show=verbose,validate=f'{len(data)}\r\n>>>')
                send("outfile.close()", show=verbose)
                if send_error:
                    print('RELOAD OKAY')
                print(f'LOADED: {bc} bytes OKAY')
                send_error = False
                break
            except Exception as e:
                send("outfile.close()",show=False)
                print(traceback.format_exc())
                if x <= 1:
                    print('RELOADING')
                send_error = True
                connection.write([3]) # clear = ctrl-c = 0x03
                time.sleep(0.2)
                connection.write([3]) # clear = ctrl-c = 0x03
                time.sleep(0.2)
        if send_error:
            raise Exception('FILE LOAD ERROR:',os.path.basename(p2))

        # count
        fc += 1

    # remove temp files
    if not keeptemp:
        shutil.rmtree(tempdir)

# -----------------------
# serial
# -----------------------

if verbose:
    print(div)
connection.write([3])  # clear = ctrl-c = 0x03
time.sleep(0.1)
send(show=verbose)
connection.close()

# -----------------------
# print done
# -----------------------

print(div)
print(f'DONE: {dc} dirs, {fc} files loaded')
print()

# -----------------------
# end
# -----------------------
