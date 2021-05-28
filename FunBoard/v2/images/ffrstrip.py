import sys
args = sys.argv[1:]
if args:
    f1 = args[0]
    if f1 != args[-1]:
        f2 = args[-1]
    else:
        f2 = f1 + '.rs'
    with open(f1,'rb') as f:
        data = f.read()
        f.close()
    data = data.rstrip(b'\xff')
    #data = data.rstrip(b'\x00')
    with open(f2,'wb') as f:
        f.write(data)
        f.close()

