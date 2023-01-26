class Notebook:
    """Container class for all lists owned by the user

    :param lists: Initial list of :class:`List` instances
    :type lists: list
    """

    def __init__(self, lists=None):
        self.lists = [] if lists is None else lists
