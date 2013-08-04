import abc

class BaseForum(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def browse_channels(self):
        return

    @abc.abstractmethod
    def browse_shows(self):
        return

    @abc.abstractmethod
    def browse_episodes(self):
        return

    @abc.abstractmethod
    def get_episode_data(self):
        return

    @abc.abstractmethod
    def play_video(self):
        return