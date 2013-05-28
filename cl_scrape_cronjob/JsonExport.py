"""
This is a json writing module reconfigured from a gutted csv writing module.

It generates a filename and potentially a folder based on supplied parameters.

The module is for generating a unique filename based on the current date down to
the second and then depositing the json file there.

Now that I'm repurposing the module for something else, I'm wondering if I couldn't
generalize it a little more in the first place.

The active function to call from your module is write.

Example:

import jsonexport
...
jsonexport.write( dict, file_name_root, directory_name )

Both directory_name and file_name_root are optional and user-defined content. 
An important note, if you exclude either, the default for both is 'output'. The
script must output to some subdirectory. I am not sure what will happen if a linux
system specifies ./  It actually may work...

"""

import datetime
import json
import os
import errno
import sys

def pick_file_name( file_name="output", target_dir="output" ):
    """ Generate a filename from the specified file_name and current time. """
    
    time_string = datetime.datetime.now().strftime("%m%d%Y.%H.%M.%S")
    name_of_file = "./" + target_dir + "/" + file_name + "." + time_string + ".json"
    return name_of_file


def dir_check ( target_dir ):
    """ Check if target_dir exists in ./ and, if not, create it. 

    For my reference:
    Add the dir ./target_dir to running directory if it doesn't exist.
    If the directory cannot be made, the os module will raise OSError.
    Module errno will ignore EEXIST (File exists) error, and raise
    an exception for all other errors.
    """
    try:
        os.makedirs( target_dir )
    except OSError as e: #record the OSError type as e, to pass to errno
        if e.errno != errno.EEXIST:  # check the error type against errno.EEXIST
            raise
    return


def write( any_dict, file_name="output", target_dir="output" ):
    """ This is the main function. """

    # Check and potentially create target_dir if it doesn't exist.
    dir_check( target_dir )

    # Pick a unique filename based on the user input and the datetime module.    
    file_path_name = pick_file_name( file_name, target_dir )

    # Write the file.
    if isinstance( any_dict, dict ):
        json_file = open( file_path_name, "w" )
        json.dump( any_dict, json_file )
        json_file.close()


    # I might want to make this an exception.
    else:
        sys.exit("jsonexport: ABORT! Input not a dict, write aborted! No data collected!")
    
    return
