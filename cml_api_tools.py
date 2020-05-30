# Import Required Modules
import os
import re
import sys
import csv
import json
import socket
import random
import netaddr
from virl2_client \
        import ClientLibrary \
        as cmlClient
# Import custom modules from file
from cml_api_modules import \
        define_password,\
        GetAllLabDetails


#
#
#
# Define Blank URL Get Script as Function
def BlankGet(cml):
    print ('''
***********************************************************************************************
*                             Basic URL GET Script                                            *
*_____________________________________________________________________________________________*
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. URI Path (/api/v0/node_definitions)                                                     *
*                                                                                             *
*  2. Save output to file                                                                     *
*                                                                                             *
*                                                                                             *
***********************************************************************************************
''')

    # Request API URI Path
    api_path = input('Please Enter URI: ').lower().strip()

    # Clean URI
    if (api_path[-1] == '/'):
        api_path = api_path[:-1]

    # Set URL
    url = f'{cml.url}{api_path}'
    if url[-1] == '/':
        url = url[:-1]

    # Perform API GET call
    print(f'Performing API GET to: {url}')
    try:
        # REST call with SSL verification turned off:
        s = cml.session
        r = s.get(url,verify=False)
        status_code = r.status_code
        resp = r.json()
        if (status_code == 200):
            print('GET successful...')
            # Ask if output should be saved to File
            save = input('Would You Like To Save The Output To File? [y/N]: ').lower()
            if save in (['yes','ye','y']):
                # Random Generated JSON Output File
                filename = ''
                for i in range(6):
                    filename += chr(random.randint(97,122))
                filename += '.txt'
                print(f'*\n*\nRANDOM LOG FILE CREATED... {filename}\n')
                with open(filename, 'a') as OutFile:
                    OutFile.write(json.dumps(resp,indent=4))
            elif save in (['no','n','']):
                print(json.dumps(resp,indent=4))
        else:
            r.raise_for_status()
            print(f'Error occurred in GET --> {resp}')
    except requests.exceptions.HTTPError:
        print(f'Error in connection --> {traceback.format_exc()}')
        print(json.dumps(resp,indent=4))
    # End
    finally:
        try:
            if r: r.close()
        except:
            None


#
#
#
# Define Topology Download Function
def TopoDownload(cml):
    print ('''
***********************************************************************************************
*                             Download Topology for Lab                                       *
*_____________________________________________________________________________________________*
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. Select which lab to download                                                            *
*                                                                                             *
*  2. Topology will automatically be saved to current directory                               *
*                                                                                             *
***********************************************************************************************
''')
    # Get Lab details and request user to select lab if multiple
    labs = cml.get_lab_list()
    if len(labs) == 0:
        print('\nNo labs found...\n\n')
        return
    elif len(labs) == 1:
        lab = cml.join_existing_lab(labs[0])
        d = lab.details()
        print(f'Downloading topology for lab: {d["lab_title"]}')
        url = f'{cml.url}/api/v0/labs/{d["id"]}/topology'
    else:
        d = GetAllLabDetails(cml)
        print('''
***********************************************************************************************
*                             Please select lab to download                                   *
***********************************************************************************************
''')
        for k,v in d.items():
            print(f'{k}. Title: {v["lab_title"]}, Description: {v["lab_description"]}\n')
        I = ''
        while I not in d:
            I = input('Selection: ')
            if I not in d:
                print('Invalid Selection...\n')
        url = f'{cml.url}/api/v0/labs/{d[I]["id"]}/topology'

    #TODO: YAML or JSON format, with/without configurations
    # Perform API GET call
    print(f'Performing API GET to: {url}')
    try:
        # REST call with SSL verification turned off:
        s = cml.session
        r = s.get(url,verify=False)
        status_code = r.status_code
        resp = r.json()
        if (status_code == 200):
            print('GET successful...')
            # Ask if output should be saved to File
            save = input('Would You Like To Save The Output To File? [y/N]: ').lower()
            if save in (['yes','ye','y']):
                # Random Generated JSON Output File
                filename = f'{resp["lab_title"]}_v{resp["version"]}.json'
                print(f'*\n*\nTopology File Created... {filename}\n')
                with open(filename, 'a') as OutFile:
                    OutFile.write(json.dumps(resp,indent=4))
            elif save in (['no','n','']):
                print(json.dumps(resp,indent=4))
        else:
            r.raise_for_status()
            print(f'Error occurred in GET --> {resp}')
    except requests.exceptions.HTTPError:
        print(f'Error in connection --> {traceback.format_exc()}')
        print(json.dumps(resp,indent=4))
    # End
    finally:
        try:
            if r: r.close()
        except:
            None






#
#
#
# Run Script if main
if __name__ == "__main__":
    #
    #
    #
    # Initial input request
    print ('''
***********************************************************************************************
*                                                                                             *
*              Cisco Modeling Labs v2.0 API Tools (Written for Python 3.6+)                   *
*                                                                                             *
***********************************************************************************************
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. FQDN for CML server (hostname.domain.com)                                               *
*                                                                                             *
*  2. API Username                                                                            *
*                                                                                             *
*  3. API Password                                                                            *
*                                                                                             *
***********************************************************************************************
''')

    Test = False
    while not Test:
        # Request CML server FQDN
        server = input('Please Enter CML fqdn: ').lower().strip()

        # Validate FQDN
        if server[-1] == '/':
            server = server[:-1]
        if server.startswith('https://') or server.startswith('http://'):
            server = server.replace('http://','').replace('https://','')

        # Perform Test Connection To FQDN
        s = socket.socket()
        print(f'Attempting to connect to {server} on port 443')
        try:
            s.connect((server, 443))
            print(f'Connecton successful to {server} on port 443')
            Test = True
        except:
            print(f'Connection to {server} on port 443 failed: {traceback.format_exc()}\n\n')

    # Adding HTTPS to Server for URL
    server = f'https://{server}'

    # Request Username and Password without showing password in clear text
    username = input('Please Enter API Username: ').strip()
    password = define_password()
    # Instantiate API session to CML
    cml = cmlClient(server, username, password, ssl_verify=False)

    print ('''
***********************************************************************************************
*                                                                                             *
* TOOLS AVAILABLE:                                                                            *
*                                                                                             *
*  1. Basic URL GET                                                                           *
*                                                                                             *
*  2. Download Lab Topology and save to file                                                  *
*                                                                                             *
*  3. Upload Lab Topology and Create Lab                                                      *
*                                                                                             *
*  4. Delete Lab                                                                              *
*                                                                                             *
***********************************************************************************************
''')

    #
    #
    #
    # Run script until user cancels
    while True:
        Script = False
        while not Script:
            script = input('Please Select Script: ')
            if script == '1':
                Script = True
                BlankGet(cml)
            elif script == '2':
                Script = True
                TopoDownload(cml)
            #elif script == '3':
            #    Script = True
            #    TopoUpload(cml)
            elif script == '4':
                Script = True
                LabDelete(cml)
            #elif script == '5':
            #    Script = True
            #    GetInventory(server,headers,username,password)
            else:
                print('INVALID ENTRY... ')

        # Ask to end the loop
        print ('''
***********************************************************************************************
*                                                                                             *
* TOOLS AVAILABLE:                                                                            *
*                                                                                             *
*  1. Basic URL GET                                                                           *
*                                                                                             *
*  2. Download Topology and save to file                                                      *
*                                                                                             *
***********************************************************************************************
''')
        Loop = input('*\n*\nWould You Like To use another tool? [y/N]').lower()
        if Loop not in (['yes','ye','y']):
            break


