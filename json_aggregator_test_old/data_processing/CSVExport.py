"""
This module is intended for exporting a list or list of lists to a CSV file with
the special feature of creating a unique timestamped CSV each time it runs.

This feature is particularly nice when learning manipulate and dump large
chunks of data, because you are probably trying to manually check a lot.
In order to use the module, import the module and call the fuction as:

csvexport.write(any_list, file_name, target_dir)

The output file will have the format "./target_dir/file_name.MMDDYYYY.HHMMSS.csv"

Please note that you should not create more than one file per second.
This can be changed in the pick_file_name function, down to the microsecond.

Future goals: Handle numpy arrays (not sure what would happen with this implementation).
"""

import datetime
import csv
import os
import errno


def pick_file_name( file_name="output", target_dir="output" ):
    """ Generate a filename from the specified file_name and current time. """
    
    time_string = datetime.datetime.now().strftime("%m%d%Y.%H%M%S")
    name_of_file = "./" + target_dir + "/" + file_name + "." + time_string + ".csv"
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


def write( any_list, file_name="output", target_dir="output" ):
    """ write the list passed to csvexport.write() and call all support functions. """

    # Check and potentially create target_dir.
    dir_check( target_dir )

    # Pick a file name for your new datetime-stamped CSV file.    
    file_path_name = pick_file_name( file_name, target_dir )

    # Iterate over any_list into each line of the CSV file.
    line_write = csv.writer( open( file_path_name, 'wb' ), delimiter=',' )
    if isinstance( any_list, list ):
        for each in any_list:
            if isinstance ( each, list ):
                line_write.writerow( each )
            else:
                line_write.writerow( [ str( each ) ] )

    # I might want to make this an exception.
    else:
        print "csvexport: not a list, turning into a single-item list."
        line_write.writerow( [ str(any_list) ] )
    return
