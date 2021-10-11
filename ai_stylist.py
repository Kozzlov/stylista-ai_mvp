from google.cloud import vision
import google.cloud.storage as gcs
from google.cloud import storage
from google.cloud.storage import client


from google.protobuf import field_mask_pb2 as field_mask

import os
project_id = 'stylista-ai'
# creds_file = 'C:/Users/danii/Desktop/stylista-ai-b42e3e125a0e.json'
# creds_file = 'stylista-ai-b42e3e125a0e.json'
creds_file = 'stylista-ai-b42e3e125a0e.json'
bucket_name = 'ai-stylist-bucket'
location = 'us-west1'
product_set_id = 'ai-stylist-test-product-set_id'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_file

# ai_stylist_bucket = 'gs://ai-stylist-bucket/my_closet/accessories/black_leather_belt/photo1626950491.jpeg'


oauth_client_id = '786187877615-mvk68u76vdgnctmthimq325vg0uv6gnp.apps.googleusercontent.com'
oauth_client_secret = 'n0i0MBDmlEZw9IzNnKP4Y7lv'

# pip install --upgrade google-cloud-storage
# vision_credentials = Credentials.from_service_account_info(info)
# client = vision.ImageAnnotatorClient(credentials=vision_credentials)

from google.cloud import storage

#create prodcut set
def create_product_set(project_id, location, product_set_id, product_set_display_name):
    """Create a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_set_display_name: Display name of the product set.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product set with the product set specification in the region.
    product_set = vision.ProductSet(
            display_name=product_set_display_name)

    # The response is the product set with `name` populated.
    response = client.create_product_set(
        parent=location_path,
        product_set=product_set,
        product_set_id=product_set_id)

    # Display the product set information.
    print('Product set name: {}'.format(response.name))

#create product
def create_product(project_id, location, product_id, product_display_name, product_category):
    """Create one product.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        product_display_name: Display name of the product.
        product_category: Category of the product.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product with the product specification in the region.
    # Set product display name and product category.
    product = vision.Product(
        display_name=product_display_name,
        product_category=product_category)

    # The response is the product with the `name` field populated.
    response = client.create_product(
        parent=location_path,
        product=product,
        product_id=product_id)

    # Display the product information.
    print('Product name: {}'.format(response.name))

#link image to existing product
def create_reference_image(
        project_id, location, product_id, reference_image_id, gcs_uri):
    """Create a reference image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        reference_image_id: Id of the reference image.
        gcs_uri: Google Cloud Storage path of the input image.
    """

    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Create a reference image.
    reference_image = vision.ReferenceImage(uri=gcs_uri)

    # The response is the reference image with `name` populated.
    image = client.create_reference_image(
        parent=product_path,
        reference_image=reference_image,
        reference_image_id=reference_image_id)

    # Display the reference image information.
    print('Reference image name: {}'.format(image.name))
    print('Reference image uri: {}'.format(image.uri))

