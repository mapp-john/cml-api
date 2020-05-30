# Import Required Modules
import os
import re
import json
import random
import netaddr
from getpass import getpass
from virl2_client import ClientLibrary as cmlClient



#
#
#
# Define Password Function
def define_password():
    password = None
    while not password:
        password = getpass('Please Enter API Password: ')
        passwordverify = getpass('Re-enter API Password to Verify: ')
        if not password == passwordverify:
            print('Passwords Did Not Match Please Try Again')
            password = None
    return password


#
#
#
# Define Get All Lab Details
# Returns Dictionary
def GetAllLabDetails(cml):
    labs = cml.get_lab_list()
    d = {}
    count = 1
    for l in labs:
        d[str(count)] = {}
        lab = cml.join_existing_lab(l)
        D = lab.details()
        d[str(count)].update(D)
        count += 1
    return d


