# -*- coding: utf-8 -*-

# Module: default
# Author: JonFlix Mgmt 
# Created on: 28.10.2016
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import json
import re
import os
import datetime
import urllib
import urllib2
from urllib2 import Request, urlopen, URLError
import HTMLParser

from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import xbmcaddon

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

my_addon = xbmcaddon.Addon()
#my_addon.setSetting('access_key', '')

def fetch_data(path):

   url = 'http://france.jonstones.com/movies/kodi.php?'+path
 
   access_key = my_addon.getSetting('access_key')
   data=''
   try:
       response = urllib2.urlopen(url)
       # everything is fine
       data = json.loads(response.read())
   except URLError as e:
       if hasattr(e, 'reason'):
           xbmcgui.Dialog().ok('JonFlix', url, e.reason)
       elif hasattr(e, 'code'):
           xbmcgui.Dialog().ok('JonFlix', url, e.code)
   else:
      return data


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Get video categories
    VIDEOS=fetch_data('category=all')
    if not VIDEOS:
       return
    categories = VIDEOS.keys() 
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
    #    list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
    #                      'poster': VIDEOS[category][0]['thumb'],
    #                      'fanart': VIDEOS[category][0]['thumb']})

        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'plot': VIDEOS[category] })
        list_item.setLabel2(VIDEOS[category]) ;

        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = '{0}?action=listing&category={1}'.format(_url, category)

        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True

        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))

    # Add our listing to Kodi.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: str
    """
    # Get the list of videos in the category.
    VIDEOS=fetch_data('category='+category)
    if not VIDEOS:
       return
    videos=VIDEOS[category]
    # Create a list for our items.
    listing = []
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])

        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['name'], 'imdbnumber':video['imdbCode'],'plot':video['description'], 'studio':video['production'] })
        list_item.setSubtitles(video['srtfiles']) ;

        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Errors ?! list_item.setUniqueIDs({ 'imdb': video['imdbCode'] })

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')

        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/vids/crab.mp4
        #print video['video'].encode('utf8') ;
        url = '{0}?action=play&video={1}'.format(_url, video['video'].encode('utf8')) ;

        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    #xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video( params['video'] )
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
