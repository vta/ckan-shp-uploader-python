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
import os.path
import urllib.request
import re
import json
import fiona
import sys
import time
import threading

from urllib.parse import urlparse
from urllib.error import URLError
from cli_utils import url_exists, prompt

API_KEY_IS_VALID = re.compile(r"(([^-])+-){4}[^-]+")

import ckanapi


def run_long_process(function_name, *args, **kwargs):
    t1 = threading.Thread(target=function_name, args=args, kwargs=kwargs)
    start_t = time.time()
    t1.start()
    spinner = ['-','\\','|','/','-','\\','|','/']
    spinner_i = 0
    delta_t = 0
    while t1.is_alive():
        delta_t = (time.time() - start_t)
        sys.stdout.write("running... time elapsed: {0:.1f}s  {1}   \r".format(delta_t, spinner[spinner_i]))
        spinner_i = (spinner_i + 1) % len(spinner)
        time.sleep(0.1)
        delta_t = (time.time() - start_t)
        sys.stdout.flush()
        
    print('Done!                           ')
    print('Finished in {0:.2f} seconds'.format(delta_t))


class Uploader:

    def __init__(self):
        self.server_url = None
        self.api_key = None
        self.dataset_name = None
        self.filename = None
        self.ckan_inst = None

    def prompt_args(self):
        
        self.server_url = prompt(
            message = "Enter the URL of the CKAN server", 
            errormessage= "The URL you provides is not valid (it must be the full URL)",
            isvalid = lambda v: url_exists(v))

        self.api_key = prompt(
            message = "Enter the API key to use for uploading", 
            errormessage= "A valid API key must be provided. This key can be found in your user profile in CKAN",
            isvalid = lambda v : API_KEY_IS_VALID.search(v))

        self.filename = prompt(
            message = "Enter the path of the file to upload", 
            errormessage= "The file path you provided does not exist",
            isvalid = lambda v : os.path.isfile(v))

        self.dataset_name = prompt(
            message = "Enter the name of the dataset you want to create", 
            errormessage= "The dataset must be named",
            isvalid = lambda v : len(v) > 0)

    def upload(self):
        self.ckan_inst = ckanapi.RemoteCKAN(
            self.server_url,
            apikey=self.api_key,
            user_agent='CKAN SHP Uploader'
        )
        run_long_process(
            self.ckan_add_resource_to_dataset,
            self.dataset_name,
            self.filename,
            name=os.path.basename(self.filename),
        )

    def ckan_delete_dataset(self, dataset_id):
        """
        Delete a dataset
        """
        try:
            self.ckan_inst.action.package_delete(id=dataset_id)
        except ckanapi.ValidationError as ex:
            print(ex)
        except ckanapi.NotAuthorized as ex:
            print('access denied. Is your API key valid?')
            print(ex)
            raise

    def ckan_purge_dataset(self, dataset_id):
        """
        WARNING: cannot be undone
        This frees up the URL of the resource
        """
        try:
            self.ckan_inst.call_action('dataset_purge', {'id': dataset_id})
        except ckanapi.ValidationError as ex:
            print(ex)
        except ckanapi.NotAuthorized as ex:
            print('access denied. Is your API key valid?')
            print(ex)
            raise

    def ckan_update_resource(
        self, dataset_title, filepath, owner_org='vta',
        name=None, url='dummy-value', data_format='csv'
):
        """
        For this to work, the resource names should be unique (this is not enforced).
        If the names are not unique, only the last one with the same name will be updated.

        http://docs.ckan.org/en/latest/api/index.html#ckan.logic.action.update.resource_update
        """
        # run a SOLR search for the package
        # http://data2.vta.org/api/3/action/package_search?q=&fq=title:ins_sample%20AND%20organization:city-of-san-jose
        solr_query = 'title:{0} AND organization:{1}'.format(dataset_title, owner_org)
        res = self.ckan_inst.action.package_search(q=solr_query)
        if res.get('count') is not 1:
            print('could not find the requested dataset; dataset title and organization not specific enough')
            return

        # would something like this work instead?
        # res = self.ckan_inst.action.package_show(id=dataset_title)

        print('looking for file "{0}" inside the "{1}" dataset'.format(
            name, dataset_title
        ))
        resource_id = None
        for r in res.get('results')[0].get('resources'):
            print (str(r.get('name'))+' : '+str(r.get('id')))
            if str(r.get('name')) == str(name):
                resource_id = r.get('id')

        if resource_id is None:
            print('could not find the requested resource')
            return
        else:
            print('found resource id "{0}"'.format(resource_id))

        print('uploading...')
        try:
            res = self.ckan_inst.action.resource_update(
                id=resource_id,
                name=name,
                upload=open(filepath, 'rb'),
                url=url,
                format=data_format)
            print('done')
            return res
        except ckanapi.ValidationError as ex:
            print(ex)
        except ckanapi.NotAuthorized as ex:
            print('access denied. Is your API key valid?')
            print(ex)
            raise
        print('done')

    def ckan_add_resource_to_dataset(
            self, package_id, filepath, name=None,
            url='dummy-value', data_format='csv'):
        """
        Upload a new resource and associate it with a dataset
        """
        print('adding resource to dataset --> '+package_id+' :: '+filepath)
        name = name or os.path.basename(filepath)
        try:
            print('uploading...')
            res = self.ckan_inst.action.resource_create(
                package_id=package_id,
                name=name,
                upload=open(filepath, 'rb'),
                url=url,
                format=data_format)
            print('done')
            return res
        except ckanapi.ValidationError as ex:
            print(ex)
        except ckanapi.NotAuthorized as ex:
            print('access denied. Is your API key valid?')
            print(ex)
            return
        print('done')

    def ckan_create_dataset(self, dataset_name,
                            dataset_title, owner_org='vta'):
        """
        Create a dataset without an associated resource
        """
        try:
            self.ckan_inst.action.package_create(
                name=dataset_name,
                title=dataset_title,
                owner_org=owner_org
            )
        except ckanapi.ValidationError as ex:
            if ex.error_dict.get('name') ==  ['That URL is already in use.']:
                print('Package already exists')
            else:
                raise
        except ckanapi.NotAuthorized as ex:
            print('access denied. Is your API key valid?')
            print(ex)
            return
        print('done')

    def to_string(self):
        return self.server_url +' '+ self.api_key +' '+ self.dataset_name +' '+ self.filename


