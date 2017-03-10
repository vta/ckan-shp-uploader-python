import ckanapi
import os.path

def check_preview_file(filename):
    # check that the file exists and
    # preview what we're going to upload

    print("Let's see if this file is readable:")
    if os.path.isfile(filename):
        with open(filename) as f:
            head = [next(f) for x in iter(range(5))]
        print(head)
    else:
        print('file not found')

def create_dataset(dataset_name, dataset_title, owner_org='vta'):
    """
    Create a dataset with an associated resource
    """
    print("Can we create this dataset?")
    try:
        ckan_inst.action.package_create(
                name=dataset_name,
                title=dataset_title,
                owner_org=owner_org)
    except ckanapi.ValidationError as ex:
        print(ex)
    except ckanapi.NotAuthorized as ex:
        print('access denied. Is your API key valid?')
        print(ex)
        return
    print('done')

def add_resource_to_dataset(package_id, filepath, name=None, url='dummy-value', data_format='csv'):
    """
    Upload a new resource and associate it with a dataset
    """
    if name is None:
        name = os.path.basename(filepath)
    try:
        print('uploading...')
        res = ckan_inst.action.resource_create(
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

    
def get_dataset_info(dataset_title):
    ds = ckan_inst.action.package_show(id=dataset_title)
    print(ds)
    return ds
    
if __name__ == '__main__':

	#Edit these variables
	org_name='test'
	API_KEY = '4b8be186-ccadads-asdadr-21412414'
	SERVER = 'http://data2.vta.org'


	# input_file = 'samples/SalesJan2009.csv'
	input_file = 'samples/Sacramentorealestatetransactions_a.csv'
	dataset_name = 'test'
	dataset_title = 'test'
	resource_name = 'test_resource_2'



	USER_AGENT = 'CKAN SHP Uploader'
	ckan_inst = ckanapi.RemoteCKAN(
            SERVER,
            apikey=API_KEY,
            user_agent=USER_AGENT
        )
	check_preview_file(input_file)

	#Pick the functions you want to perform
	create_dataset(dataset_name, dataset_title, owner_org=org_name)
	add_resource_to_dataset(dataset_name, input_file, name=resource_name)
