from bs4 import BeautifulSoup
import md5
import datetime
import re
import copy

"""
A list of functions:
    *make_soup_if_necessary()
    extract_from_soup()
    url_mutator()
    loop_end_condition()
    *standalone_writer()

note:  * never called externally

note:   no functions call each other. all functions are called
         externally.
        a dict of results from extract_from_soup() is fed 
         to loop_end_condition().
        loop_end_condition() cleans duplicate entries from the dict based on
         the unpickled prev_dict dictionary file.
        loop_end_condition() returns a list with an end condition which
         is true if an old datapoint is hit, false if max_iterations is hit.

"""


def make_soup_if_necessary():
    """
    This function is only to be used as a standalone placeholder if this parser 
    isn't plugged into a bigger framework. Best used to create a new parser.

    Be sure to enable the code at the bottom if you are using this function.
    """
    import urllib
    target_url = "http://sfbay.craigslist.org/sfc/apa"
    target_url_loc = urllib.urlopen( target_url )
    target_url_data = target_url_loc.read()
    target_url_loc.close()
    target_url_soup = BeautifulSoup( target_url_data )

    return target_url_soup


def extract_from_soup( target_url_soup ):
    """
    This is a parser function for data extraction from websites using 
    beautifulsoup4.

    This parser is for use with a framework, but there are standalone functions 
    in this file.  The standalone functions are for making or debugging a parser.

    While the skeleton of this function will probably be used a lot, I expect 
    this to change significantly for every webpage scraped.

    This iteration is for "http://sfbay.craigslist.org/sfc/apa"
    """

    datetime_now = datetime.datetime.now().strftime("%m.%d.%Y:%H.%M.%S")

    # Declare a list for each variable extracted below.
    title_list = []
    href_list = []
    cost_list = []
    info_list = []
    loc_list = []
    datetime_pulled = []

    # Iteratively extract the data into a list that goes to a dictionary.
    for each in target_url_soup.find_all('p'):
        ##  Filter this thing which gets caught in the craigslist data.
        if each.a.string == "next 100 postings":
            pass
        else:
            # Get the title, get none on an exception
            try:         
                #print str(each.a.string)
                post_title = str(each.a.string)
            except:
                post_title = ""
            
            # Get the hyperlink, get none on an exception
            try:
                #print str(each.a.get('href'))
                post_href = str(each.a.get('href'))
            except:
                post_href = ""

            # Get the cost/info, get none on an exception
            post_cost = ""
            post_info = ""
            try:
                #print str(each.find("span", 
                #                   "itemph").string).strip().strip('-').strip()
                post_cost_info = str(each.find("span", 
                                    "itemph").string).strip().strip('-').strip()
                

                # Use a regular expression to parse this data further
                if re.match("\$", post_cost_info) is None:
                    post_info = str(post_cost_info).strip()

                else:
                    # If there is no /, assign as dollars.
                    if re.search("/", post_cost_info) is None:
                        post_cost = str(post_cost_info).strip().strip('$')
                    
                    # chop up any entry with $COST / x br
                    else:
                        cost_info_list = [] # list to receive re.split()
                        cost_info_list = re.split('/', post_cost_info, 1 )
                        post_cost = str(cost_info_list[0]).strip().strip('$')
                        post_info = str(cost_info_list[1]).strip()
            
            # Close the above try block for cost and info
            except:
                pass                

            # Get the location, get none on an exception
            try: 
                #print str(each.find("span", 
                #                    "itempn").string).strip().strip('()')
                post_loc = str(each.find("span", 
                                         "itempn").string).strip().strip('()')
            except:
                post_loc = ""
        
        ## Add all extracted items to their respective lists.
        ## We are still in the above loop here.  All lists will get an entry.
        ## This keeps the lists in step in the case of bad entries, so they can
        ## still be zipped, but with blank spaces. Some data is better than
        ## no data.
        title_list.append( post_title )
        href_list.append( post_href )
        cost_list.append( post_cost )
        info_list.append( post_info )
        loc_list.append( post_loc )
        ## Append the datetime_now to each tuple, kept in step.
        datetime_pulled.append( datetime_now )

    # Zip the lists collected in the for loop into a tuple.
    # The tuple is the value of the dict/json.
    extracted_data_tuple = zip(title_list, 
                               href_list, 
                               cost_list,
                               info_list,
                               loc_list, 
                               datetime_pulled)
    """
    This tuple is used for MD5 generation because it excludes the unique 
    datetime attribute.  This would salt the MD5 and we want the md5 to 
    represent the data inside so we can detect duplicates.

    I have now also removed the href_list because of duplicate posts
    The likelihood of different people having the same title, cost, info, and
    location is still very low and won't affect data.
    """
    extracted_data_tuple_nouniquetime = zip(title_list, 
                               cost_list, 
                               info_list, 
                               loc_list)
    
    md5_key_list = []
    # Generate a list of md5 keys from the data tuple, the md5s are the keys. 
    for each in extracted_data_tuple_nouniquetime:
        eachmd5 = md5.new()
        eachmd5.update( str(each) )
        md5_key_list.append( str( eachmd5.hexdigest() ) )

    # Zip a tuple and convert into a dictionary for JSON extraction
    extracted_data_dict = dict( zip( md5_key_list, extracted_data_tuple ) )

    return ( extracted_data_dict )


