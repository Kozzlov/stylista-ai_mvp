import pprint

from google.cloud import vision
import google.cloud.storage as gcs
from google.cloud.storage import client

from google.protobuf import field_mask_pb2 as field_mask
from google.oauth2.service_account import Credentials

import PIL
import urllib
import os

project_id = 'stylista-ai'
# creds_file = 'C:/Users/danii/Desktop/stylista-ai-b42e3e125a0e.json'
creds_file = 'stylista-ai-b42e3e125a0e.json'
bucket_name = 'ai-stylist-bucket'
location = 'us-west1'
product_set_id = 'ai-stylist-test-product-set_id'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_file

ai_stylist_bucket = 'gs://ai-stylist-bucket/my_closet/accessories/black_leather_belt/photo1626950491.jpeg'


oauth_client_id = '786187877615-mvk68u76vdgnctmthimq325vg0uv6gnp.apps.googleusercontent.com'
oauth_client_secret = 'n0i0MBDmlEZw9IzNnKP4Y7lv'

# pip install --upgrade google-cloud-storage
# vision_credentials = Credentials.from_service_account_info(info)
# client = vision.ImageAnnotatorClient(credentials=vision_credentials)

from google.cloud import storage

#CREATE PRODUCT SET-----------------------------------------------------------------------------------------------------

# did not work well enough, the library is a little outdated, specifically problem with types library
# from ProductSearch import ProductSearch, ProductCategories
#
# ps = ProductSearch(project_id=project_id,
#                    location='us-west1',
#                    creds_file=creds_file,
#                    bucket_name=bucket_name)
#
# productSet = ps.createProductSet('my_test_set')

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

#my product set
# create_product_set(project_id=project_id,
#                    location=location,
#                    product_set_id='ai-stylist-test-product-set_id',
#                    product_set_display_name='ai-stylist-test-product-set')

# I wanted to extract data from my bucket. but honestly speaking i did not manged to find such option yet

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
#-----------------------------------------------------------------------------------------------------------------------

def update_product_labels(
        project_id, location, product_id, key, value):
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
    key_value = vision.Product.KeyValue(key=key, value=value)
    keys = vision.Product.product_labels()
    product = vision.Product(
        name=product_path,
        product_labels=[key_value])

    # Updating only the product_labels field here.
    update_mask = field_mask.FieldMask(paths=['product_labels'])

    # This overwrites the product_labels.
    updated_product = client.update_product(
        product=product, update_mask=update_mask)

    # Display the updated product information.
    print('Product name: {}'.format(updated_product.name))
    print('Updated product labels: {}'.format(product.product_labels))


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

#-----------------------------------------------------------------------------------------------------------------------

