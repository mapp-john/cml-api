# Import Required Modules
import os,\
        re,\
        sys,\
        csv,\
        yaml,\
        json,\
        socket,\
        random,\
        netaddr,\
        traceback
from virl2_client \
        import ClientLibrary \
        as cmlClient
# Import custom modules from file
from cml_api_modules import \
        define_password,\
        GetAllLabDetails,\
        DeleteLab


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
    return


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
        #url = f'{cml.url}/api/v0/labs/{d["id"]}/topology'
        ID = d['id']
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
        print(f'Downloading topology for lab: {d[I]["lab_title"]}')
        #url = f'{cml.url}/api/v0/labs/{d[I]["id"]}/topology'
        ID = d[I]['id']

    #TODO: YAML or JSON format, with/without configurations
    # Perform API GET call
    try:
        # REST call with SSL verification turned off
        lab = cml.join_existing_lab(ID)
        resp = yaml.safe_load(lab.download())
        print('GET successful...')
        # Ask if output should be saved to File
        save = input('Would You Like To Save The Output To File? [y/N]: ').lower()
        if save in (['yes','ye','y']):
            # Random Generated YAML Output File
            if not os.path.exists('topologies'):
                os.mkdir('topologies')
            filename = f'topologies/{resp["lab"]["title"]}_v{resp["lab"]["version"]}.yml'
            with open(filename, 'w') as OutFile:
                OutFile.write(yaml.safe_dump(resp))
            print(f'*\n*\nTopology File Created... {filename}\n')
        elif save in (['no','n','']):
            print(yaml.safe_dump(resp))
    except:
        print(f'Error in connection --> {traceback.format_exc()}')
    # End
    finally:
        try:
            if r: r.close()
        except:
            None
    return


#
#
#
# Define Import Topology Function
def TopoImport(cml):
    print ('''
***********************************************************************************************
*                                Import Lab Topology File                                     *
*_____________________________________________________________________________________________*
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. Select YAML Topology File to Import (Must be YAML format)                               *
*                                                                                             *
***********************************************************************************************
''')
    # Request Topology File
    Test = False
    while not Test:
        # Request Input File
        topo_file = input('Please Enter Input File /full/file/path.yml: ')
        title = input('Please enter Lab title: ')
        if os.path.isfile(topo_file):
            #TODO: Validate YAML vs JSON
            Test = True
        else:
            print('MUST PROVIDE INPUT FILE...')
            Test = False
    # Import Lab file and start Lab
    try:
        print(f'Importing Lab {title}, and starting Lab...\n')
        lab = cml.import_lab_from_path(topo_file, title)
        lab.start()
        print(f'Lab {title} started...\n')
    except:
        print(f'\nError Occurred --> {traceback.format_exc()}\n')

    return



#
#
#
# Define Delete Lab Function
def LabDelete(cml):
    print ('''
***********************************************************************************************
*                                        Delete Labs                                          *
*_____________________________________________________________________________________________*
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. Select which lab to delete                                                              *
*                                                                                             *
***********************************************************************************************
''')
    # Get Lab details and request user to select lab if multiple
    labs = cml.get_lab_list()
    if len(labs) == 0:
        print('\nNo labs found...\n\n')
        return
    else:
        d = GetAllLabDetails(cml)
        print('''
***********************************************************************************************
*                             Please select lab to delete                                  *
***********************************************************************************************
''')
        for k,v in d.items():
            print(f'{k}. Title: {v["lab_title"]}, Description: {v["lab_description"]}\n')
        print(f'{len(d)+1}. DELETE ALL LABS\n')

        I = ''
        while I not in d:
            I = input('Selection: ')
            if (I in d) or (I == str(len(d)+1)):
                C = input(f'Confirm Selection: ')
                if C != I:
                    I = ''
            if (not I in d) and (not I == str(len(d)+1)):
                print('Invalid Selection...\n')
            elif I == str(len(d)+1):
                print('Deleting All Labs')
                I = 'ALL'
                break

    # Delete labs
    try:
        if I == 'ALL':
            for k,v in d.items():
                Del = DeleteLab(cml,k['id'])
                if Del:
                    print(f'\nDeleted Lab "{v["lab_title"]}" Successfully\n')
                else:
                    print(f'\nError Occurred when attempting to Delete Lab "{v["lab_title"]}"....\n')
        else:
            Del = DeleteLab(cml,d[I]['id'])
            if Del:
                print(f'\nDeleted Lab "{d[I]["lab_title"]}" Successfully\n')
            else:
                print(f'\nError Occurred when attempting to Delete Lab "{d[I]["lab_title"]}"....\n')
    except:
        print(f'\nError Occurred --> {traceback.format_exc()}\n')

    return




