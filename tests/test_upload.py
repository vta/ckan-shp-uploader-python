import pytest
import upload
import argparse
import tempfile

def test_valid_api_key():
    good_api_key = '11111111-1111-1111-1111-111111111111'
    assert upload.valid_api_key(arg=good_api_key) == good_api_key

    with pytest.raises(argparse.ArgumentTypeError):
        upload.valid_api_key(arg='thisshouldbeugly')
