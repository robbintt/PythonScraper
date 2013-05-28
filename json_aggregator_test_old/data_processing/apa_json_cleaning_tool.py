import json
import os
import re
import CSVExport


""" 
Purpose:

This module will import a json for manipulation and post-acquisition 
processing.

I can use this as boilerplate for each time I process json data or I could 
create specialized parsing modules that are passed to this code as
extension modules. For an example, see the cl_scrape_cronjob project.

"""


##  These can eventually go into argv or be assigned elsewhere.
directory_to_process_at = "./"
json_file_name = "apartment_data_day1.json"
project_name = "cleaned_apartment_data"



def import_file ( json_file_name, target_directory ):

    """

    Pass this function a "xyz.json" filename to import it and return it
    as a dictionary file. 
    
    """
    target_file = target_directory + json_file_name

    json_file = open( target_file, 'r' )
    json_dict = json.load( json_file )
    json_file.close()

    return( dict( json_dict ))


def process_the_json ( json_file_name, target_directory ):
    """ 
    Post-acquisition json processing. This is a highly specific 
    region of code, written to clean specific information in the 
    target json file.

    ***
    Should I include the processing as a parser module? Perhaps
    I should separate the parser function in the parser code if 
    it isn't already totally separated. then I could call the 
    parser function from the parser module here for any function
    during data cleaning/organization.


    """
    # Import the json into a dictionary.
    json_dict = import_file( json_file_name, target_directory )


    # Perform data cleaning and processing on the json dictionary. 
    dict_to_list = []
    for each_key, each_value in json_dict.iteritems():
        new_list = []
        for item in each_value:
            new_list.append( str(item) )
        dict_to_list.append( new_list )
   

    # Lets extract areas with $ signs.
    cleaned_values_list = []
    for each in dict_to_list:
        string_list = []
        # append the first two items in each to string_list
        string_list.append( each.pop(0) )
        string_list.append( each.pop(0) )

        # We will be expandind each list by one to account for $ 
        # and bedrooms.

        # If there are no $, pass the bedrooms.
        if re.match("\$", each[0]) is None:
            string_list.append( "" )
            string_list.append( str(each[0]).strip() )
        
        else:
            # If there is no /, pass the dollars.
            if re.search("/", each[0]) is None:
                string_list.append( str(each[0]).strip('$') )
                string_list.append( "" )
           
            # chop up any entry with $COST / x br
            else:
                cost_and_rooms = re.split('/', each[0], 1 )
                string_list.append( 
                    (str(cost_and_rooms[0])).strip().strip('$') )
                string_list.append( 
                    (str(cost_and_rooms[1])).strip() )
        done_with_it = each.pop(0) # This has now been appended.        
        for item in each:
            string_list.append( str(item) )
#        print len(string_list)
#        print string_list
#        print "\n"
        
        # construct the new list of lists
        cleaned_values_list.append( string_list )
    

    return ( cleaned_values_list )



# Run the module:
CSVExport.write( process_the_json(json_file_name, directory_to_process_at),
                 project_name, project_name) 

