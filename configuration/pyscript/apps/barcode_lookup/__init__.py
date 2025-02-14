# TODO: Adding a product adds it to the OpenFoodFacts and/or UPCDatabases also

# Test Barcodes
# 5000147030156 - Robinson squash - Found on OFF and UPCDB
# 5011309015416 - Covonia cough medcine - Not on OFF but on UPCDB
# 8710364042845 - Dremel EZ SpeedClic Discs - Not on either

####################################################################################################
# IMPORT MODULES
####################################################################################################
import requests
import json
import csv

####################################################################################################
# BARCODE LOOKUP
####################################################################################################
@service(supports_response="only") # Tells Pyscript to make this function available as a HA action
def barcode_lookup(barcode=0000000000000, return_response=True):
    """yaml
name: Barcode Lookup
description: Lookup a product barcode on the OpenFoodFacts API
fields:
    barcode:
        description: The product barcode to be looked up against the API.
        example: 5000147030156
        required: true
        selector:
            text:
    """
    product = {} # Python dictionary to return data to Home Assistant
    
    # If the cache_csv is set in the config the check it first
    if pyscript.app_config["cache_csv"] == None:
        log.info(f"Cache not configured in the config. Skipping searching the cache.")
    else:
        log.info(f"Looking for barcode {barcode} in the cache.")

        # Lookup the barcode in the cache file
        cache = task.executor(cache_lookup, barcode, pyscript.app_config["cache_csv"])
        
        if cache['result'] == 'success': # If it is found in the cache then return it from the cache
            product['result'] = 'success'
            product['source'] = 'Cache'
            product['barcode'] = cache['barcode']
            product['brand'] = cache['brand']
            product['title'] = cache['product']
            product['type'] = cache['type']
            product['quantity'] = cache['qty']
            log.info(f"Barcode {barcode} found in the cache.")
            return product
        elif cache['result'] == 'error': # If there was an error then log it and return
            product['result'] = 'error'
            product['source'] = 'Cache'
            product['error'] = cache['error']
            log.error(f"An error occurred while searching the cache: {cache['error']}.")
            return product
        else: # Log it wasn't found in the cache and move on
            log.info(f"Barcode {barcode} not found in the cache")

    # Check if off_url_base is set in the config
    if pyscript.app_config["off_url_base"] == None:
        log.info(f"off_url_base not configured in the config. Skipping searching the OpenFoodFacts.org API.")
    else:
        log.info(f"Looking for barcode {barcode} in on the OpenFoodFacts.org API.")

        # Try OpenFoodFacts.org for the product
        off = off_lookup(barcode)

        if off['result'] == 'success': # If it is found on the API then return it 
            product['result'] = 'success'
            product['source'] = 'OpenFoodFacts'
            product['barcode'] = off['barcode']
            product['brand'] = off['brand']
            product['title'] = off['title']
            product['type'] = off['type']
            product['quantity'] = off['quantity']

            # Log the found product
            log.info(f"Barcode {barcode} identified as {product['brand']} {product['title']} in the OpenFoodFacts.org API.")
            
            # Add it to the cache if configured
            if not pyscript.app_config["cache_csv"] == None:
                log.info(f"Adding {barcode} identified as {product['brand']} {product['title']} to the cache.")
                task.executor(cache_add, product, pyscript.app_config["cache_csv"])
            else:
                log.info(f"Cache not configured. Skipping adding {barcode} to the cache.")

            return product

        elif off['result'] == 'error': # If there was an error then log it and return
            product['result'] = 'error'
            product['source'] = 'OpenFoodFacts'
            product['error'] = off['error']
            log.error(f"An error occurred while searching the OpenFoodFacts API: {off['error']}.")
            return product
        else:
            log.info(f"Barcode {barcode} not found on OpenFoodFacts.")

    # If upcdb_url_base and upcdb_api_key are set in the config the check the UPCDatabase API
    if pyscript.app_config["upcdb_url_base"] == None or \
        pyscript.app_config["upcdb_api_key"] == None:
        log.info(f"upcdb_url_base or upcdb_api_key not configured in the config. Skipping searching the UPCDatabase API.")
    else:
        log.info(f"Looking for barcode {barcode} in on the UPCDatabase.org API.")
        
        # Try UPCDatabase.org for the product
        upcdb = upcdb_lookup(barcode)

        if upcdb['result'] == 'success': # If it is found on the API then return it 
            product['result'] = 'success'
            product['source'] = 'UPCDatabase'
            product['barcode'] = upcdb['barcode']
            product['brand'] = upcdb['brand']
            product['title'] = upcdb['title']
            product['type'] = upcdb['type']
            product['quantity'] = upcdb['quantity']

            # Log the found product
            log.info(f"Barcode {barcode} identified as {product['brand']} {product['title']} in the UPCDatabase.org API.")
            
            # Add it to the cache if configured
            if not pyscript.app_config["cache_csv"] == None:
                log.info(f"Adding {barcode} identified as {product['brand']} {product['title']} to the cache.")
                task.executor(cache_add, product, pyscript.app_config["cache_csv"])
            else:
                log.info(f"Cache not configured. Skipping adding {barcode} to the cache.")

            return product
        elif upcdb['result'] == 'error': # If there was an error then log it and return
            product['result'] = 'error'
            product['source'] = 'UPCDatabase'
            product['error'] = upcdb['error']
            log.error(f"An error occurred while searching the UPCDatabase: {upcdb['error']}.")
            return product
        else:
            log.info(f"Barcode {barcode} not found on UPCDatabase.")
    
    # Return that it wasn't found anywhere
    product['result'] = 'unknown'
    product['barcode'] = barcode
    return product

