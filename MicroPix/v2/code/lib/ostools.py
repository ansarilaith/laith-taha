#----------------------- 
# notify
#-----------------------

print('LOAD: ostools.py') 

#----------------------- 
# notes
#-----------------------

# oct(os.stat(file)[0]) = '0o100000' = file
# oct(os.stat(file)[0]) = '0o40000'  = dir

#-----------------------
# imports
#-----------------------

import os

#-----------------------
# functions
#-----------------------

def abspath(fd):
    fd = fd.strip().rstrip('/')
    if not fd:
        return os.getcwd()
    elif fd[0] == '/':
        return fd
    else:
        return os.getcwd().rstrip('/')+'/'+fd

def pwd():
    return os.getcwd()

def cwd(d='/'):
    return os.chdir(d)

def listdir(d=''):
    return os.listdir(d)    

def stat(fd='/'):
    try:
        return os.stat(fd)
    except:
        return None

def fsize(f='/'):
    return os.stat(f)[6]
 
def isfile(f):
    s = stat(f)
    if s and oct(s[0])[-5] != '4':
        return True
    return False

def isdir(d):
    s = stat(d)
    if s and oct(s[0])[-5] == '4':
        return True
    return False

def exists(fd):
    return stat(fd) != None

def touch(f):
    try:
        d,f2 = f.rsplit('/',1)
        mkdir(d)
        with open(f,'wb') as f3:
            f3.close()
        return True
    except:
        return False   

def mkdir(d):
    try:
        d = [x.strip() for x in abspath(d).split('/') if x.strip()]
        path = ''
        for x in d:
            if path:
                path += '/'+x
            else:
                path = x
            if isdir(path):
                continue
            elif isfile(path):
                return False
            else:
                os.mkdir(path) # call to os.mkdir
        return path
    except:
        return False

def tree(d='',i=0):
    d = abspath(d)
    s = stat(d)
    if not s:
        return None
    x = d.split('/')[-1]
    if oct(s[0])[-5] != '4': # file
        print('file:',x,s[6])
    else: # dir
        if (not i) and d not in ('','/'):
            print(d.rsplit('/',1)[0])
        print('  '*i+'|-/'+x)
        i += 1
        listing = os.listdir(d)
        listing.sort()
        dl = []
        for x in listing:
            x2 = d.rstrip('/')+'/'+x
            s = stat(x2)
            if oct(s[0])[-5] != '4': # file
                print('  '*i+'|--'+x,s[6])
            else:
                dl.append(x2)
        for d in dl:
            tree(d,i)

def fmatch(df):
    df = abspath(df)
    s = stat(df)
    if s:
        return [df]
    d,f = df.rsplit('/',1)
    if (not f) or '*' not in f:
        return []
    ms = []
    if f.startswith('*'):
        for m in os.listdir(d):
            if m.endswith(f[1:]):
                ms.append(d+'/'+m)
    elif f.endswith('*'):
        for m in os.listdir(d):
            if m.startswith(f[:1]):
                ms.append(d+'/'+m)
    # add additional matching here
    return ms

def remove(df):
    ms = fmatch(df)
    fc1 = len(df)
    fc2 = 0
    success = False
    for df in ms:
        s = stat(df)
        if oct(s[0])[-5] != '4': # file
            print('REMOVE: f',df[-48:],end=' ')
            os.remove(df)
            print('DONE')
            fc2 += 1
        else: # dir
            while 1:
                df2 = os.listdir(df)
                if not df2:
                    break
                df2 = df+'/'+df2.pop(0)
                fc2 += remove(df2)
            print('REMOVE: d',df[-48:],end=' ')
            if df not in ('/','/sd'):
                os.rmdir(df)
                fc2 += 1
                print('DONE')
            else:
                print('NOT ALLOWED')
    return fc2

def cat(f):
    print('-'*32)
    with open(f) as f2:
        for line in f2:
            print(line.rstrip())
        f2.close()
    print('-'*32)
    print('FILE:',f.rsplit('/',1)[-1],stat(f)[6])
    
#-----------------------
# end
#-----------------------
