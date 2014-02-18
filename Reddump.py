'''
Created on Feb 13, 2014

@author: Abhimanyu

Reddump v 1.2 : Downloads pictures and imgur albums from subreddits with just one double-click.


'''

import re
import os
import urllib2
import json


class TerminateError(Exception):
    pass

pattern_album = re.compile("(?:i|w{3})?\.?imgur.com/a/[a-zA-Z0-9#]+$")
pattern_imagelink = re.compile("(?:i|w{3})?\.?imgur.com/[a-zA-Z0-9]+$")
pattern_image = re.compile("\.\w+$")

image_extensions = ["jpg", "jpeg", "png", "bmp", "gif"]
valid_filters = ["day", "hour", "week", "month", "year", "all"]

pattern_album_scrapper = re.compile('<meta property="og:image" content="http://((?:i|w{3})?\.?imgur.com/\w+\.\w+)" />')

def direct_image_downloader(i, data, target):    
    target_folder = os.path.join(target,"%d_"%i + data["author"] )  
    if not os.path.exists(target_folder):  
        os.mkdir(target_folder)        
    extention = data["url"].split(".")[-1]
    final_target = os.path.join(target_folder, data["author"])+".%s"%extention
    if not os.path.exists(final_target):
        img = urllib2.urlopen(data["url"])
        t_img = open(final_target, "wb")
        t_img.write(img.read())

    
def imgur_album_downloader(i, data, target):
    target_folder = os.path.join(target,"%d_"%i + data["author"])
    urldump = urllib2.urlopen(data["url"]).read()
    photo_tuples=pattern_album_scrapper.findall(urldump)
    photo_links = ["".join(element) for element in photo_tuples]
    if not os.path.exists(target_folder):  
        os.mkdir(target_folder) 
    i = 0
    for url in photo_links: 
        i += 1 
        extention = url.split(".")[-1]
        final_target = os.path.join(target_folder, data["author"] + "_%d"%i )+".%s"%extention   
        if not os.path.exists(final_target):         
            img = urllib2.urlopen("http://" + url)
            t_img = open(final_target, "wb")
            t_img.write(img.read())
        
def imgur_imagelink_downloader(i, data, target):
    target_folder = os.path.join(target,"%d_"%i + data["author"])
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)    
    print data["id"]
    pattern = re.compile('i\.imgur\.com/' + '%s'%data["url"].split("/")[-1] + '.\w+')    
    coverdump = urllib2.urlopen(data["url"])    
    imageurl = pattern.search(coverdump.read()).group()  
    extention = imageurl.split(".")[-1]
    final_target = os.path.join(target_folder, data["author"])+".%s"%extention
    if not os.path.exists(final_target): 
        img = urllib2.urlopen("http://"+ imageurl)
        t_img = open(final_target, "wb")
        t_img.write(img.read())

print "Enter subreddit name: "
subreddit = raw_input()
check = urllib2.urlopen('http://www.reddit.com/r/' + subreddit)
if "there doesn't seem to be anything here" in check.read():
    raise TerminateError("No such subreddit exists.")

target = os.path.join(os.getcwd(),subreddit + "_dump")
if not os.path.exists(target):
    os.mkdir(target)

print "Enter filter (hot, new, top) : "
sort_filter = raw_input()
print "Enter the number of posts you want to download: "
n = raw_input()

try:
    if sort_filter == "hot":
        response = urllib2.urlopen('http://www.reddit.com/r/' + subreddit + '/hot/.json?limit=' + n)
    elif sort_filter == "new":
        response = urllib2.urlopen('http://www.reddit.com/r/' + subreddit + '/new/.json?limit=' + n)
    elif sort_filter == "top":
        print "Top posts by? (hour, day, week, month, year, all) : " 
        top_filter = raw_input()
        if top_filter in valid_filters:        
            response = urllib2.urlopen('http://www.reddit.com/r/+' + subreddit + '/top/.json?sort=top&t=' + top_filter + '&limit=' + n)
        else:
            raise TerminateError("Invalid sort filter, please try again.")
    else: 
        raise TerminateError("Invalid filter, please try again")
    data = json.load(response)
    
    i = 1
    print ">>Initiating dump procedure ..."
    for element in  data["data"]["children"]:
        flag = False
           
        print ">>>>Now downloading " + element["data"]["author"] + "'s post..." 
        if pattern_image.search(element["data"]["url"]):
            if element["data"]["url"].split(".")[-1] in image_extensions:
                direct_image_downloader(i, element["data"], target)
                flag = True
        elif pattern_album.search(element["data"]["url"]):             
            imgur_album_downloader(i, element["data"], target)  
            flag = True      
        elif pattern_imagelink.search(element["data"]["url"]):            
            imgur_imagelink_downloader(i, element["data"], target)
            flag = True
        if flag: 
            print "done..."
            i+=1
        else: 
            print "User's post is not supported for download."
        
except urllib2.HTTPError: 
    print "Network error. Link could not be loaded. Please make sure the subreddit is not private."
except TerminateError:
    print TerminateError.message
    