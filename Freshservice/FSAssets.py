# Python script to intergreate Freshservice APIs using
# REST operations and receiving responses as plain JSON
# Freshservice API documentation can be found at 
# https://api.freshservice.com/
# 2023-06-07    created by nestor.sanchez@hts.com


import requests
import json

path = 'C:/Users/nestor.sanchez/Downloads/'
option = 0
actions = {
    1: 'asset_types', 2: 'vendors', 3: 'locations', 
    4: 'products', 5: 'assets', 6: 'requesters'
    }
auth = ('[redacted]', 'hts')
ver = 0.1
debug = 1


if not debug:
    userOpt = input('\n\n\nThe use of this script is purely for testing and experimental purposes \n' \
        'You should not be using this script if you are not willing to accept liability \n' \
        'of any unintended results. Always have someone with agent access to Freshstatus to verify \n'
        'any actions completed with this script.\n\n\n' \
        'Confirm and continue with [Y] (case-sensitive)\t>')
    #if userOpt != "Y": endMe()


def build_data(sel=''):

    import uuid
    from datetime import datetime

    page=0
    count = 100
    getResponse = dict([])
    
    while count == 100:

        page += 1;     
        headers = {'Content-Type': 'application/json'}
        url = 'https://hts.freshservice.com/api/v2/' + sel + '?per_page=100&page=' + str(page)
        rawResponse = requests.get(url, headers=headers, auth=auth)
        rawResponse = json.loads(rawResponse.content.decode("utf-8")) if type(rawResponse.content) is bytes else rawResponse.content
        if rawResponse.get("errors"): print( 'Something went wrong! /n' + rawResp['errors']); exit()

        count = len( rawResponse[sel] )

        if getResponse: getResponse[sel] = getResponse[sel] + rawResponse[sel] 
        else: getResponse = rawResponse

        if count == 100: print('Over 100 results for \"' +sel+ '\", admending list...'); continue
        else: break

    print( 'Total ' + sel + ' type found: ' + str(len(getResponse[sel])) + '\n' )
    return getResponse 


def main():
    
    from datetime import datetime

    payload = {}
    
    if not option:        
        for i in actions.keys(): payload.update(build_data(actions[i]))    
    else: payload.update(build_data(actions[option]))
    
    t = datetime.now().strftime("-%Y%m%d%H%M")
    f = open( fname := (path + 'Exported_FS_Data' +t + '.json'), 'w',  encoding="utf-8")
    f.write(str(json.dumps(payload, indent = 4)))
    f.close()

    print( fname +' file generated. \n' )
    
main()

print( 'Script end.' )