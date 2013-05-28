import urllib
import unicodedata
import csvexport

target_url = urllib.urlopen("http://www.craigslist.org/about/sites")
target_url_soup = target_url.read()
target_url.close()

from bs4 import BeautifulSoup
soup = BeautifulSoup(target_url_soup)

content_export = soup.prettify()


#for each in target_url_soup.find_all('p'):
#    try:
#        print str(each.a.string)
#    except:
#      pass

#unicodedata.normalize('NFKD', content_export).encode('ascii','ignore')

#content_export.encode('ascii', 'replace')

print content_export.encode('ascii', 'replace')

csvexport.write( content_export.encode('ascii', 'replace'), "craigslist.about.sites", "rawxml" )

#for link in soup.find_all('a'):
#    print(link.get('href'))
#    print(link)

