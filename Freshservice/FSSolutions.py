# Python script to intergreate Freshstatus APIs using
# REST operations and receiving responses as plain JSON
# Freshservice API documentation can be found at 
# https://api.freshservice.com/
# 2023-06-08    created by nestor.sanchez@hts.com

# fpath value: Change the values of the destgination 
# folder where you want to create the directories
# fcat value: this is in teh URL of the desired solutions catalog.
# i.e. https://hts.freshservice.com/a/solutions/categories/4000040529

import requests
import json
import datetime
from tabulate import tabulate
from colorama import Fore, Style

ver = 0.1
debug = 1

# Specific to "TRAX Knowledge Base" category

if not debug:
    userOpt = input('\n\n\nThe use of this script is purely for testing and experimental purposes \n' \
        'You should not be using this script if you are not willing to accept liability \n' \
        'of any unintended results. Always have someone with agent access to Freshstatus to verify \n'
        'any actions completed with this script.\n\n\n' \
        'Confirm and continue with [Y] (case-sensitive)\t>')
    #if userOpt != "Y": endMe()

auth = ('[redacted]', 'hts')


fpath = 'C:/Users/nestor.sanchez/Downloads/'
fcat = '4000040529' #TRAX Knowledge Base

def ArticlesFunc(fAbsPath='', rawResp={}):

    # make JSON file
    f = open( fAbsPath + '.json', 'w',  encoding="utf-8")
    f.write(str(json.dumps(rawResp, indent = 4)))
    f.close()


    # make HTML file
    f = open( fAbsPath + '.html', 'w',  encoding="utf-8")
    
    ftitle = str(rawResp['title'])
    fbody = rawResp['description']
    ftemplate = """<html>
    <head>
    <title>%s</title>
    </head>
    <body>
    %s
    </body>
    </html>
    """

    f.write(ftemplate % (ftitle, fbody))
    f.close()

import os.path

# get folders list and create directories if not found
url = 'https://hts.freshservice.com/api/v2/solutions/folders?category_id=' + fcat
headers = {'Content-Type': 'application/json'}
getResponse = requests.get(url, headers=headers, auth=auth)
rawResp = getResponse.content

if type(getResponse.content) is bytes: rawResp = json.loads(rawResp.decode("utf-8"))
foldList = []

for i in range(len(rawResp['folders'])):
    
    fname = (str(rawResp['folders'][i]['position']) + '. ' + rawResp['folders'][i]['name']).replace( '/', '-').strip()
    foldList.append([fname, rawResp['folders'][i]['id']])

    if not os.path.exists(fpath + fname): os.mkdir(fpath + fname); print(fname)
    else: print('Directory ' + fname + ' exists, skipping.')

for i in range(len(foldList)):
    url = 'https://hts.freshservice.com/api/v2/solutions/articles?folder_id=' + str(foldList[i][1])
    headers = {'Content-Type': 'application/json'}
    getResponse = requests.get(url, headers=headers, auth=auth)
    rawResp = getResponse.content
    fname = foldList[i][0] + '/'

    if type(getResponse.content) is bytes: rawResp = json.loads(rawResp.decode("utf-8"))

    for i in range(len(rawResp['articles'])):

        if not os.path.exists(fpath + fname + (ftitle := (rawResp['articles'][i]['title'].replace( '/', '-').strip()))):
            print('Generating files for article ' + fname + ftitle + '.')
            ArticlesFunc(fpath + fname + ftitle, rawResp['articles'][i])
        else: print('Article ' + fname + ftitle + ' exists, skipping.')
            

print('end')