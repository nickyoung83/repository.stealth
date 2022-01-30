# -*- coding: utf-8 -*-

'''
    realizer Add-on
'''

import os
import sys
from datetime import datetime

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

add_item = xbmcplugin.addDirectoryItem
addon_info = xbmcaddon.Addon().getAddonInfo
addon_id = addon_info('id')
addon_fanart = addon_info('fanart')
addon_icon = addon_info('icon')
art_folder = xbmcvfs.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/artwork/', ''))
content = xbmcplugin.setContent
dialog = xbmcgui.Dialog()
directory = xbmcplugin.endOfDirectory
execute = xbmc.executebuiltin
item = xbmcgui.ListItem
lang = xbmcaddon.Addon().getLocalizedString
progressDialog = xbmcgui.DialogProgress()
resolve = xbmcplugin.setResolvedUrl
setting = xbmcaddon.Addon().getSetting
timeNow = datetime.now().strftime('%Y%m%d%H%M')

data_path = xbmcvfs.translatePath(addon_info('profile'))
rd_auth_file = os.path.join(data_path, 'rdauth.json')


def info_dialog(message, heading=addon_info('name'), icon='', time=3000, sound=False):
    if icon == '': icon = addon_icon
    elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
    elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
    dialog.notification(message, heading, icon, time, sound)


def open_settings(query=None, id=addon_info('id')):
    try:
        execute('Addon.OpenSettings(%s)' % id)

        if query is None:
            raise Exception()

        c, f = query.split('.')
        execute('SetFocus(%i)' % (int(c) - 100))
        execute('SetFocus(%i)' % (int(f) - 80))
    except:
        pass


def refresh():
    return execute('Container.Refresh')


def add_directory_item(name, query, thumb, context=None, isFolder=True):
    try: name = lang(name)
    except: pass
    url = '%s?action=%s' % (sysaddon, query)
    cm = []
    if context is not None:
        cm.append((lang(context[0]), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
    thumb = art_folder + thumb
    # xbmc.log("realizer debug: control.add_directory_item sysaddon = %s" % syshandle, xbmc.LOGWARNING) #DEBUG
    listitem = item(label=name)
    listitem.addContextMenuItems(cm)
    listitem.setArt({'icon': thumb, 'thumb': thumb})
    if addon_fanart is not None: listitem.setProperty('Fanart_Image', addon_fanart)
    add_item(handle=syshandle, url=url, listitem=listitem, isFolder=isFolder)


def end_directory():
    content(syshandle, 'addons')
    directory(syshandle, cacheToDisc=True)
