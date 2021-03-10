# Software Development Kit (SDK) for the EZIoT.link Application Programmer Interface (API).
# In other words, the SDK for the EZIoT API.
# This is designed to work in Python3.5+ and Micropython1.10+

#----------------------------------------------
# user variables
#----------------------------------------------

# the default key and secret "EXAMPLE" is a user
# that everybody can use to test things out

# you will need to use get_creds() to get your
# own account (unless you just like sharing)

api_key = 'EXAMPLE' 
api_secret = 'EXAMPLE'
api_version = 1

#----------------------------------------------
# general variables
#----------------------------------------------

api_base_path = 'https://eziot.link/api'

#----------------------------------------------
# imports
#----------------------------------------------

# micropython option
try:
    import usys # this will fail for python
    import time
    import urequests as requests
    import ujson as json
    from urandom import randint   

# default to regular python
except:
    import time
    import requests
    import json
    from random import randint

#----------------------------------------------
# micropython-only imports
#----------------------------------------------

# note: you can delete the above section and
# use the imports below if you are only using
# this module in a micropython device

##import urequests as requests
##import ujson as json
##from urandom import randint   

#----------------------------------------------
# network functions (not used directly)
#----------------------------------------------

def _check_error(code,jdata):

    # error
    if code != 200 or not jdata.get('success',False):
        message = 'Request error: code: {}, detail: {}'.format(code,jdata.get('message','unknown reason'))
        raise Exception(message)

    # okay
    return True

def _make_request(route,data={},timeout=10):

    # make path
    route = '{}/v{}/{}'.format(api_base_path,float(api_version),route)

    # set up auth
    key,secret,n = None,None,randint(-16,32)
    if api_key:
        key = ''.join((chr(ord(c)+n) for c in api_key))
    if api_secret:
        secret = ''.join((chr(ord(c)+n) for c in api_secret))
    auth = [key,secret,n]

    # make packet
    assert type(data) == dict
    data['auth'] = auth
    packet = json.dumps(data)

    # request
    resp = requests.post(route,data=packet,headers={'Content-Type':'application/json'},timeout=timeout)

    # build return
    code = resp.status_code
    try:
        jdata = resp.json()
    except:
        jdata = {'json_parse_error':resp.text}

    # done
    return code,jdata

#----------------------------------------------
# general functions
#----------------------------------------------

# get stats for data table
def stats():
    '''Get the current state of your data.
    RETURN: dict of item:value pairs'''

    # make request
    code,jdata = _make_request('stats')

    # error
    _check_error(code,jdata)

    # return dict
    return jdata.get('stats',{})

#----------------------------------------------
# data functions
#----------------------------------------------

# insert a row of data, return rowid of insert
def post_data(group=None,device=None,data1=None,data2=None,data3=None,data4=None):
    '''Insert a row of data. No values are required.
    RETURN: rowid (id number) if inserted data'''

    # build data
    # only send non-None values
    data = {}

    # check general data types and string lengths
    # this is a pre-check, the server also checks
    for name,value,length in (('group',group,32),
                              ('device',device,32),
                              ('data1',data1,32),
                              ('data2',data2,32),
                              ('data3',data3,32),
                              ('data4',data4,256)):
        if value != None:
            if type(value) == str:
                assert len(value) <= length
            else:
                assert type(value) in (int,float)
            data[name] = value

    # make request
    code,jdata = _make_request('data/post',data)

    # error
    _check_error(code,jdata)

    # return rowid
    return jdata.get('rowid',0)

# get rows of data
def get_data(count=1,after=None,group=None,device=None,sort=None):
    '''Get rows of data. Limit return using "after", "group", "device".
    count = 1-1024 (how many rows to return)
    after = rowid (only rows after this rowid)
    group = "groupname" (only rows with this group name)
    device = "devicename" (only rows with this device name)
    sort = "asc" or "desc" (sort on rowids, default descending)
    RETURN: list of data row lists [[row],[row],...]
    row = [rowid,epoch,gmt,ip,group,device,data1,date2,data3,data4]
    '''

    # build data
    # only send non-None values
    data = {}

    # count
    assert type(count) == int and count > 0
    data['count'] = count

    # check general data types and string lengths
    for name,value in (('group',group),('device',device),('sort',sort)):
        if value != None:
            if type(value) == str:
                assert len(value) <= 32
            else:
                assert type(value) in (int,float)
            data[name] = value

    # after
    if after != None:
        assert type(after) == int
        data['after'] = after

    # make request
    code,jdata = _make_request('data/get',data)

    # error
    _check_error(code,jdata)

    # return rowid
    return jdata.get('rows',[])

# delete rows of data, return count of rows deleted
def delete_data(rowids=[],before=None,xall=False):
    '''Delete rows of data. !!!This is PERMANENT!!!
    rowids = int or list (a rowid of a list of rowids)
    before = rowid (delete all rowids before this rowid)
    xall = True|False (delete all rows)
    RETURN: count of deleted rows
    '''

    # build data
    # only send non-None values
    data = {}

    # rowids
    if rowids:
        assert type(rowids) in (int,list,tuple)
        if type(rowids) == int:
            data['rowids'] = [rowids]
        else:
            data['rowids'] = [int(x) for x in rowids]

    # before
    if before != None:
        assert type(before) == int
        data['before'] = before

    # xall
    if xall:
        data['xall'] = True

    # make request
    code,jdata = _make_request('data/delete',data)

    # error
    _check_error(code,jdata)

    # return rowid count
    return jdata.get('rows',0)

