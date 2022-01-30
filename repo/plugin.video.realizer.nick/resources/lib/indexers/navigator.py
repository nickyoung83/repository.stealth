# -*- coding: utf-8 -*-

'''
    realizer Add-on
'''

import sys

from resources.lib.modules import control
from resources.lib.api import debrid

def root():
    status = debrid.RealDebrid().account_info()
    if status is not True:
        message = ('  [B][COLOR red]!!![/COLOR][/B] This addon cannot be used without a RealDebrid account. [B][COLOR red]!!![/COLOR][/B] \n \n'
                   '                    Would you like to authorise RealDebrid?')
        ret = control.dialog.yesno('RD Auth Required', message, 'Exit', 'Authorise')
        if ret is True:
            control.execute('RunPlugin(plugin://plugin.video.realizer.nick/?action=authRealdebrid)')
            sys.exit()
        else:
            sys.exit()

    control.add_directory_item(50001, 'NULL', 'NULL')
    control.add_directory_item(50002, 'list_torrents', 'cloud.png')
    control.add_directory_item(50003, 'list_downloads', 'cloud.png')
    control.add_directory_item(40001, 'open_settings&query=0.0', 'settings.png', isFolder=False)
    control.end_directory()
