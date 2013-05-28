import urllib
import unicodedata
import csvexport
import time
from bs4 import BeautifulSoup

#target_url = urllib.urlopen("http://www.craigslist.org/about/sites")
#target_url_soup = target_url.read()
#target_url.close()

#soup = BeautifulSoup(target_url_soup)


f = open('cl_locations_031013.txt', 'r')
html_doc = f.read()
f.close()

soup = BeautifulSoup(html_doc)

content_export = soup.prettify()

href_list = []
location = []
project_name = []
max_iterations = [] # default is 10
parser_list = [] # default is parser_cl_ANYCITY_apa


"""
for each in soup.find_all('a'):
    try:
        print str(each.get('href'))
        print str(each.get_text())
    except:
        pass
"""

for each in soup.find_all('a'):
    try:

        # get the location and find a place to store this. we might need a 
        # universal project file in the data/project_name directory
        location.append( str(each.get_text()) )

        # make a project name from the concatenated URL name from CL
        project_name.append( "json_cl_" + str(each.get('href')).replace("http://","").replace(".craigslist.org","")  + "_apa" )

        # make the html file... might want to test this
        link_loc = str(each.get('href')) + "/apa/" 
        
        # soup this URL to find if it is 404 (baseline failure)
        test_url = urllib.urlopen( link_loc )
        test_url_text = test_url.read()
        test_url.close()
        test_soup = BeautifulSoup( test_url_text )
        time.sleep( 0.3 ) # prevent too many server requests at once.

        if test_soup.title.string == "craigslist | Page Not Found":
            print "Fail case: ", link_loc, " - Fail ignored. Case still in database.\n"
        else:
            print link_loc, "Success.\n"
        href_list.append( link_loc )

        # this is the default for cl apartments
        parser_list.append( "parser_cl_ANYCITY_apa" )

        # 10 is the default
        max_iterations.append( "10" )
    except:
        pass

configuration_tuple = zip( project_name, 
                           href_list, 
                           parser_list, 
                           max_iterations, 
                           location )


output_file = open("new_config_file_rename_me.cfg", "w")

for tuple in configuration_tuple:
    for item in tuple:
        #print str(item)
        output_file.write( str(item) + "\t\t" )
    output_file.write( "\n" )

output_file.close()


####################

#csvexport.write( configuration_tuple,   "cl_scrape_cronjob.csv.generated", 
#                                        "config_file_gen")

#unicodedata.normalize('NFKD', content_export).encode('ascii','ignore')

#content_export.encode('ascii', 'replace')

#print content_export.encode('ascii', 'replace')

#csvexport.write( content_export.encode('ascii', 'replace'), "craigslist.about.sites", "rawxml" )

#for link in soup.find_all('a'):
#    print(link.get('href'))
#    print(link)

