"""
Do the testing for all our geographic information transformation.

"""

import os
import json
import upload
import os.path
import tempfile

HERE = os.path.abspath(os.path.dirname(__file__))


def test_shapefile_to_geojson():
    """
    This does almost everything, taking shapefiles and making geojson files out of them.
    It's what we want, and we have to make sure it's comprehensive.

    :return:
    """

    filepath = os.path.join(HERE, 'fixture', 'WSYSTEMS.shp')
    with tempfile.TemporaryDirectory() as tempdir:
        upload.shapefile_to_geojson(infile=filepath, tempdir=tempdir)
        jsonfile = os.path.join(tempdir, 'WSYSTEMS.json')
        with open(jsonfile, 'r') as json_handle:
            data = json.load(json_handle)
        with open(os.path.join(tempdir, 'WSYSTEMS.crs')) as crs_handle:
            data = json.load(crs_handle)
            print(data)