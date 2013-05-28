"""

1. Generate a clean database from scraped data using regular expressions into
    a json output.  

2. Use derivative data to flesh out the objects before proceeding.  Collect
    the region from the filename and collect the subregion from the url.
    Learn if any data exists in the pid...

3. Once this data is generated, it should be totally independent of the raw 
    data.

4. Aggregate? What are standard ways to arrange file sizes in json databases?
"""

import json
import re
import JsonExport

""" temporary input for tests """

temp_db_name = "json_cl_sfbay_apa.05202013.09.35.25.json"
temp_project_name = "clean_data_obj_db"


def json_db_importer ( db_filename ):

    """Do I really want to put the whole database into a dict file? yes."""

    temp_file = open(db_filename, "r")
    json_db_dict = json.load(temp_file)
    temp_file.close()

    return json_db_dict


def object_exporter ( json_db_dict,  project_name ):

    JsonExport.write( json_db_dict, project_name, project_name )

    return


def object_parser ( json_db_dict ):
    
    """ 
    This function parses each object using regular expressions. 
    
    The output will be the finalized json dictionary.

    This function will create an object for each previous object, using
    the md5 code supplied.  Each such object will contain an object for
    each separate piece of data available for that apartment entry. The
    object title for each object will be uniform across all such objects
    and will be a proper descriptor for the information contained.

    """

    for each in json_db_dict.iteritems():
        
        print each[0]  ## create a dict object for each[0]
        """ This is the name under which the object will be saved. """


        for item in each[1:]:
            """ here the object will be created for each piece of data """



            print item[0] # this is the data object captured
            # 1. separate, format, and assign all retrieved data object types
            
            ###
            ### Latitude:
            ###
            if re.search("latitude", item[0]) == None:
                latitude = "NA"
            else:
                tail_latitude = re.split("data-latitude=\"", item[0], 1)
                head_latitude = re.split("\" data-longitude=", tail_latitude[1], 1)
                latitude = head_latitude[0]
            print latitude, "latitude"


            ###
            ### Longitude:
            ###
            if re.search("longitude", item[0]) == None:
                longitude = "NA"
            else:
                tail_longitude = re.split("data-longitude=\"", item[0], 1)
                head_longitude = re.split("\" data-pid=", tail_longitude[1], 1)
                longitude = head_longitude[0]
            print longitude, "longitude"
            
            ###
            ### pid:
            ###
            if re.search("data-pid", item[0]) == None:
                pid = "NA"
            else:
                tail_pid = re.split("data-pid=\"", item[0], 1)
                head_pid = re.split("\">", tail_pid[1], 1)
                pid = head_pid[0]
            print pid, "pid"

            ###
            ### supertitle -- end_url/title/sub-location
            ###
            tail_supertitle = re.split("<span class=\"pl\"> <span class=\"star\"></span> <a ", item[0], 1)
            head_supertitle = re.split("</a>", tail_supertitle[1], 1)
            supertitle = head_supertitle[0]
            print supertitle, "supertitle"

            ###
            ### end_url/title:
            ###
            tail_end_url = re.split("href=\"", supertitle, 1)
            print tail_end_url
            head_end_url = re.split("\">", tail_end_url[1], 1)
            print head_end_url
            end_url = head_end_url[0]
            print end_url, "= end_url"
            ### rebuild complete URL frrm end_url
            full_url = "http://www.craigslist.org" + end_url
            print full_url
            title = head_end_url[1]
            print title, "= title"
            
            """ Make a function that specifies the main location from
                the filename.  From there, use that to determine the
                sublocation in the thing below. Separate this whole
                process into individual independent (or dependent)
                functions to make sure the process is easy to change and
                work with in the future.  This is additional postprocessing
                and parsing and will need to be easy to alter and update for
                future data acquisition and analysis in this and other 
                projects."""


            ###
            ### get the sub location... IT NEEDS THE MAIN LOCATION
            ### because it will have to compare to the main location
            ### and give NA if the sub location is the same as the
            ### main location (basic case)
            ###
            sub_loc_key_list = re.split("/", end_url)
            print sub_loc_key_list[1]

            
            
            # 2. separate, format, and assign date and time objects
            obj_list = re.split(':', item[1], 1) 

            obj_date = obj_list[0]
            obj_time = re.sub("\.", ":", obj_list[1])
            print obj_date
            print obj_time


    return json_db_dict



""" temporary executer """
db_dict_to_parse = json_db_importer ( temp_db_name )

final_json_object_output = object_parser( db_dict_to_parse )

object_exporter ( final_json_object_output, temp_project_name )




