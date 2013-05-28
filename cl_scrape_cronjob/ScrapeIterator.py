"""

This class seeks to:
1. Use Beautiful Soup on a document from target_url
2. Process the Beautiful Soup data according the module_name called when
    initializing the class with customized_parser
3. Export the data to a unique file according to the JsonExport module
    according to a cronjob schedule based on the cron script stored in
    the local directory. This script is softlinked to the relevant cron
    folder.

Four arguments must be passed externally from the script importing this
class and should be documented here in the future:
    project_name:  ---
    project_target_url: ---
    module_name: ---
    max_iterations: ---

This class makes use of a few modules, all of which are imported at the
top.  It is launched from a virtual environment (virtualenv) with
beautifulsoup4 installed, and the relevant requirements met for that
module.


***** Export the "overlap detection" to the parser as a function!
***** Then people can change the detection function to fit their goals.
This class detects if there have been previous scrapes for a particular
project and seeks to iteratively process more data until there is overlap
in the previous and current data sets. That overlap is not reconciled
at this point, and must be cleaned up later in data processing. The overlap
is detected from a pickle of the last scrape dictionary that was json'd.



***** BUG FIX REQUIRED IN THE PARSER SCRIPTS
An edge case exists in the parsers, if something is duplicate posted between
scrapes, the parser will detect the duplicate post as the original and will
assume that the scraped data overlaps. 
This can be fixed by requiring numerous consecutive overlaps, and should be 
fixed in the parsers. 
It could also be fixed by including the HTML in the md5 key.  This would 
ensure that each unique POST to craigslist is captured, regardless of 
whether multiple posts have duplicate data.


"""
import os
import errno
import sys

import urllib
import time
import pickle
import importlib

from bs4 import BeautifulSoup

# Modules I've written for this:
import JsonExport

