# -*- coding: utf-8 -*-
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import xbmc

import requests

from resources.lib.modules import cleantitle, clipboard, control, utils

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])

USER_AGENT = 'RealDebrid Addon for Kodi'
# data = {}
# params = {}
VALID_EXT = ['mkv', 'avi', 'mp4', 'divx', 'mpeg', 'mov', 'wmv', 'avc', 'mk3d', 'xvid', 'mpg', 'flv', 'aac', 'asf', 'm4a', 'm4v', 'mka', 'ogg', 'oga', 'ogv', 'ogx', '3gp', 'vivo', 'pva', 'flc']
REQUEST_TIMEOUT = 30
# EXT_BLACKLIST = ['rar.html', '.php', '.txt', '.iso', '.zip', '.rar', '.jpeg', '.img', '.jpg', '.RAR', '.ZIP', '.png', '.sub', '.srt']

# #############################################################################
# ################################ REAL DEBRID ################################
# #############################################################################


class RealDebrid:
    def __init__(self):
        self.rd_api = 'https://api.real-debrid.com/rest/1.0'
        self.rd_apiname = 'Realizer'
        self.rd_clientid = 'X245A4XAIBGVM'
        self.rd_oauth = 'https://api.real-debrid.com/oauth/v2/device/code?client_id=%s&new_credentials=yes' % self.rd_clientid
        self.rd_token_auth = 'https://api.real-debrid.com/oauth/v2/token'
        self.rd_credentials_auth = 'https://api.real-debrid.com/oauth/v2/device/credentials?client_id=%s&code=%s'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'
        # self.transfers = []
        # self.torrents = []


    def save_json(self, client_id=None, client_secret=None, token=None, refresh_token=None):
        if not os.path.exists(control.data_path): os.makedirs(control.data_path)
        if token is not None: data = {'client_id':client_id, 'client_secret':client_secret, 'token':token, 'refresh_token':refresh_token, 'added':control.timeNow}
        else: data = {'client_id':client_id, 'client_secret':client_secret, 'token':'0', 'refresh_token': '0', 'added':control.timeNow}
        with open(control.rd_auth_file, 'w') as outfile: json.dump(data, outfile, indent=2)


    def auth(self):
        result = requests.get(self.rd_oauth, timeout=REQUEST_TIMEOUT).json()
        expires_in = int(result['expires_in'])
        device_code = result['device_code']
        interval = int(result['interval'])
        message = ('1) Visit:[B][COLOR skyblue] {url} [/COLOR][/B] \n'
                   '2) Input Code:[B][COLOR skyblue] {code} [/COLOR][/B] \n \n'
                   'Note: Your code has been copied to the clipboard'
                  ).format(url=result['verification_url'], code=result['user_code'])
        # message = '\n'.join([verification_url, user_code, line3])

        try: clipboard.Clipboard.copy(result['user_code'])
        except: pass

        control.progressDialog.create('Real Debrid', message)

        for i in range(0, expires_in):
            try:
                if control.progressDialog.iscanceled(): break
                time.sleep(1)
                if not float(i) % interval == 0: raise Exception()

                percent = int(float((i * 100) / expires_in))
                control.progressDialog.update(percent, message)

                credentials = self.get_credentials(device_code)
                if "client_secret" not in str(credentials): raise Exception()

                client_secret = credentials["client_secret"]
                client_id = credentials["client_id"]
                r = self.get_auth(self.rd_token_auth , client_id, client_secret, device_code)

                if "access_token" in str(r):
                    token = r["access_token"]
                    refresh_token = r["refresh_token"]
                    self.save_json(token=token, client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
                    control.info_dialog("RealDebrid Authorised")

                    try: control.progressDialog.close()
                    except: pass

                    return token
                    # break
            except: pass
        try: control.progressDialog.close()
        except: pass


    def get_credentials(self, device_code):
        url = self.rd_credentials_auth % (self.rd_clientid, device_code)
        result = requests.get(url, timeout=5).json()
        return result


    def get_auth(self, url, client_id, client_secret, device_code):
        headers = {"User-Agent": self.user_agent}
        data = {"client_id": client_id, "client_secret": client_secret, "code": device_code, "grant_type": 'http://oauth.net/grant_type/device/1.0'}
        result = requests.post(url, data=data, headers=headers, timeout=REQUEST_TIMEOUT).json()
        return result


    def refresh_rd_token(self, refresh_token, client_secret, client_id):
        headers = {'User-Agent': self.user_agent}
        data = {'client_id': client_id, 'client_secret': client_secret, 'code': refresh_token, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
        result = requests.post(self.rd_token_auth, data=data, headers=headers, timeout=REQUEST_TIMEOUT).json()
        if 'access_token' in str(result):
            # expires_in = result['expires_in']
            token = result['access_token']
            refresh_token = result['refresh_token']
            # print ("REFRESHING TOKEN", token)
            self.save_json(token=token, client_secret=client_secret, client_id=client_id, refresh_token=refresh_token)
            return token


    def get_token(self, refresh=False):
        token = '0'
        if not os.path.exists(control.rd_auth_file):
            self.save_json()
            return
        if refresh:
            try:
                with open(control.rd_auth_file) as json_file:
                    try:
                        data = json.load(json_file)
                        refresh_token = data['refresh_token']
                        client_id = data['client_id']
                        client_secret = data['client_secret']
                        token = self.refresh_rd_token(refresh_token, client_secret, client_id)
                    except: token = None
                if token == '' or token is None or token == '0': control.info_dialog('Real Debrid is not Authorised','Please authorise in the settings')
            except: pass
        else:
            try:
                with open(control.rd_auth_file) as json_file:
                    try:
                        data = json.load(json_file)
                        token = data['token']
                    except: token = None
                if token == '' or token is None or token == '0': control.info_dialog('Real Debrid is not Authorised','Please authorise in the settings')
            except: pass
        if token == '' or token is None: token = '0'
        return token


    def account_info(self):
        token = '0'
        if not os.path.exists(control.rd_auth_file): self.save_json()
        try:
            with open(control.rd_auth_file) as json_file:
                try:
                    data = json.load(json_file)
                    token = data['token']
                except:
                    token = None
        except: pass
        if token == '' or token is None or token == '0': return False
        return True


    def rd_request(self, url, method='get', data=None, params=None, refresh=False):
        token = self.get_token(refresh=refresh)
        headers = {'Authorization': 'Bearer %s' % token, 'client_id': self.rd_clientid, 'User-Agent': self.user_agent}
        try:
            if method == 'get': result = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            elif method == 'post': result = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
            elif method == 'delete': result = requests.delete(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
        # except requests.Timeout as err: control.info_dialog('REALDEBRID TIMED OUT', time=3)
        except requests.Timeout: control.info_dialog('REALDEBRID TIMED OUT')
        if result.status_code == 401:
            if not refresh:
                result = self.rd_request(url, method=method, data=data, refresh=True)
                return result
            # else: return result
        else:
            return result


    def get_downloads(self):
        url = self.rd_api + '/downloads'
        params = {'limit': 100}
        result = self.rd_request(url, method='get', params=params).json()
        return result


    def list_downloads(self):
        r = self.get_downloads()

        try:
            for result in r:
                try:
                    cm = []
                    icon = result['host_icon']
                    name = result['filename']
                    name = self.normalize(name)
                    id = result['id']
                    # link = result['link']
                    ext = name.split('.')[-1]

                    # isPlayable = ext in VALID_EXT
                    # isPlayable = not isPlayable

                    if ext.lower() not in VALID_EXT: raise Exception()
                    label = ext.upper() + " | " + name

                    item = control.item(label=label)
                    item.setArt({'icon': icon, 'thumb': icon})
                    item.setProperty('Fanart_Image', control.addon_fanart)
                    infolabel = {"Title": name}
                    item.setInfo(type='Video', infoLabels = infolabel)
                    item.setProperty('IsPlayable', 'true')
                    url = result['download']
                    cm.append(('Delete Download Item', 'RunPlugin(%s?action=rdDeleteItem&id=%s&type=downloads)' % (sysaddon, id)))
                    # if control.setting('downloads') == 'true': cm.append(('Download from Cloud', 'RunPlugin(%s?action=download&name=%s&url=%s&id=%s)' % (sysaddon, name, url, id)))
                    item.addContextMenuItems(cm)
                    control.add_item(handle=syshandle, url=url, listitem=item, isFolder=False)
                except: pass
        except: pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)


    def get_torrents(self):
        url = self.rd_api + '/torrents'
        params = {'limit': 100}
        result = self.rd_request(url, method='get', params=params).json()
        return result


    def list_torrents(self):
        r = self.get_torrents()

        if control.setting('sort.torrents') == 'true':
            try: r = sorted(r, key=lambda k: utils.title_key(k['filename']))
            except: pass

        for item in r:
            cm = []
            status = item['status']
            id = item['id']
            name = item['filename']
            label = status.upper() + " | " + name
            item = control.item(label=label)
            item.setArt({'icon': control.addon_icon})
            item.setProperty('Fanart_Image', control.addon_fanart)
            # infolabel = {"Title": label}
            cm.append(('Delete Torrent Item', 'RunPlugin(%s?action=rdDeleteItem&id=%s&type=torrents)' % (sysaddon, id)))
            url = '%s?action=%s&id=%s' % (sysaddon, 'rdTorrentInfo', id)
            item.addContextMenuItems(cm)
            control.add_item(handle=syshandle, url=url, listitem=item, isFolder=True)

        control.directory(syshandle, cacheToDisc=True)


    def get_torrent_info(self, id):
        url = self.rd_api + '/torrents/info/' + id
        result = self.rd_request(url, method='get').json()
        return result


    def list_torrent_info(self, id):
        r = self.get_torrent_info(id)

        # links = r['links']
        files = r['files']
        try: files = sorted(files, key=lambda k: utils.title_key(k['path']))
        except: pass
        # count = 0
        for x in files:
            try:
                original_filename = x['path']
                if original_filename.startswith('/'):
                    name = original_filename.split('/')[-1]

                ext = name.split('.')[-1]
                # isPlayable = ext in VALID_EXT
                if ext.lower() not in VALID_EXT: raise Exception()
                label = ext.upper() + " | " + name

                item = control.item(label=label)
                item.setArt({'icon': control.addon_icon})
                item.setProperty('Fanart_Image', control.addon_fanart)
                infolabel = {"Title": name}
                item.setInfo(type='Video', infoLabels = infolabel)
                item.setProperty('IsPlayable', 'true')
                systitle = urllib.parse.quote_plus(name)
                url = '%s?action=%s&name=%s&id=%s' % (sysaddon, 'play_torrent_item', systitle, id)
                control.add_item(handle=syshandle, url=url, listitem=item, isFolder=False)
            except: pass

        control.content(syshandle, 'movies')
        control.directory(syshandle, cacheToDisc=True)


    def play_torrent_item(self, name, id):
        torrent_in_download = []
        try : name = name.split('/')[-1]
        except: pass
        # except: name = name
        try:
            downloads = self.get_downloads()
            torrent_in_download = [i for i in downloads if i['filename'].lower() == name.lower()][0]
        except: pass

        if len(torrent_in_download) > 0:
            item = control.item(label=name)
            item.setArt({'icon': control.addon_icon})
            item.setProperty('Fanart_Image', control.addon_fanart)
            infolabel = {"Title": name}
            item.setInfo(type='Video', infoLabels = infolabel)
            item.setProperty('IsPlayable', 'true')
            item = control.item(path= torrent_in_download['download'])
            control.resolve(int(sys.argv[1]), True, item)
        else:
            new_torrent = []

            result = self.torrent_item_to_download(name, id)
            if result is not None: new_torrent.append(result)

            time.sleep(1)
            torrent_item = new_torrent[0]

            if len(torrent_item) > 0:
                control.info_dialog('Playing Torrent Item', torrent_item['filename'])
                item = control.item(label=name)
                item.setArt({'icon': control.addon_icon})
                item.setProperty('Fanart_Image', control.addon_fanart)
                infolabel = {"Title": name}
                item.setInfo(type='Video', infoLabels = infolabel)
                item.setProperty('IsPlayable', 'true')
                item = control.item(path= torrent_item['download'])
                control.resolve(int(sys.argv[1]), True, item)


    def torrent_item_to_download(self, name, id):
        r = self.get_torrent_info(id)
        links = r['links']
        files = r['files']
        new_torrent = []

        files = [i for i in files if not (i['selected'] == 0)]

        count = 0
        for x in files:
            filename = x['path']
            try: filename = filename.split('/')[-1]
            except: pass

            original_filename = name
            try: original_filename = original_filename.split('/')[-1]
            except: pass

            playlink = links[count]
            count += 1

            if cleantitle.get(filename) == cleantitle.get(original_filename):
                new_torrent.append(self.resolve(playlink, full=True))
                for y in new_torrent:
                    return y


    def delete_list_item(self, id, type):
        # DOWNLOADS
        if type == 'downloads':
            d = '/downloads/delete/%s' % id
            delete = self.rd_api + d
            self.rd_request(delete, method='delete')

        # TORRENTS
        if type == 'torrents':
            d = '/torrents/delete/%s' % id
            delete = self.rd_api + d
            self.rd_request(delete, method='delete')


    def resolve(self, url, full=False):
        if url.startswith("//"): url = 'http:' + url
        try:
            post = {'link': url}
            url = self.rd_api + '/unrestrict/link'
            result = self.rd_request(url, method='post', data=post).json()
            if 'error_code' in str(result): return None
            if full is True: return result
            try: url = result['download']
            except: return None
            if url.startswith('//'): url = 'http:' + url
            return url
        except:
            return None


    def normalize(self, txt):
        txt = re.sub(r'[^\x00-\x7f]',r'', txt)
        return txt
