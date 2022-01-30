# -*- coding: utf-8 -*-

from urllib.parse import parse_qsl
import sys

params = dict(parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
icon = params.get('icon')
id = params.get('id')
type = params.get('type')
name = params.get('name')
imdb = params.get('imdb')
tvdb = params.get('tvdb')
tmdb = params.get('tmdb')
query = params.get('query')
source = params.get('source')
content = params.get('content')

# xbmc.log("realizer debug: main params = %s" % params, xbmc.LOGWARNING) #DEBUG

if action is None:

    from resources.lib.indexers import navigator
    navigator.root()

elif action == 'authRealdebrid':
    from resources.lib.modules import control
    from resources.lib.api import debrid
    token = debrid.RealDebrid().auth()

elif action == 'list_downloads':
    from resources.lib.api import debrid
    # debrid.list_downloads()
    debrid.RealDebrid().list_downloads()

elif action == 'list_torrents':
    from resources.lib.api import debrid
    # debrid.list_torrents()
    debrid.RealDebrid().list_torrents()

elif action == 'play_torrent_item':
    from resources.lib.api import debrid
    # debrid.play_torrent_item(name, id)
    debrid.RealDebrid().play_torrent_item(name, id)

elif action == 'rdTorrentInfo':
    from resources.lib.api import debrid
    # debrid.torrent_info(id)
    debrid.RealDebrid().list_torrent_info(id)

elif action == 'rdDeleteItem':
    from resources.lib.modules import control
    from resources.lib.api import debrid
    debrid.RealDebrid().delete_list_item(id, type=type)
    control.refresh()

# elif action == 'refresh':
    # from resources.lib.modules import control
    # control.refresh()

# elif action == 'queueItem':
    # from resources.lib.modules import control
    # control.queueItem()

elif action == 'open_settings':
    from resources.lib.modules import control
    control.open_settings(query)

elif action == 'artwork':
    from resources.lib.modules import control
    control.artwork()

# elif action == 'traktManager':
    # from resources.lib.api import trakt
    # trakt.manager(name, imdb, tvdb, content)

# elif action == 'authTrakt':
    # from resources.lib.api import trakt
    # trakt.authTrakt()

# elif action == 'clearMeta':
    # import os
    # from resources.lib.modules import control
    # control.idle()
    # try:
        # os.remove(control.cacheFile)
    # except:
        # pass
    # try:
        # os.remove(control.metacacheFile)
    # except:
        # pass

    # control.info_dialog('Meta Cache Deleted', sound=True, icon='INFO')