#add product to product set
def add_product_to_product_set(
        project_id, location, product_id, product_set_id):
    """Add a product to a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Add the product to the product set.
    client.add_product_to_product_set(
        name=product_set_path, product=product_path)
    print('Product added to product set.')

#add multiple lables to product (in paticulat, product category and public url of reference image)
def update_product_multiple_labels(project_id, location, product_id, labels_dict):
    """Update the product labels.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        key: The key of the label.
        value: The value of the label.
    """
    client = vision.ProductSearchClient()

    # Get the name of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Set product name, product label and product display name.
    # Multiple labels are also supported.
    labels = []
    for key, value in labels_dict.items():
        key_value = vision.Product.KeyValue(key=key, value=value)
        # keys = vision.Product.product_labels()
        labels.append(key_value)
    product = vision.Product(
        name=product_path,
        product_labels=labels)

        # Updating only the product_labels field here.
    update_mask = field_mask.FieldMask(paths=['product_labels'])

    # This overwrites the product_labels.
    updated_product = client.update_product(
        product=product, update_mask=update_mask)

    # Display the updated product information.
    print('Product name: {}'.format(updated_product.name))
    print('Updated product labels: {}'.format(product.product_labels))

def can_add_item(existing_items, new_type):
    if new_type in existing_items:
        return False
    if new_type == 'bottom' and 'dress' in existing_items:
        return True
    if new_type == 'top' and 'dress' in existing_items:
        return True
    if new_type == 'bottom' and 'overalls' in existing_items:
        return True
    if new_type == 'top' and 'overalls' in existing_items:
        return True
    return True

def fulfill_deep_fashion_product_set(project_id, location, product_set_id, product_id, product_display_name, reference_image_id, gcs_uri, labels_dict, bucket_name):
    create_product(project_id=project_id,
                   location=location,
                   product_id=product_id,
                   product_display_name=product_display_name,
                   product_category='apparel-v2')
    add_product_to_product_set(project_id=project_id,
                               location=location,
                               product_id=product_id,
                               product_set_id=product_set_id)
    create_reference_image(project_id=project_id,
                           location=location,
                           product_id=product_id,
                           reference_image_id=reference_image_id,
                           gcs_uri=gcs_uri)
    update_product_multiple_labels(project_id=project_id,
                                   location=location,
                                   product_id=product_id,
                                   labels_dict=labels_dict)

##create empty product set for DeepFashion dataset
# create_product_set(project_id=project_id,
#                    location=location,
#                    product_set_id='deep_fashion_test_product_set_id',
#                    product_set_display_name='deep_fashion_test_product_set')

def create_deep_fashion_product_set(blobs_all):
    for blob in blobs_all:
        labels_dict = dict.fromkeys(['product_category','product_public_url'])
        product_id = blob.id.replace('/', '')
        product_display_name = blob.name.replace('/', '')
        reference_image_id = 'reference_image_id_' + product_display_name
        gcs_uri = 'gs://' + bucket_name + '/' + blob.name
        product_category = blob.name.split('/')[0]
        product_category = product_category.split('_')[-1]
        labels_dict['product_category'] = product_category
        product_public_url = blob.public_url
        labels_dict['product_public_url'] = product_public_url
        fulfill_deep_fashion_product_set(project_id=project_id,
                                         location=location,
                                         product_set_id='deep_fashion_test_product_set_id',
                                         product_id=product_id,
                                         product_display_name=product_display_name,
                                         reference_image_id=reference_image_id,
                                         gcs_uri=gcs_uri,
                                         labels_dict=labels_dict,
                                         bucket_name=bucket_name)

#getting access to gcp bucket to access all image files to create product set
storage_client = storage.Client()
bucket_name = 'deep_fashion_test_bucket'
bucket = storage_client.get_bucket(bucket_name)

#Get blobs in bucket (including all subdirectories)
blobs_all = list(bucket.list_blobs())

#create product set with previously accessed DeepFashion dataset in deep_fashion_test_bucket bucket 
# create_deep_fashion_product_set(blobs_all=blobs_all[0: len(blobs_all)-1])

#in case any issue have appeared during product set creation, the following function will purge all products from product set
# purge_products_in_product_set(project_id=project_id,location=location,product_set_id='deep_fashion_test_product_set_id',force=True)

categories_top = ('Tee', 'Tank' ,'Blouse',
                        'Hoodie', 'Sweater', 'Top',
                        'Poncho', 'Cardigan', 'Blazer',
                        'Jacket', 'Jersey', 'Coat',
                        'Flannel', 'Henley', 'Button-Down',
                        'Turtleneck', 'Parka', 'Peacoat',
                        'Anorak', 'Robe', 'Bomber', 'Coverup')
categories_bottom = ('Shorts', 'Skirt', 'Leggings',
                        'Culottes', 'Joggers', 'Sweatpants',
                        'Jeans', 'Cutoffs', 'Sweatshorts',
                        'Jeggings', 'Chinos', 'Trunks',
                        'Capris', 'Gauchos', 'Jodhpurs',
                        'Sarong')
categories_overalls = ('Kaftan', 'Halter', 'Onesie',
                       'Caftan', 'Kimono', 'Jumpsuit',
                       'Dress', 'Romper')

three_types_of_categories = []
three_types_of_categories.append(categories_top)
three_types_of_categories.append(categories_bottom)
three_types_of_categories.append(categories_overalls)

def get_similar_products_url(
    project_id, location, product_set_id, product_category,
    image_uri, filter):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        image_uri: Cloud Storage location of image to be searched.
        filter: Condition to be applied on the labels.
        Example for filter: (color = red OR color = blue) AND style = kids
        It will search on all products with the following labels:
        color:red AND style:kids
        color:blue AND style:kids
    """
    existing_items = []
    matches = {}

    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Create annotate image request along with product search feature.
    image_source = vision.ImageSource(image_uri=image_uri)
    image = vision.Image(source=image_source)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter)
    image_context = vision.ImageContext(
        product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search( # pylint: disable=no-member
        image, image_context=image_context)

    # index_time = response.product_search_results.index_time
    # print('Product set index time: ')
    # print(index_time)

    results = response.product_search_results.results

    # print('Search results:')
    for result in results:
        product = result.product
        if (product.product_labels not in existing_items) or (product.product_labels in existing_items and existing_items.count(product.product_labels) < 2):
            existing_items.append(product.product_labels)
            can_add_item(existing_items=existing_items, new_type=product.product_labels)
            matches[product.product_labels[-1].value] = product.product_labels[-2].value
            # matches.append(product.product_labels[-1].value)
        # if any(product.name in category for category in categories_top) and top_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     top_matches += 1
        #     links.append(product.product_labels[-1].value)
        # if any(product in category for category in categories_bottom) and bottom_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     bottom_matches += 1
        #     links.append(product.product_labels[-1].value)
        # if any(product in category for category in categories_overalls) and overall_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     overall_matches += 1
        #     links.append(product.product_labels[-1].value)
            # list_reference_images(project_id=project_id, location=location, product_id=product.name.split('/')[-1])
            # print('Score(Confidence): {}'.format(result.score))
            # print('Image name: {}'.format(result.image))
            # print('Product name: {}'.format(product.name))
            # print('Product display name: {}'.format(product.display_name))
            # print('Product description: {}\n'.format(product.description))
            # print('Product description: {}\n'.format(product.product_labels))
    return matches

def get_similar_products_file(
        project_id, location, product_set_id, product_category,
        file_path, filter):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        file_path: Local file path of the image to be searched.
        filter: Condition to be applied on the labels.
        Example for filter: (color = red OR color = blue) AND style = kids
        It will search on all products with the following labels:
        color:red AND style:kids
        color:blue AND style:kids
    """
    existing_items = []
    matches = {}

    # product_search_client is needed only for its helper methods.
    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Read the image as a stream of bytes.
    with open(file_path, 'rb') as image_file:
        content = image_file.read()

    # Create annotate image request along with product search feature.
    image = vision.Image(content=content)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter)
    image_context = vision.ImageContext(
        product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search( # pylint: disable=no-member
        image, image_context=image_context)

    index_time = response.product_search_results.index_time
    print('Product set index time: ')
    print(index_time)

    results = response.product_search_results.results

    for result in results:
        product = result.product
        if (product.product_labels not in existing_items) or (product.product_labels in existing_items and existing_items.count(product.product_labels) < 2):
            existing_items.append(product.product_labels)
            can_add_item(existing_items=existing_items, new_type=product.product_labels)
            matches[product.product_labels[-1].value] = product.product_labels[-2].value
            # matches.append(product.product_labels[-1].value)
        # if any(product.name in category for category in categories_top) and top_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     top_matches += 1
        #     links.append(product.product_labels[-1].value)
        # if any(product in category for category in categories_bottom) and bottom_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     bottom_matches += 1
        #     links.append(product.product_labels[-1].value)
        # if any(product in category for category in categories_overalls) and overall_matches < 3:
        #     print('Product description: {}\n'.format(product.product_labels))
        #     overall_matches += 1
        #     links.append(product.product_labels[-1].value)
            # list_reference_images(project_id=project_id, location=location, product_id=product.name.split('/')[-1])
            # print('Score(Confidence): {}'.format(result.score))
            # print('Image name: {}'.format(result.image))
            # print('Product name: {}'.format(product.name))
            # print('Product display name: {}'.format(product.display_name))
            # print('Product description: {}\n'.format(product.description))
            # print('Product description: {}\n'.format(product.product_labels))
    return matches

def find_deep_fashion_clothing_set_for_url_references(references):
    recommendations = []
    for reference_link in references:
        result = [reference_link]
        print('THE ITEM %s - ' %reference_link + ' HAS THE FOLLOWING MATCHES:')
        matches = get_similar_products_url(project_id=project_id,
                                           location=location,
                                           product_set_id='deep_fashion_test_product_set_id',
                                           product_category='apparel-v2',
                                           image_uri=reference_link,
                                           filter='')
        matches_divided_into_three_categories = {'tops': [], 'bottoms': [], 'overalls': []}
        for key, value in matches.items():
            if value in three_types_of_categories[0] and len(matches_divided_into_three_categories['tops']) <= 2:
                matches_divided_into_three_categories['tops'].append(key)
            if value in three_types_of_categories[1] and len(matches_divided_into_three_categories['bottoms']) <= 2:
                matches_divided_into_three_categories['bottoms'].append(key)
            if value in three_types_of_categories[2] and len(matches_divided_into_three_categories['overalls']) <= 2:
                matches_divided_into_three_categories['overalls'].append(key)
        result.append(matches_divided_into_three_categories)
        recommendations.append(result)
    # print(recommendations)
    return recommendations

def find_deep_fashion_clothing_set_for_path_references(paths):
    recommendations = []
    for reference_path in paths:
        result = [reference_path]
        print('THE ITEM %s - ' %reference_path + ' HAS THE FOLLOWING MATCHES:')
        matches = get_similar_products_file(project_id=project_id,
                                           location=location,
                                           product_set_id='deep_fashion_test_product_set_id',
                                           product_category='apparel-v2',
                                           file_path=reference_path,
                                           filter='')
        matches_divided_into_three_categories = {'tops': [], 'bottoms': [], 'overalls': []}
        for key, value in matches.items():
            if value in three_types_of_categories[0] and len(matches_divided_into_three_categories['tops']) <= 2:
                matches_divided_into_three_categories['tops'].append(key)
            if value in three_types_of_categories[1] and len(matches_divided_into_three_categories['bottoms']) <= 2:
                matches_divided_into_three_categories['bottoms'].append(key)
            if value in three_types_of_categories[2] and len(matches_divided_into_three_categories['overalls']) <= 2:
                matches_divided_into_three_categories['overalls'].append(key)
        result.append(matches_divided_into_three_categories)
        recommendations.append(result)
    # print(recommendations)
    return recommendations