####################################################################################################
# ADD PRODUCT TO THE CACHE
####################################################################################################
# We need the function to be compiled to access the open() function but it then 
# can't access the Pyscript app config. So we create a wrapper function which 
# can be called from Home Assistant which then calls the compiled function.
@service(supports_response="only") # Tells Pyscript to make this function available as a HA action
def barcode_cache_add(barcode, title, brand="", type="other", quantity="", return_response=True):
    """yaml
name: Barcode Cache Add
description: Adds a product to the local cache of barcodes that have either been returned from wesites or manually entered.
fields:
    barcode:
        description: The product barcode. Normally a 13 digit number but can also be other lengths.
        example: 5000147030156
        required: true
        selector:
            text:
    brand:
        description: The brand of the product.
        example: Robinsons
        required: false
        selector:
            text:
    title:
        description: The name of the of the product.
        example: Summer Fruits Squash
        required: true
        selector:
            text:
    type:
        description: The type of product. Currently supported values are "food" and "other".
        example: food
        required: true
        selector:
            select:
                options:
                    - food
                    - other
    quantity:
        description: The quantity, weight, or measurement the product comes in.
        example: 1.5l
        required: true
        selector:
            text:
    """
    # Create a dictionary for the product
    product = {}
    product["barcode"] = barcode
    product["brand"] = brand
    product["title"] = title
    product["type"] = type
    product["quantity"] = quantity

    # Call the compiled function that can access the file with open()
    result = task.executor(cache_add, product, pyscript.app_config["cache_csv"])
    return {"result": "success"} if result == True else {"result": "failed"}

@pyscript_compile # Tells Pyscript to compile the function
def cache_add(product, file):

    # Sort the passed product object into a row ready for the csv to make sure it is in the correct order etc
    row = [product['barcode'], product['brand'], product['title'], product['type'], product['quantity']]

    # Open the cache csv in append mode and create a file object
    with open(file, 'a') as cache_f_obj:
        cache_w_obj = csv.writer(cache_f_obj) # Pass the file object to csv.writer() to get a writer object
        cache_w_obj.writerow(row) # Add the row to the writer object
        cache_f_obj.close # Close the file object

        return True
    return False

####################################################################################################
# CACHE LOOKUP
####################################################################################################
@pyscript_compile
def cache_lookup(barcode, file):
    product = {} # Dictionary to pass back

    try:
        with open(file, 'r') as cache_f_obj: # Open the cache file in read mode
            for row in csv.reader(cache_f_obj): # Loop through the rows
                if row[0] == str(barcode): # If the row matches the barcode
                    # Fill out the dictionary to returm
                    product['result'] = 'success'
                    product['barcode'] = barcode
                    product['brand'] = row[1]
                    product['product'] = row[2]
                    product['type'] = row[3]
                    product['qty'] = row[4]
                    cache_f_obj.close # Close the file
                    return product

            # If the barcode isn't found in the file return unknown
            product['result'] = 'unknown'
            product['barcode'] = barcode
            cache_f_obj.close # Close the file
            return product
            
    except requests.exceptions.RequestException as e: # If an error occured return it
        product['result'] = 'error'
        product['error'] = e
        return product

####################################################################################################
# CLEAR THE CACHE
####################################################################################################
# We need the function to be compiled to access the open() function but it then 
# can't access the Pyscript app config. So we create a wrapper function which 
# can be called from Home Assistant which then calls the compiled function.
@service(supports_response="only") # Tells Pyscript to make this function available as a HA action
def barcode_cache_clear(return_response=True):
    """yaml
name: Barcode Cache Clear
description: WARNING THIS CAN'T BE UNDONE! Clears the local cache of barcodes that have either been returned from wesites or manually entered.
    """
    # Call the compiled function that can access the file with open()
    result = task.executor(cache_clear, pyscript.app_config["cache_csv"])
    return result

@pyscript_compile
def cache_clear(file):
    result = {} # Dictionary to pass back

    # Clear the csv file
    with open(file, 'w+') as cache_f_obj: # w+ opens the file in write mode but truncates the file
        # Recreate the header row
        header_row = ['barcode', 'brand', 'product', 'type', 'qty']
        # Pass the file object to csv.writer() to get a writer object
        cache_w_obj = csv.writer(cache_f_obj)
        # Add the row to the writer object
        cache_w_obj.writerow(header_row)
        # Close the file
        cache_f_obj.close()

        result['result'] = 'success'
        return result