def url_mutator( iteration, base_url ):
    """
    This function is called when max_iterations is higher than 1, although
    max_iterations may be bounded by the capabilities of this function.
    
    When passed iteration, the url_mutator will return a URL for that
    iteration.

    While called a mutator function, this function can simply return a
    list based on the "iteration" integer passed if desired, but the true
    purpose of the mutator is to provide a space to generate successive URLs
    on the fly for appending successive webpages of data onto the dataset.
    
    """
    # This case doesn't currently exist but just in case.
    if iteration == 0:
        return base_url
    else:
        next_craigslist_index = str( 100 * iteration )
        mutated_url = base_url + "index" + next_craigslist_index + ".html"
        return mutated_url


def loop_end_condition( new_dict, prev_dict ):
    """
    This function is built in order to provide customizability of end
    conditions when snagging multiple pages of data for one project.
    
    The textbook use case of this module is for craigslist when you want to
    grab enough data to have your previous scrape overlap with your current
    one.  Any time you have a persistent setup like this, you can use this
    function.  This function can also chop out parts of your dicts if you
    wish to do a more fine-grained overlap for this project.

    *** This function can be left to return [ False, new_dict ] if you don't
    desire to use it.  
    
    As there are no mechanisms to capture errors, be sure
    to at least pass new_dict back if nothing else. If you return nothing it 
    WILL FAIL.
    
    """
    end_condition = False
    
    ## This deepcopy will be the duplicate-purged copy of new_dict
    truncated_new_dict = copy.deepcopy( new_dict )

    ## purge new_dict of any overlapping entries with prev_dict 
    ## using the md5 checksum dict key.
    for entry in new_dict:
        if entry in prev_dict:
            end_condition = True
            del truncated_new_dict[entry]
            

    return [ end_condition, truncated_new_dict, new_dict ]


def standalone_writer( extracted_data_dict ):
    """
    The FINAL part of the standalone functions for this code. This will be 
    automatically used if the function at the bottom is called to tool out
    a new parser.
    
    Otherwise, no changes here affect the scraper framework.
    """
    import JsonExport ## Make sure JsonExport.py is available in this directory.
    JsonExport.write( extracted_data_dict, "standalone_parse", 
                      "standalone_parse" )

## Be certain the function calls are commented out below if you are 
## using this as a parser.
## This line is ONLY to be used when make_soup_if_necessary() is
## being used as a standalone to create the soup for parsing.
## standalone_writer( extract_from_soup( make_soup_if_necessary() ))


