import re
import resources.lib.util as util


class Part():
    '''
    part holds part title and list of associated media.
    media list consists of host & video id tuples.
    these will be resolved later as I am unable to
    pass HostedMediaFile objects between function calls
    (they simply end up as type lists and need to be redone)
    '''

    def __init__(self, partnum, host, vid, text):
        self.partnum = partnum
        self.text = text
        self.media = [(host, vid)]
        #print 'Part initialized: {part}'.format(part=text)

    def add_media(self, host, vid):
        self.media.append((host, vid))


class Post():
    def __init__(self):
        self.parts = {}

    def __get_part_text(self, partnum):
        if partnum > 0:
            return 'Part {partnum}'.format(partnum=partnum)
        return 'Single link'

    #def __get_media_file(self, host, vid, text):
    #    '''
    #    resolve media file url
    #    '''
    #    import urlresolver
    #    return urlresolver.HostedMediaFile(
    #        host=host.server,
    #        media_id=vid,
    #        title=text)

    def __get_video_id(self, url):
        '''
        get video id from url
        '''
        v = url.find('v=')
        if (v > 0):
            vid = url[v+2:]
        return vid

    def __get_match_string(self, text):
        '''
        get match string for host mapping
        e.g. tube.php -> youtube
        '''
        m = re.compile('\/(\w+\.php)\?').findall(text)
        if m:
            match = m[0]
        return match

    def __get_part_number(self, text):
        '''
        get part number from text.
        Single link is Part 0
        '''
        p = re.compile('[pP]art\s*(\d+)').findall(text)
        if p:
            return int(p[0])
        return 0

    def add_link(self, posturl, urltext, matchstr):
        '''
        parse links from forum post
        add to local parts dictionary
        '''
        # parse text to get part number
        partnum = self.__get_part_number(urltext)

        # parse posturl to get matchstr
        match = self.__get_match_string(posturl)
        if match:
            #print 'Match string: {match}'.format(match=match)

            # get host from local match string dictionary
            host = matchstr.get(match)
            if host:
                #print 'Host found: {host}'.format(host=host.label)

                # get video id
                vid = self.__get_video_id(posturl)
                if vid:
                    #print 'Video ID: {vid}'.format(vid=vid)

                    text = self.__get_part_text(partnum)
                    #print 'part title: {text}'.format(text=text)

                    # add to parts dictionary
                    part = self.parts.get(partnum, None)
                    if part:
                        part.add_media(host, vid)
                    else:
                        self.parts[partnum] = Part(partnum, host, vid, text)
                else:
                    print '{addon}: No video id found for {url}'.format(
                        addon=util.addon_id, url=posturl)
            else:
                print '{addon}: No host found for {url}'.format(
                    addon=util.addon_id, url=posturl)
        else:
            print '{addon}: No match found for {url}'.format(
                addon=util.addon_id, url=posturl)
