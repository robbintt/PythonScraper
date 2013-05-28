import ScrapeIterator

"""
    This module will generate an instance of ScrapeIterator for each
    line of the config file.  Each line of the config file should represent
    a separate craigslist webpage that will be scraped as a cronjob per the
    specifications of the cl_scrape_cronjob project.

    This function allows the application to be extensible with the sizeable
    caveat that each instance is governed by its parser file, which is the
    third argument passed to the ScrapeInstanceClass object.
    
    As such, for each new project, a new parser file will be defined, and
    all data collected is governed by the parser.  If the 'soup' generated
    by BeautifulSoup changes or if the webpages are changed, the changes 
    must be reflected in how the parser file collects data.

    The parser file is also where data collection optimizations should take 
    place.

    Calling config_iterator( config_filename ) at the bottom bootstraps the 
    entire project.

    """

config_filename = "cl_scrape_cronjob.cfg"

def config_iterator( config_filename ):
    """
    This function is currently extremely succeptible to bad formatting in 
    the config file, and can basically explode and die a fiery death if it 
    isn't perfect.

    Obviously, this needs attention.
    
    """

    scrape_instance_list = []
    for each in loop_over_file( config_filename ):
        scrape_instance_list.append( ScrapeIterator.scrape_iterator( 
                                                each[0],
                                                each[1],
                                                each[2],
                                                int(each[3]) )) 
                                               
        scrape_instance_list[-1].scrape_main_function( 
                            scrape_instance_list[-1].project_name, 
                            scrape_instance_list[-1].project_target_url,
                            scrape_instance_list[-1].max_iterations )

def loop_over_file( config_file ):

    """
        Parse a specific format config file.
        The format is defined in cl_scrape_cronjob.config

    """

    # ADD: Implement a try and raise an exception if there is no config file
    config_file = open( config_file, "r")
    config_list = config_file.readlines()
    config_file.close()


    # Strip empty lines and lines that begin with hashmarks from config_list
    relevant_lines = []
    for each in config_list:
        each = each.strip()
        head,sep,tail = each.partition('#')
        head = head.strip('\r\n')
        if head != "":
            relevant_lines.append( head )
    
    # Split the relevant lines into words and append the list of words to 
    # config_attributes.
    config_attributes = []
    for each in relevant_lines:
        config_attributes.append( each.split() )
    
    # Return a list of lists, each list will represent a class instance
    return( config_attributes )

# This bootstraps the whole thing.
config_iterator( config_filename )