def url_exists(url):
    parsed_url = urlparse(url)
    if not bool(parsed_url.scheme):
        argparse.ArgumentTypeError("{0} is not a valid URL".format(url))
    try:
        urllib.request.urlopen(url)
        return url         # URL Exist
    except ValueError:
        # URL not well formatted
        argparse.ArgumentTypeError("{0}  is not a valid URL".format(url))
    except URLError:
        # URL don't seem to be alive
        argparse.ArgumentTypeError("could not connect to the server at {0}".format(url))


def valid_api_key(arg):
    if API_KEY_IS_VALID.search(arg):
        return arg
    raise argparse.ArgumentTypeError("{0} is not a valid API key".format(arg))


def check_preview_file(filename):
    # check that the file exists and
    # preview what we're going to upload
    if os.path.isfile(filename):
        with open(filename) as f:
            head = [next(f) for x in iter(range(5))]
        print(head)
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid filepath".format(fname))

def shapefile_to_geojson(infile, tempdir=None):
    """
    Take an ESRI shapefile as input, and hopefully turn it into a GeoJSON.

    :return:
    """

    with fiona.open(infile, 'r') as shapefile:
        source_crs = shapefile.crs
        source_schema = shapefile.schema

        # Open the writable outfile
        filename = os.path.splitext(os.path.basename(infile))[0]
        outfilepath = os.path.join(tempdir, filename)
        features = [feature for feature in shapefile]
        crs = " ".join("+%s=%s" % (k,v) for k,v in shapefile.crs.items())

        outfile_layer = {
        "type": "FeatureCollection",
        "features": features,
        "crs": {
            "type": "link",
            "properties": {"href": "my_layer.crs", "type": "proj4"} }
        }

        with open("{}.json".format(outfilepath), "w") as f:
            f.write(json.dumps(outfile_layer))
        with open("{}.crs".format(outfilepath), "w") as f:
            f.write(crs)

if __name__ == '__main__':
    # uploader = Uploader()

    # http://stackoverflow.com/a/7856172/940217
    parser = argparse.ArgumentParser(description='Upload files to CKAN')
    subparsers = parser.add_subparsers(description='available subcommands')

    parser_main = subparsers.add_parser('direct', help='provide input as positional arguments')
    parser_main.add_argument('url', metavar='url', type=url_exists, help='the full URL of the CKAN server')
    parser_main.add_argument('key', metavar='key', type=valid_api_key,
                             help=('the API key to use for interacting with the API '
                                   '(this key can be found in your user profile in CKAN)'))
    parser_main.add_argument('name', metavar='name', type=str, help='the name of the dataset you want to create')
    parser_main.add_argument('title', metavar='title', type=str, help='Title to display for the dataset')
    parser_main.add_argument('filename', metavar='filename', type=valid_file, help='the path of the file to upload')
    parser_main.add_argument('--shapefile', action='store_true', default=False,
                             help='Is file a shapefile that needs geoJSON conversion')
    
    parser_interactive = subparsers.add_parser('interactive', help='enter interactive mode to be prompted for input')
    
    args = parser.parse_args()

    ckan_util = CkanUtil(ckan_server=args.url,
                         api_key=args.key)
    ckan_util.fileUpload(dataset_name=args.name,
                         dataset_title=args.title,
                         filepath=args.filename)

    # u = Uploader()
    # u.prompt_args()
    # print u.to_string()
    # u.upload()