####################################################################################################
# OPEN FOOD FACTS
####################################################################################################
# The OpenFoodFacts.org API returns JSON containing data for the product. If the product isn't found
# in the database then the API returns a 404.
def off_lookup(barcode):
    # Create a dictionary to return the result in
    product = {}

    # Build the URL for the OpenFoodFacts API call
    off_url = f'{pyscript.app_config["off_url_base"]}{barcode}.json'

    # Make the API request
    response = task.executor(requests.get, off_url) 

    # Log the call and response
    log.info(f"Call to {off_url} returned {response.status_code}")

    # If it returned a 200 code return the product
    if response.status_code == 200:
        # Parse the JSON
        json_data = json.loads(response.content)

        # Check the API is actually reporting a success and has a product name
        if json_data.get('status') == 1 and \
            len(str(json_data.get('product').get('product_name') or '')) > 0:
            # Populate the product from the OFF returned JSON
            product['result'] = 'success'
            product['source'] = 'OpenFoodFacts'
            product['barcode'] = barcode
            product['brand'] = str(json_data.get('product').get('brands') or '').split(',')[0]
            product['title'] = str(json_data.get('product').get('product_name') or '').replace(',', '')
            product['type'] = str(json_data.get('product').get('product_type') or '').split(',')[0]
            product['quantity'] = str(json_data.get('product').get('quantity') or '').split(',')[0]
            return product
        else:
            product['result'] = 'unknown'
            product['source'] = 'OpenFoodFacts'
            product['barcode'] = barcode
            return product

    # If it returned a 404 return unknown
    elif response.status_code == 404:
        product['result'] = 'unknown'
        product['source'] = 'OpenFoodFacts'
        product['barcode'] = barcode
        return product
    # Any other code
    else:
        product['result'] = 'error'
        product['source'] = 'OpenFoodFacts'
        product['error'] = response
        return product

####################################################################################################
# UPC DATABASE
####################################################################################################
# The UPCDatabase API returns a 200 code whether the product is found or not. A "result" fiels in 
# the returned JSON indicated is the product was found or not. The API seems to have some issues and
# often returns some HTML before the JSON so this needs to be handled
def upcdb_lookup(barcode):
    product = {}

    # Build the URL for the UPCDatabase API call
    upcdb_url = f'{pyscript.app_config["upcdb_url_base"]}{barcode}?apikey={pyscript.app_config["upcdb_api_key"]}'

    # Make the API request
    response = task.executor(requests.get, upcdb_url) 

    # Log the call and response
    log.info(f"Call to {upcdb_url} returned {response.status_code}")

    # If it returned a 200 code 
    if response.status_code == 200:
        # The UPCDatabase API sometimes returns a load of rubbish before the JSON. So we get rid of 
        # it, stripping out everything before the first "{".
        response_text = response.text
        json_start = response_text.find('{')
        response_clean = response_text[json_start:]

        # Now it's clean, parse the JSON
        json_data = json.loads(response_clean)

        # If the product is successfully returned from the API 
        if json_data.get('success') == True:
            if len(json_data.get('title')) > 0 or \
                len(json_data.get('alias')) > 0 or \
                len(json_data.get('description')) > 0:
                # Populate the product from the UPCDatabase returned JSON
                product['result'] = 'success'
                product['source'] = 'UPCDatabase'
                product['barcode'] = barcode
                product['brand'] = str(json_data.get('brand') or '').split(',')[0]
                if len(json_data.get('title')) >0:  
                    product['title'] = str(json_data.get('title') or '').replace(',', '') 
                elif len(json_data.get('alias')) >0:
                    product['title'] = str(json_data.get('alias') or '').replace(',', '') 
                else:
                    product['title'] = str(json_data.get('description') or '').replace(',', '') 
                product['type'] = str(json_data.get('category') or '').split(',')[0].lower()
                if not json_data.get('metadata') == None:
                    product['quantity'] = str(json_data.get('metadata').get('quantity') or '').split(',')[0]
                else: 
                    product['quantity'] = ''
                return product
            else:
                product['result'] = 'unknown'
                product['source'] = 'UPCDatabase'
                product['barcode'] = barcode
                return product

        # If the barcode is not in the database0
        elif json_data.get('success') == False:
            product['result'] = 'unknown'
            product['source'] = 'UPCDatabase'
            product['barcode'] = barcode
            log.info(f"Barcode {barcode} not found in UPCDatabase database")
            return product
        # If an unknown error occurs
        else:
            product['result'] = 'error'
            product['source'] = 'UPCDatabase'
            product['error'] = response
            return product

    else:
        product['result'] = 'error'
        product['source'] = 'UPCDatabase'
        product['error'] = response
        return product
