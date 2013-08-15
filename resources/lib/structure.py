import resources.lib.util as util


class Category():
    def __init__(self, label, channels):
        self.label = label
        self.channels = channels


class Channel():
    def __init__(self, id, label, thumb=''):
        self.id = id
        self.label = label
        self.thumb = thumb