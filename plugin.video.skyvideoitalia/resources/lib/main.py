# -*- coding: utf-8 -*-
from resources.lib.skyitalia import SkyItalia
from resources.lib import addonutils


class SkyVideoItalia(object):
    LOCAL_MAP = {
        'media.not.found': 31003,
        'live.not.found': 31004,
    }

    def __init__(self):
        self.skyit = SkyItalia()

    def addItems(self, items):
        video = False
        for item in items:
            if item.get('videoInfo'):
                video = any([item['videoInfo'].get('mediatype') == 'video', video])
            addonutils.addListItem(
                label=item.get('label'),
                label2=item.get('label2'),
                params=item.get('params'),
                videoInfo=item.get('videoInfo'),
                arts=item.get('arts'),
                isFolder=False if item.get('isPlayable') else True,
            )
        if video:
            addonutils.setContent('videos')

    def main(self):
        params = addonutils.getParams()
        self.skyit._log('main, Params = %s' % str(params))
        if 'asset_id' in params:
            # PLAY VIDEO
            url = self.skyit.getVideo(params['asset_id'])
            if url:
                self.skyit._log('main, Media URL = %s' % url, 1)
                addonutils.setResolvedUrl(url)
            else:
                self.skyit._log('main, Media URL not found, asset_id = %s' % params['asset_id'], 3)
                addonutils.notify(addonutils.LANGUAGE(self.LOCAL_MAP['media.not.found']))
                addonutils.setResolvedUrl(solved=False)

        elif 'playlist_id' in params:
            # PLAYLIST CONTENT
            playlist_content = self.skyit.getPlaylistContent(params['playlist_id'])
            self.addItems(playlist_content)

        elif all(x in params for x in ['playlist', 'section', 'subsection']):
            # PLAYLIST SECTION
            playlist = self.skyit.getPlaylists(
                params['section'], params['subsection'])
            self.addItems(playlist)

        elif all(x in params for x in ['title', 'section', 'subsection']):
            # SUBSECTION MENU
            subsection_content = self.skyit.getSubSection(
                params['section'], params['subsection'], params['title'])
            self.addItems(subsection_content)

        elif 'section' in params:
            # SECTION MENU
            section_content = self.skyit.getSection(params['section'])
            self.addItems(section_content)

        elif 'livestream_id' in params:
            # LIVESTREAM PLAY SECTION
            live_content = self.skyit.getLiveStream(params['livestream_id'])
            if live_content:
                item = addonutils.createListItem(
                    path=live_content.get('path'),
                    label=live_content.get('label'),
                    videoInfo=live_content.get('videoInfo'),
                    arts=live_content.get('arts'),
                    isFolder=False
                )
                addonutils.setResolvedUrl(item=item)
            else:
                self.skyit._log('main, Livestream URL not found, id = %s' % params['livestream_id'], 3)
                addonutils.notify(addonutils.LANGUAGE(self.LOCAL_MAP['live.not.found']))
                addonutils.setResolvedUrl(solved=False)

        elif 'live' in params:
            # LIVESTREAM SECTION
            live_content = self.skyit.getLiveStreams()
            self.addItems(live_content)

        else:
            # MAIN MENU
            menu = self.skyit.getMainMenu()
            self.addItems(menu)

        self.skyit = None
        addonutils.endScript(exit=False)