class scrape_iterator(object):

    """ 
    Accepts three arguments from the config parser and loader, and
    initializes a class for the project they represent.
    
    """

    def __init__(self, project_name, project_target_url, module_name,
                 max_iterations):
        # These variables are initialized here but passed with an instance
        self.project_name = project_name
        self.project_target_url = project_target_url
        self.module_name = "parsers." + str(module_name)
        self.max_iterations = max_iterations
        
        ## This is a little sloppy, as the pickle directory is also defined
        ## separately in the error handling function in deliver_dictionary()
        self.pickle_project_filename = "pickle/"+project_name+"_last.pickle"

        # This is the custom parser and is called directly from functions
        # that are called in each instance created in cl_scrape_cronjob
        self.customized_parser = importlib.import_module( 
                                                "parsers." + module_name )
    
    def scrape_and_soup(self, target_url):
        """ 
        Scrape a URL and make a soup.  This function is called inside
        the process_project_url function for the parser.

        If possible, it would be good to configure beautiful soup
        more specifically for individual projects, much like the
        parser functions that are called here as module_name.
        
        """

        # get the url contents for processing
        target_url_loc = urllib.urlopen( target_url )
        target_url_data = target_url_loc.read()
        target_url_loc.close()

        # prepare the soup that we will extract data from. 
        target_url_soup = BeautifulSoup( target_url_data, "lxml" )

        return target_url_soup


    def scrape_main_function(self, project_name, project_target_url, 
                            max_iterations ):
        """
        Package an instance of the scrape project into this function. 

        If the parser expects more than one page deep of data to be taken,
        this function should supply a few things:
        1. A transformation of the URL suitable for the next iteration.
        2. A for loop to iterate with.
        3. Bounds for the iteration, that define the max number of
            iterations possible. (just an int value, iterators start at 1)
        4. The dictionary should be passed back through this function to
            the deliver_dictionary function.
        5. Exit conditions should be passed to this function by the
            process_project_url function.
        6. The first page scraped is always completely pickled for use
            the next time the scraper runs. The pickled dictionary is
            generated here and pickled in deliver_dictionary.
        """

        ## declare these in the proper scope
        updated_dict = {}   ## will be updated up to max_iterations
        pickle_first_page = {}   ## pickle the first scraped page

        for each in range(0, max_iterations):
            add_dict = []
            # range returns 0,,(i-1)
            # get dict from scrape_parse_compare for each iteratively.

            if each > 0:
                mutated_url =  self.customized_parser.url_mutator ( 
                                                        each,
                                                        project_target_url )

                add_dict =     self.scrape_parse_compare(    
                                                    project_name,
                                                    mutated_url )

            else: 
                # only happens once, when range=0
                add_dict =     self.scrape_parse_compare(    
                                                    project_name,
                                                    project_target_url )
                """
                this preserves the first scraped dictionary
                and may be used to detect duplicates in the future
                depending on how loop_end_condition is written.

                the pickling function may need to be de-generalized into the
                parser in the future, and saved there, rather than here.
                """
                ## print add_dict
                pickle_first_page = add_dict[2]  ##add_dict[2] is necessary here!!


            updated_dict.update( add_dict[1] ) # update dict immediately

            # Write out the delivered results if this loop through satisfies
            # the end conditions in customized_parser.loop_end_condition()
            if add_dict[0] == True:
                
                self.deliver_dictionary( updated_dict, 
                                         pickle_first_page, 
                                         project_name )
                return ()

            time.sleep( .5 ) # this prevents too many server requests


        # Write out the delivered results.
        # Only occurs if no duplicates are ever found.
        '''
         this delivery function also passes the whole updated_dict
         as the file to be pickled.  This strongly increases the chances
         that there will be overlap from similar posting.
         it is recommended that a copy of the first page pulled be
         retained and plugged in here, which would be the first add_dict[1]


        '''
        self.deliver_dictionary( updated_dict, 
                                 pickle_first_page,
                                 project_name )
        return ()


    def scrape_parse_compare( self,
                              project_name, 
                              project_target_url  ):
        """
        Process everything into a dictionary. This fuction calls a module 
        that performs processing for the beautiful soup output. 
        
        This fuction will be generalized for all data extraction, not just
        craigslist and changes should be included in the called module.
        """

        # The url is downloaded and turned into soup here.
        project_target_url_soup = self.scrape_and_soup( project_target_url )

        # This is the parser! The new data is parsed here.
        # The parser points to an import in the class defined above.
        # The imported method comes from the config file.
        new_dict = {}
        prev_dict = {}
        new_dict.clear()
        new_dict = self.customized_parser.extract_from_soup( 
                                            project_target_url_soup )
      
        # Get the previous dict out of a pickle for comparison
        try:
            pickle_prev = open( self.pickle_project_filename, 'r')
        
        # Skip, if there is no pickle file for this project.
        except: 
            # If there is no pickle file, don't try to use loop_end_condition.
            return [ False, new_dict, new_dict ]

        prev_dict = pickle.load( pickle_prev )
        pickle_prev.close()

        # use a customized duplicates checking function to serve this data
        # do not disable this function here, you can allow this function to
        # return its inputs. Please read the documentation for this function
        # inside this function in your parser file.
        condition_dict_list = []
        condition_dict_list = self.customized_parser.loop_end_condition(
                                        new_dict, prev_dict )

        return condition_dict_list

    
    def deliver_dictionary( self, 
                            dictionary_to_json, 
                            dictionary_to_pickle, 
                            project_name ):

        """ Write the dictionary as a pickle and as a json file """

        ## write the current dict to a pickle file to compare next scrape
        ## The pickle file is used in the process_project_url method.
        
        ## This is a little sloppy, as the pickle directory is also defined
        ## separately in self.pickle_project_filename
        try:
            os.makedirs( "pickle" )
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        temp_file = open(self.pickle_project_filename, "w")
        pickle.dump( dictionary_to_pickle, temp_file )
        temp_file.close()

        ## Dump data into a unique json in the data/project_name directory
        ## Please Note: The results of the "data/"+project_name string.
        JsonExport.write( dictionary_to_json, project_name, "data/"+project_name )

        return ()
