import pytest
import upload
import os.path
import argparse
import tempfile

def test_valid_api_key():
    good_api_key = '11111111-1111-1111-1111-111111111111'
    assert upload.valid_api_key(arg=good_api_key) == good_api_key

    with pytest.raises(argparse.ArgumentTypeError):
        upload.valid_api_key(arg='thisshouldbeugly')


def test_check_preview_file():

    with tempfile.TemporaryDirectory() as temp_dir:
        filename = os.path.join(temp_dir, 'test.txt')
        with pytest.raises(argparse.ArgumentTypeError):
            upload.check_preview_file(filename=filename)
        with open(filename, 'w') as f:
            f.write('1\n')
            f.write('2\n')
            f.write('3\n')

        upload.check_preview_file(filename=filename)
