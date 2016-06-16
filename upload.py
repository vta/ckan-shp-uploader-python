#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# import urllib2
# import urllib
# import json
# import pprint
# 
# # Put the details of the dataset we're going to create into a dict.
# dataset_dict = {
#     'name': 'flattened-crash-data-2010-2015',
#     'notes': 'Flattened Crash Data 2010-2015',
# }
# 
# # Use the json module to dump the dictionary to a string for posting.
# data_string = urllib.quote(json.dumps(dataset_dict))
# 
# # We'll use the package_create function to create a new dataset.
# request = urllib2.Request(
#     'http://www.my_ckan_site.com/api/action/package_create')
# 
# # Creating a dataset requires an authorization header.
# # Replace *** with your API key, from your user account on the CKAN site
# # that you're creating the dataset on.
# request.add_header('Authorization', 'a059851e-dea1-4638-aeb4-1c4a7d789fa5')
# 
# # Make the HTTP request.
# response = urllib2.urlopen(request, data_string)
# assert response.code == 200
# 
# # Use the json module to load CKAN's response into a dictionary.
# response_dict = json.loads(response.read())
# assert response_dict['success'] is True
# 
# # package_create returns the created package as its result.
# created_package = response_dict['result']
# pprint.pprint(created_package)

import argparse
import requests
import os.path
import urllib2
import re
import sys
import time

from cli_utils import url_exists, prompt




class Ckan_Util:

    def __init__(self, ckan_server, api_key):
        self.server = ckan_server
        self.api_key = api_key

    def fileUpload(self, dataset_name, filepath):
        print('fileUpload --> '+dataset_name+' :: '+filepath)
        
        r = requests.post(self.server + '/api/action/resource_create',
                  data={"package_id":dataset_name},
                  headers={"X-CKAN-API-Key": self.api_key},
                  files=[('upload', file(filepath))])
        if r.status_code == requests.codes.ok:
            print "success!"
            print r.text
        else:
            print(str(r.status_code)+' '+r.text)



class Uploader:
    def __init__(self):
        self.server_url = None
        self.api_key = None
        self.dataset_name = None
        self.filename = None

    def prompt_args(self):
        
        self.server_url = prompt(
            message = "Enter the URL of the CKAN server", 
            errormessage= "The URL you provides is not valid (it must be the full URL)",
            isvalid = lambda v : url_exists(v))

        self.api_key = prompt(
            message = "Enter the API key to use for uploading", 
            errormessage= "A valid API key must be provided. This key can be found in your user profile in CKAN",
            isvalid = lambda v : re.search(r"(([^-])+-){4}[^-]+", v))

        self.filename = prompt(
            message = "Enter the path of the file to upload", 
            errormessage= "The file path you provided does not exist",
            isvalid = lambda v : os.path.isfile(v))

        self.dataset_name = prompt(
            message = "Enter the name of the dataset you want to create", 
            errormessage= "The dataset must be named",
            isvalid = lambda v : len(v) > 0)




    def upload(self):
        ckan = Ckan_Util(self.server_url, self.api_key)
        ckan.fileUpload(self.dataset_name, self.filename)

    def to_string(self):
        return self.server_url +' '+ self.api_key +' '+ self.dataset_name +' '+ self.filename


def url_exists(url):
    parsed_url = urlparse(url)
    if not bool(parsed_url.scheme):
        argparse.ArgumentTypeError("{0} is not a valid URL".format(url))
    try:
        urllib2.urlopen(url)
        return url         # URL Exist
    except ValueError, ex:
        # URL not well formatted
        argparse.ArgumentTypeError("{0}  is not a valid URL".format(url))
    except urllib2.URLError, ex:
        # URL don't seem to be alive
        argparse.ArgumentTypeError("could not connect to the server at {0}".format(url))

def valid_api_key(arg):
    if re.search(r"(([^-])+-){4}[^-]+", arg):
        return arg
    raise argparse.ArgumentTypeError("{0} is not a valid API key".format(arg))

if __name__ == '__main__':
    u = Uploader()

    # http://stackoverflow.com/a/7856172/940217
    parser = argparse.ArgumentParser(description='Upload files to CKAN')
    subparsers = parser.add_subparsers(description='available subcommands')

    parser_main = subparsers.add_parser('direct', help='provide input as positional arguments')
    parser_main.add_argument('url', metavar='url', type=str, help='the full URL of the CKAN server')
    parser_main.add_argument('key', metavar='key', type=valid_api_key, help='the API key to use for interacting with the API (this key can be found in your user profile in CKAN)')
    parser_main.add_argument('name', metavar='name', type=str, help='the name of the dataset you want to create')
    parser_main.add_argument('filename', metavar='filename', type=argparse.FileType('r'), help='the path of the file to upload')
    
    parser_interactive = subparsers.add_parser('interactive', help='enter interactive mode to be prompted for input')
    
    args = parser.parse_args()

    
    print type(args)
    print dir(args)

    print (args.url)
    print (args.key)
    print (args.name)
    print (args.filename)


    # u = Uploader()
    # u.prompt_args()
    # print u.to_string()
    # u.upload()