#----------------------------------------------
# note: once you have your credentials, you can
# delete the next section. you don't need the 
# get_creds() function on your micropython device
#----------------------------------------------

#----------------------------------------------
# user credentials functions 
#----------------------------------------------

def get_creds():
    '''Get your own credentials based on your email.
    Verification data and credentials are sent to your email.
    Just follow the prompts.'''

    # get email
    email,email2 = None,'cats and dogs'
    while email != email2:
        email  = prompt('What is your email address?')
        email2 = prompt('Re-type your email address?')
        if email != email2:
            print("Email addresses don't match!")
    print('EMAIL:',email)

    # check email
    print('Checking email...')
    code,jdata = _make_request('creds',{'email':email,'action':'check'})
    known = jdata.get('success',False)

    # known email options
    if known:
        print('EZIot knows this email.')
        print('You can resend or reset your credentials.')
        if prompt('Do you want to RESEND your credentials?',True):
            code,jdata = _make_request('creds',{'email':email,'action':'resend'})
            if not jdata.get('success',False):
                if '429' in jdata.get('message',''):
                    print('You can only resend every 10 minutes.')
                else:
                    print('Something went wrong: {}'.format(jdata.get('message','unknown error')))
                print('Try again later.')
                return
            else:
                print('Your new credentials have been sent to your email address.')
        elif prompt('Do you want to RESET your credentials?',True):
            print('If you reset, you will have to change the the credentials in all your device.')
            if prompt('Are you sure you want to RESET your credentials?',True):
                code,jdata = _make_request('creds',{'email':email,'action':'reset'})
                if not jdata.get('success',False):
                    if '429' in jdata.get('message',''):
                        print('You can only reset every 10 minutes.')
                    else:
                        print('Something went wrong: {}'.format(jdata.get('message','unknown error')))
                    print('Try again later.')
                    return
                else:
                    print('Your new credentials have been sent to your email address.')

    # unknown
    else:
        print('This is a new email.')
        if not prompt('Do you want to create a new user account?',True):
            print('Okay. Ending get_creds() script.')
            return
        print('\nPlease read and acknowledge the following statements:\n')
        time.sleep(2)
        for condition in conditions:
            block(condition)
        if not prompt('Do you concur, acknowledge and agree?',True):
            print('Okay. Closing credentials script.')
            return
        print("\nOkay. I'm requesting a validation code...")
        code,jdata = _make_request('creds',{'email':email,'action':'new'})
        if not jdata.get('success',False):
            print('Something went wrong: {}'.format(jdata.get('message','unknown error')))
            print('Try again later.')
            return
        print('A validation code has been sent to your email address.')
        vcode = prompt('What is the validation code?')
        print("I'm checking the code...")
        code,jdata = _make_request('creds',{'email':email,'action':'new','code':vcode})
        if not jdata.get('success',False):
            print('Something went wrong: {}'.format(jdata.get('message','unknown error')))
            print('Try again later.')
            return
        print('\nYour new credentials have been sent to your email address.')

def prompt(prompt,yn=False):
    line = input(prompt+'> ')
    line = line.strip()
    if line.lower() == 'q':
        raise KeyboardInterrupt
    if not yn:
        return line
    if line.lower().startswith('y'):
        return True
    return False

def block(s,width=72):
    s = s.split()
    ll = 0
    for word in s:
        if ll + len(word) > width:
            print('\n'+word,end=' ')
            ll = len(word) + 1
        else:
            print(word,end=' ')
            ll += len(word) + 1
    print()
    print()

conditions = [

'''EZIot.link is a free, experimantal service provided for the benefit of Clayton Darwin's Patreon supporters.
Although anyone can test the service, data and accounts from non-supporters may be deleted at any time.
Typically non-supporter accounts are purged overnight between 1:00 and 2:00 GMT -5:00.''',

'''EZIot.link should not be used to transmit or store any sensitive or confidential information.
Although EZIot.link uses HTTPS encryption and industry-best practices, data security is not guaranteed.''',

'''EZIot.link should not be used to transmit or store any data or information that is critical to commercial, medical, or military infrastructure or systems.
EZIot.link is an experimental service targeted at developers and hobbyists and is subject to change, evolve, or even be removed.
There is currently no guarantee of long-term support.''',

'''EZIot.link should not be used for any activity deemed illegal by the United States of America
or by any county from which data/information is produced or consumed.
Any violation will result in the user, account, and email being permanently blocked from the service,
and the illegal activities being reported to the proper authorities.''',

'''I understand that EZIot.link does not store user data apart from the user's assigned data table.
I understand that any delete operation is permanent and unrecoverable.
I understand that once my data table is full, posting new data will cause the permanent deletion of old data.''',

'''I understand that my EZIot.link credentials (key and secret) must be kept private.
I understand that anyone with my key and secret can use them to load, view and delete data on my EZIot.link account.
I understand that anyone with my key and secret can use them to reset my credentials and potentially lock me out of my own account.''',

'''As a user of EZIot.link, I will not abuse the EZIot.link service, system, or server.
I understand EZIot.link is a community service and will do my best to be a considerate and helpful member of the user community.
I will work diligently to insure my applications have the least possible amount of interactions with the server,
and I will never attempt to view/hack/manipulate another users' data without express permission.''',

    ]

#----------------------------------------------
# end
#----------------------------------------------
