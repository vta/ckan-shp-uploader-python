#!/usr/local/bin/python
# -*- coding: utf-8 -*-


# # We'll use the package_create function to create a new dataset.
# request = urllib2.Request(
#     'http://www.my_ckan_site.com/api/action/package_create')
# 
# # Creating a dataset requires an authorization header.
# # Replace *** with your API key, from your user account on the CKAN site
# # that you're creating the dataset on.
# request.add_header('Authorization', 'a059851e-dea1-4638-aeb4-1c4a7d789fa5')
# 


import argparse
import requests
import os.path
import urllib2
import re
import sys
import time

from urlparse import urlparse
from cli_utils import url_exists, prompt

import ckanapi


class Ckan_Util:

    def __init__(self, ckan_server, api_key):
        self.server = ckan_server
        self.api_key = api_key

    def fileUpload(self, dataset_name, filepath):
        print('fileUpload --> '+dataset_name+' :: '+filepath)

        mysite = ckanapi.RemoteCKAN(self.server,
            apikey=self.api_key,
            user_agent='CKAN SHP Uploader')
        try:
            pkg = mysite.action.package_create(
                name=dataset_name,
                title='not going to work',
                owner_org='vta')
        except ckanapi.NotAuthorized:
            print 'access denied. Is your API key valid?'
            return

        mysite.action.resource_create(
            package_id=dataset_name,
            upload=open(filepath, 'rb'),
            url='',
            format='csv')




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

def valid_file(fname):
    if os.path.isfile(fname):
        return fname
    raise argparse.ArgumentTypeError("{0} is not a valid filepath".format(arg))

if __name__ == '__main__':
    u = Uploader()

    # http://stackoverflow.com/a/7856172/940217
    parser = argparse.ArgumentParser(description='Upload files to CKAN')
    subparsers = parser.add_subparsers(description='available subcommands')

    parser_main = subparsers.add_parser('direct', help='provide input as positional arguments')
    parser_main.add_argument('url', metavar='url', type=url_exists, help='the full URL of the CKAN server')
    parser_main.add_argument('key', metavar='key', type=valid_api_key, help='the API key to use for interacting with the API (this key can be found in your user profile in CKAN)')
    parser_main.add_argument('name', metavar='name', type=str, help='the name of the dataset you want to create')
    parser_main.add_argument('filename', metavar='filename', type=valid_file, help='the path of the file to upload')
    
    parser_interactive = subparsers.add_parser('interactive', help='enter interactive mode to be prompted for input')
    
    args = parser.parse_args()

    print (args.url)
    print (args.key)
    print (args.name)
    print (args.filename)

    ckan = Ckan_Util(args.url, args.key)
    ckan.fileUpload(args.name, args.filename)

    # u = Uploader()
    # u.prompt_args()
    # print u.to_string()
    # u.upload()



