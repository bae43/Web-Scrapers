import sys
import os
import re
import requests
import json
import urllib3
from bs4 import BeautifulSoup

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: %s in.obj out.msh\n" % sys.argv[0])
        sys.exit(1)

    infile_fullname = sys.argv[1]
    inFile = open(infile_fullname, 'r')
    fileName, fileExtension = os.path.splitext(infile_fullname)
    outFile = open(fileName+"_out"+fileExtension, 'w')
    outFileL = open(fileName+"_links"+fileExtension, 'w')

    points = []

    # removes header
    next(inFile)
    next(inFile)


    for line in inFile:
        splitLine = line.strip().split(" ", 6)

        if len(splitLine) == 7:
            index = splitLine[0]
            people_count = splitLine[1]
            photo_count = splitLine[2]

            lat = re.sub('[(,)]', '', splitLine[3])
            lng = re.sub('[(,)]', '', splitLine[4])

            city = splitLine[5]
            tagset = splitLine[6].strip()
            tags = tagset.split()
            points.append((lat,lng)) 

            response = requests.get('http://api.wikilocation.org/articles?lat='+lat+'&lng='+lng)

            # init links array
            links = []

            # get objects from JSON
            objs = response.json()["articles"]
            

            # initialize vars for best URL
            best_tag_count = 0
            best_title = ""
            best_url = ""
            # for best list items
            best_tag_count_l = 0
            best_title_l = ""
            best_url_l = ""

            for obj in objs:
                url = obj["url"]
                links.append(url)

                http = urllib3.PoolManager()
                page = http.request('GET', url).data
                soup = BeautifulSoup(page)

                # extracts and formats Wiki Title
                title = str(soup('title')[0])[7:-43]
                title_formatted = (title.lower()).replace(" ","")

                # manual bypass of listing pages
                #if "list" not in title_formatted:
                
                # Finds title that matches the most tags
                tag_count = 0
                for tag in tags:
                    if tag in title_formatted:
                        tag_count += 1


                if "list" not in title_formatted:

                    if tag_count > best_tag_count:
                        best_tag_count = tag_count
                        best_url = url
                        best_title = title
                        #print("norm page: " + title + str(tag_count))
                else:
                    if tag_count > best_tag_count_l:
                        best_tag_count_l = tag_count
                        best_url_l = url
                        best_title_l = title
                        #print("list page: " + title + str(tag_count))


            # use list pages as last resort
            if best_title == "":
                best_title = best_title_l
                best_url = best_url_l

            # print best URL and title found for this entry
            link_data = index +": " + best_title + " <" + best_url + ">"   

            print(link_data)    

            data = (index,people_count,photo_count,lat,lng,city,tagset)
               
            message = "landmark #%s has been photographed by %s different people" + \
                          "in our database, with %s photos, is near lat/long (%s, %s), is in a city called %s,"+ \
                          " and has the tags \"%s\"\n"
            outFile.write( message % data)
            outFileL.write(link_data+"\n")


    inFile.close()
    outFile.close()
    outFileL.close()

if __name__ == "__main__":
    main()
