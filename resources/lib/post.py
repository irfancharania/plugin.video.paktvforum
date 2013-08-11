import re


class Part():
    media = []

    def add_media(self, media):
        self.media.append(media)

    def __init__(self, partnum, media, title):
        self.partnum = partnum
        self.title = title
        self.add_media(media)


class Post():
    parts = {}

    def get_part_title(self, partnum):
        if partnum > 0:
            return 'Part {partnum}'.format(partnum=partnum)
        return 'Single link'

    def get_media_file(self, host, vid, title):
        '''
        resolve media file url
        '''
        import urlresolver
        return urlresolver.HostedMediaFile(
            host=host,
            media_id=vid,
            title=title)

    def get_video_id(self, input):
        '''
        get video id from url
        '''
        v = input.find('v=')
        if (v > 0):
            vid = input[v+2:]
        return vid

    def get_match_string(self, input):
        '''
        get match string for host mapping
        e.g. tube.php -> youtube
        '''
        m = re.compile('\/(\w+\.php)\?').findall(input)
        if m:
            return m[0]
        return None

    def get_part_number(self, input):
        '''
        get part number from title.
        Single link is Part 0
        '''
        p = re.compile('[pP]art\s*(\d+)').findall(input)
        if p:
            return int(p[0])
        return 0

    def add_link(self, posturl, urltitle, matchstr):
        '''
        parse links from forum post
        '''
        # parse title to get part number
        partnum = self.get_part_number(urltitle)

        # parse posturl to get matchstr
        match = self.get_match_string(posturl)
        if match:

            # get host from local match string dictionary
            host = matchstr.get(match)
            if host:

                # get video id
                vid = self.get_video_id(posturl)
                if vid:
                    title = self.get_part_title(partnum)
                    # resolve media host file
                    media = self.get_media_file(
                        host,
                        vid,
                        title)

                    # add to parts dictionary
                    part = self.parts.get(partnum, None)
                    if part:
                        part.add_media(media)
                    else:
                        self.parts[partnum] = Part(partnum, media, title)
