import abc
import re


class BaseForum(object):
    __metaclass__ = abc.ABCMeta

    short_name = 'base'
    long_name = 'Base Forum'
    local_thumb = ''
    base_url = ''

    sub_id_regex = '(?:\?f=|\/f|\?t=)(\d+)'

###############################################

    def get_frame_menu(self):
        return

    def browse_frame(self, frameid, url):
        return

    def get_sub_id(self, url):
        ''' get sub forum/thread id'''
        pk = None
        if url:
            t = re.compile(self.sub_id_regex).findall(url)
            if t:
                pk = t[0]
        return pk

    def get_parents(self, linklist):
        '''identify forum sections/subsections'''
        newlist = []

        for l in linklist:
            if (l.get('id')):
                newlist.append(l)
            else:
                parent = newlist[-1]
                parent['data-has-children'] = True

        return newlist

    # For some reason the fetched request
    # doesn't contain new icons for posts.
    # Also, it doesn't tell me that these are newer
    # from the last time I opened this addon
    # maybe I need to be logged in for that...
    def has_new_episodes(self, listitem):
        if ((listitem.img['src'].find('new') > 0) or
                (listitem.a.img)):
            return True
        return False

###############################################

    @abc.abstractmethod
    def get_category_menu(self):
        return

    @abc.abstractmethod
    def get_channel_menu(self):
        return

    @abc.abstractmethod
    def get_show_menu(self):
        return

    @abc.abstractmethod
    def get_episode_menu(self):
        return

    @abc.abstractmethod
    def get_episode_data(self):
        return
