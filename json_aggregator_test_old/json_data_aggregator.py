import json
import os
import md5

""" 
Purpose:

This module is designed to combine all the json files in a directory 
into one json file.

"""

directory_to_use = "./sfbay_data_052013/" ### include a trailing /
output_path_and_filename = "./sfbay_data_052013.json"


def import_file ( json_file_name, directory_to_use ):

    """
    Pass this function a "xyz.json" filename to import it and return 
    it as a variable.  This function is looped over during the function,
    process_the_directory in order to campture all data in the target
    directory.   
    """

    target_file = directory_to_use + json_file_name

    json_file = open( target_file, 'r' )
    json_as_dict = json.load( json_file )
    json_file.close()

    return ( json_as_dict )


def get_file_names ( directory_explored ):

    """ 

    Get all xyz.json filenames in the prescribed directory. 
    
    This module assumes all json files in the prescribed directory 
    are to be combined.

    This function will return a list of filenames 'xyz.json'  

    This module is currently configured to explore the directory this 
    module is in.

    """

    # get a list of ALL files in the specified directory
    file_name_list = os.listdir( directory_explored )
    
    # declare the list which will contain only the name of all json files
    json_files_list = []

    # store all the files with .json at the end in json_files_list
    for each in file_name_list:
        if each[-5:] == ".json":
            json_files_list.append( each )
        else:
            pass

    # return just the files with .json at the end
    return ( json_files_list )


def process_the_directory ( directory_with_json_files, filename_list ):
    """ Process all json files in directory_with_json_files  """


    # Declare the list which will contain each json dictionary
    list_containing_json_dicts = []

    # All dict data from all json files goes into list_containing_json_dicts
    for each in filename_list:
        list_containing_json_dicts.append( import_file( each, 
                                            directory_with_json_files ) )

    """
    this segment of the module just checks the md5 keys used as dict keys for 
    duplicates, and then zips the dictionary back together.

    If there is a duplicate, it currently keeps the first one in, which is
    currently based on the order of filenames in filename_list.  Eventually,
    this should be decided based on the timepoint or the html in the data tuple.
    Or something...

    update:
    052313 TAR: The scraper has been changed to notice duplicate data on the
    fly. This doesn't precede the need for collision detection here.  The
    best route for this software is to develop a error log that will alert
    the administrator when there is a collision and allow a person to solve
    the collision.  It could potentially attempt to solve simple collision
    cases first, e.g. if everything is identical or most things are
    sufficiently identical, or if some data is missing from one and not the
    other.

    """
    
    combined_md5_tracker = []
    combined_list_of_jsons = [] 
    for each_dict in list_containing_json_dicts:
        for each_key in each_dict.iterkeys():
            if each_key not in combined_md5_tracker:
                combined_md5_tracker.append( each_key )
                combined_list_of_jsons.append( each_dict[each_key]  )
            else:
                pass
    
    # This dict is the the combined data, with no overlaps based on md5 keys.
    return dict( zip(    combined_md5_tracker, 
                         combined_list_of_jsons ))
    
    
def export_dict_to_json ( dict_to_export, output_path_and_filename ):
    
    """ 
    Generic json dump function, needs expanded
    
    This portion of the function is easily served in the portion of the 
    original code dedicated to exporting to a json.

    
    """
    json_file = open ( output_path_and_filename, "w" )
    json.dump( dict_to_export, json_file )
    json_file.close()

    return ()


# Get the list of json files in the directory specified.
filename_list = get_file_names( directory_to_use )

compiled_dict = process_the_directory( directory_to_use, filename_list )

# Export the final compiled dictionary as a json file.
export_dict_to_json( compiled_dict, output_path_and_filename)