#
#
#
# Define FTD Image Upload Function
def FTDUpload(cml):
    print ('''
***********************************************************************************************
*                           Upload FTD Image to CML Server                                    *
*_____________________________________________________________________________________________*
*                                                                                             *
* USER INPUT NEEDED:                                                                          *
*                                                                                             *
*  1. Path to FTD Image                                                                       *
*                                                                                             *
***********************************************************************************************
''')
    # Request FTD File Path
    Test = False
    while not Test:
        # Request Input File
        image_file = input('Please Enter Input File /full/file/path.qcow2: ')
        if os.path.isfile(image_file):
            #TODO: Validate YAML vs JSON
            Test = True
        else:
            print('MUST PROVIDE INPUT FILE...')
            Test = False
    # Validate if image is already on server
    I = cml.definitions.image_definitions()
    url = f'{cml.url}/api/v0/list_image_definition_drop_folder'
    S = cml.session
    r = S.get(url)
    images = r.json()
    images += [i['disk_image'] for i in I]
    # If Image already exists on CML server
    if image_file.split('/')[-1] in images:
        print(f'\nImage {image_file.split("/")[-1]} already exists on server\nLooking for Node definition for image...\n')
        nodes = cml.definitions.node_definitions()
        d = False
        for n in nodes:
            D = cml.definitions.image_definitions_for_node_definition(n['id'])
            if (D != []) and (D[0]['disk_image'] == image_file.split("/")[-1]):
                print(f'Node Definition: {D[0]["node_definition_id"]}')
                d = True
                return
            else:
                continue
        # If no definition exists, create them
        if not d:
            print(f'Node Defniition not found for image {image_file.split("/")[-1]}...\nCreating Node Definition....\n')
            try:
                headers = {'Accept': 'application/yaml', 'Content-Type': 'application/yaml'}
                S = cml.session
                # Create Node Definition
                url = f'{cml.url}/api/v0/node_definitions'
                Y = yaml.safe_load(open('ftdv-6.6_node_def.yml','r').read())
                r = S.post(url,headers=headers,data=yaml.safe_dump(Y))
                # Create Image Definition
                url = f'{cml.url}/api/v0/image_definitions'
                Y = yaml.safe_load(open('ftdv-6.6_image_def.yml','r').read())
                Y['disk_image'] = image_file.split('/')[-1]
                r = S.post(url,headers=headers,data=yaml.safe_dump(Y))
                print(f'Node Definition "ftdv" created successfully')
                return
            except:
                print(f'\nError Occurred --> {traceback.format_exc()}\n')

    # If Image does not exist on CML server
    else:
        try:
            print(f'Uploading Image {image_file.split("/")[-1]} to CML server and Creating Node/Image Definitions...\n')
            r = cml.definitions.upload_image_file(image_file)
            headers = {'Accept': 'application/yaml', 'Content-Type': 'application/yaml'}
            S = cml.session
            # Create Node Definition
            url = f'{cml.url}/api/v0/node_definitions'
            Y = yaml.safe_load(open('definitions/ftdv-6.6_node_def.yml','r').read())
            r = S.post(url,headers=headers,data=yaml.safe_dump(Y))
            # Create Image Definition
            url = f'{cml.url}/api/v0/image_definitions'
            Y = yaml.safe_load(open('definitions/ftdv-6.6_image_def.yml','r').read())
            Y['disk_image'] = image_file.split('/')[-1]
            r = S.post(url,headers=headers,data=yaml.safe_dump(Y))
            print(f'Node and Image Definition "ftdv" created successfully')
            return

        except:
            print(f'\nError Occurred --> {traceback.format_exc()}\n')

    return






#TODO: Create BuildLab() Function \
        #1. Choose Lab Title \
        #2. Discover what Node definitions exist \
        #3. Choose node types, and how many \
        #4. Choose nodes to connect together \
        #5. Create new Lab \
        #6. Add Nodes to Lab \
        #7. Connect Nodes \
        #8.
#
#
#
#def BuildLab(cml):






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
        if '//' in server:
            server = server.split('//')[-1]
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
*  5. Upload FTD Image (QCOW2 image)                                                          *
*                                                                                             *
*  6. Create new Lab                                                                          *
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
            elif script == '3':
                Script = True
                TopoImport(cml)
            elif script == '4':
                Script = True
                LabDelete(cml)
            elif script == '5':
                Script = True
                FTDUpload(cml)
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
*  2. Download Lab Topology and save to file                                                  *
*                                                                                             *
*  3. Upload Lab Topology and Create Lab                                                      *
*                                                                                             *
*  4. Delete Lab                                                                              *
*                                                                                             *
*  5. Upload FTD Image (QCOW2 image)                                                          *
*                                                                                             *
*  6. Create new Lab                                                                          *
*                                                                                             *
***********************************************************************************************
''')
        Loop = input('*\n*\nWould You Like To use another tool? [y/N]').lower()
        if Loop not in (['yes','ye','y']):
            break