def list_reference_images(
        project_id, location, product_id):
    """List all images in a product.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)
    # List all the reference images available in the product.
    reference_images = client.list_reference_images(parent=product_path)

    # Display the reference image information.
    for image in reference_images:
        print('Reference image uri: {}'.format(image.uri))
        reference_image_uri = client.reference_image_path(project=project_id,
                                                          location=location,
                                                          product=product_id,
                                                          reference_image=image.name)
        print('Reference image full path: {}'.format(reference_image_uri))

def purge_products_in_product_set(
        project_id, location, product_set_id, force):
    """Delete all products in a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        force: Perform the purge only when force is set to True.
    """
    client = vision.ProductSearchClient()

    parent = f"projects/{project_id}/locations/{location}"

    product_set_purge_config = vision.ProductSetPurgeConfig(
        product_set_id=product_set_id)

    # The purge operation is async.
    operation = client.purge_products(request={
        "parent": parent,
        "product_set_purge_config": product_set_purge_config,
        # The operation is irreversible and removes multiple products.
        # The user is required to pass in force=True to actually perform the
        # purge.
        # If force is not set to True, the service raises an exception.
        "force": force})

    operation.result(timeout=500)

    print('Deleted products in product set.')

def fulfill_product_set(project_id, location, product_set_id, product_set_data):
    for key, item in product_set_data.items():
        create_product(project_id=project_id,
                       location=location,
                       product_id=key,
                       product_display_name=item[0],
                       product_category='apparel-v2')
        add_product_to_product_set(project_id=project_id,
                                   location=location,
                                   product_id=key,
                                   product_set_id=product_set_id)
        create_reference_image(project_id=project_id,
                               location=location,
                               product_id=key,
                               reference_image_id=item[1],
                               gcs_uri=item[2])
        update_product_labels(project_id=project_id,
                              location=location,
                              product_id=key,
                              key=item[3],
                              value=item[4])

product_set_data = {'light_brown_suede_jacket_1': ['light_brown_suede_jacket', 'light_brown_suede_jacket_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/light_brown_suede_jacket/photo1626950507-1.jpeg', 'category', 'top'],
                    'black_everyday_bomber_1': ['black_everyday_bomber', 'black_everyday_bomber_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/black_everyday_bomber/photo1626950506-1.jpeg', 'category', 'top'],
                    'black_basic_t-shirt_1': ['black_basic_t-shirt', 'black_basic_t-shirt_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/black_basic_t-shirt/photo1626950498-1.jpeg', 'category', 'top'],
                    'black_formal_shirt_1': ['black_formal_shirt', 'black_formal_shirt_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/black_formal_shirt/photo1626950507-4.jpeg', 'category', 'top'],
                    'black_print_t-shirt_1': ['black_print_t-shirt', 'black_print_t-shirt_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/black_print_t-shirt/photo1626950498.jpeg', 'category', 'top'],
                    'black_sweater_1': ['black_sweater', 'black_sweater_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/black_sweater/photo1626950506-4.jpeg', 'category', 'top'],
                    'brown_leather_jacket_1': ['brown_leather_jacket', 'brown_leather_jacket_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/brown_leather_jacket/photo1626950506-2.jpeg', 'category', 'top'],
                    'burgundy_t-shirt_1': ['burgundy_t-shirt', 'burgundy_t-shirt_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/burgundy_t-shirt/photo1626950499.jpeg', 'category', 'top'],
                    'dark_blue_coat_1': ['dark_blue_coat', 'dark_blue_coat_picture_id', 'gs://ai-stylist-bucket/my_closet/top_clothing/dark_blue_coat/photo1626950494.jpeg', 'category', 'top'],
                    'black_loose_trousers_1': ['black_loose_trousers', 'black_loose_trousers_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/black_loose_trousers/photo1626950501.jpeg', 'category', 'bottom'],
                    'black_formal_shorts_1': ['black_formal_shorts', 'black_formal_shorts_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/black_formal_shorts/photo1626950500.jpeg', 'category', 'bottom'],
                    'black_gegular_fit_trousers_1': ['black_gegular_fit_trousers', 'black_gegular_fit_trousers_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/black_gegular_fit_trousers/photo1626950503-1.jpeg', 'category', 'bottom'],
                    'black_sweatpants_1': ['black_sweatpants', 'black_sweatpants_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/black_sweatpants/photo1626950504.jpeg', 'category', 'bottom'],
                    'blue_gegular_fit_jeans_1': ['blue_gegular_fit_jeans', 'blue_gegular_fit_jeans_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/blue_gegular_fit_jeans/photo1626950503.jpeg', 'category', 'bottom'],
                    'blue_slim_jeans_1': ['blue_slim_jeans', 'blue_slim_jeans_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/blue_slim_jeans/photo1626950502.jpeg', 'category', 'bottom'],
                    'blue_slim_jeans_1': ['blue_slim_jeans', 'blue_slim_jeans_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/blue_slim_jeans/photo1626950502.jpeg', 'category', 'bottom'],
                    'dark_blue_gerular_fit_trousers_1': ['dark_blue_gerular_fit_trousers', 'dark_blue_gerular_fit_trousers_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/dark_blue_gerular_fit_trousers/photo1626950502-1.jpeg', 'category', 'bottom'],
                    'grey_jeans_shorts_1': ['grey_jeans_shorts', 'grey_jeans_shorts_picture_id', 'gs://ai-stylist-bucket/my_closet/bottom_clothing/grey_jeans_shorts/photo1626950496-1.jpeg', 'category', 'bottom'],
                    'black_white_casual_trainers_1': ['black_white_casual_trainers', 'black_white_casual_trainers_picture_id', 'gs://ai-stylist-bucket/my_closet/shoes/black_white_casual_trainers/photo1626950487.jpeg', 'category', 'shoes'],
                    'black_white_formal_trainers_1': ['black_white_formal_trainers', 'black_white_formal_trainers_picture_id', 'gs://ai-stylist-bucket/my_closet/shoes/black_white_formal_trainers/photo1626950487-1.jpeg', 'category', 'shoes']}

# fulfill_product_set(project_id=project_id, location=location, product_set_id=product_set_id, product_set_data=product_set_data)
# purge_products_in_product_set(project_id=project_id,location=location,product_set_id=product_set_id,force=True)

# gcloud beta ml vision product-search product-sets list-products --product-set=ai-stylist-test-product-set_id --location=us-west1
#DETECT AND CLASSIFY OBJECTS IN FOR PRODUCT SET-------------------------------------------------------------------------
def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))

# localize_objects(path='C:/Users/danii/Desktop/my_closet/references/reference_1.jpg')

def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = uri

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            return (' - ({}, {})'.format(vertex.x, vertex.y))

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

categories = ('Tee', 'Tank', 'Dress',
              'Shorts', 'Skirt', 'Blouse',
              'Top', 'Leggings', 'Hoodie',
              'Sweater', 'Romper', 'Culottes',
              'Kimono', 'Jumpsuit', 'Poncho',
              'Cardigan', 'Joggers', 'Blazer',
              'Jacket', 'Sweatpants', 'Jeans',
              'Cutoffs', 'Sweatshorts', 'Jeggings',
              'Jersey', 'Coat', 'Flannel',
              'Henley', 'Chinos', 'Button-Down',
              'Turtleneck', 'Trunks', 'Parka',
              'Peacoat', 'Capris', 'Gauchos',
              'Anorak', 'Robe', 'Kaftan',
              'Halter', 'Onesie', 'Bomber',
              'Caftan', 'Jodhpurs', 'Coverup', 'Sarong')

# from PIL import Image
# import requests
# from io import BytesIO

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

if 'Kaftan' in categories_overalls:
    print(True)
if 'Kaftan' in three_types_of_categories[2]:
    print(True)

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
    response = image_annotator_client.product_search(
        image, image_context=image_context)

    index_time = response.product_search_results.index_time
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

references = ['https://i.pinimg.com/736x/b3/2e/42/b32e424d87006792d1eeea79423a2cf2.jpg',
              'https://onpointfresh.com/wp-content/uploads/2016/08/tumblr_o2hadekN0v1uceufyo1_500.jpg',
              'https://onpointfresh.com/wp-content/uploads/2016/08/tumblr_o9iygiboae1uceufyo1_1280.jpg',
              'https://i.pinimg.com/originals/6c/cf/18/6ccf181f6261dd2b290dc395ac1d9007.jpg',
              'https://i.pinimg.com/originals/b2/ac/62/b2ac621b97e6999f2235ad4bba600ca4.jpg',
              'https://media.gq-magazine.co.uk/photos/5d1399512881cc9fe10a84a4/master/w_1280,h_1920,c_limit/Street-Style-06-27Nov17_Robert-Spangle_b.jpg',
              'https://i.pinimg.com/564x/1c/cc/be/1cccbe0ec79b484a367a704c8d08bfbf.jpg']


def find_clothing_set_for_each_reference(references):
    for reference_link in references:
        print('MATCHES FOR REFERENCE: %(reference_link)s '%{'reference_link' : reference_link})
        get_similar_products_url(project_id=project_id,
                                 location=location,
                                 product_set_id=product_set_id,
                                 product_category='apparel-v2',
                                 image_uri=reference_link,
                                 filter='')

# find_clothing_set_for_each_reference(references=references)


# def show_all_reference_picture(references):
#     for reference_link in references:
#         image = Image.open(requests.get(reference_link, stream=True).raw)
#
# show_all_reference_picture(references=references)

# from os import walk
# import re

def list_unique_categories(folder_link):
    existing_items = []
    main_folder_data = os.listdir(folder_link)
    for folder in main_folder_data:
        res = folder.split('_')[-1]
        if res not in existing_items:
            existing_items.append(res)
        # folder_data = os.listdir(folder)
        # for file in folder_data:
        #     extension = os.path.splitext(file)
        #     if extension == '*.jpg':
        #         print(file)
    return existing_items

# unique_items = list_unique_categories('C:/Users/danii/Desktop/img/img')
# print(unique_items)

# def list_all_files(folder_link):
#     main_folder_data = os.listdir(folder_link)
#     for folder in main_folder_data:
#         for file in folder:
#              print(file)
#
#
#

# list_all_files('C:/Users/danii/Desktop/img/img')

# if m == *.jpg

from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()
bucket_name = 'deep_fashion_test_bucket'
bucket = storage_client.get_bucket(bucket_name)

# Get blobs in bucket (including all subdirectories)
blobs_all = list(bucket.list_blobs())

# print(type(blobs_all))
# for blob in blobs_all[:1]:
    # print(dir(blob))
    # print('START')
    # print(blob.id.replace('/', ''))
    # print(blob.name.replace('/', ''))
    # print(blob.media_link)
    # print(blob.metadata)
    # print(blob.path)
    # print(blob.public_url)
    # pprint.pprint('gs://' + bucket_name + '/' + blob.name)
    # product_id = blob.id.replace('/', '')
    # product_display_name = blob.id.replace('/', '')

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



# create_deep_fashion_product_set(blobs_all=blobs_all[501: 1000])

# purge_products_in_product_set(project_id=project_id,location=location,product_set_id='deep_fashion_test_product_set_id',force=True)

def deep_fashion_can_add_item(existing_categories_top, existing_categories_bottom, existing_categories_overalls,  new_category):
    if(new_category in categories_top) and len(existing_categories_overalls) == 0:
        return True
    if(new_category in categories_bottom) and len(existing_categories_overalls) == 0:
        return True
    if(new_category in categories_overalls) and len(existing_categories_top) == 0 and len(existing_categories_bottom) == 0:
        return True
    return True

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
    # for key in recommendations:
    #     print(key, recommendations[key])
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

#-----------------------------------------------------------------------------------------------------------------------
#PART RELATED TO PRODUCT SEARCH WITH PATH REQUIRED
#-----------------------------------------------------------------------------------------------------------------------

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
    response = image_annotator_client.product_search(
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
    # for key in recommendations:
    #     print(key, recommendations[key])
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
