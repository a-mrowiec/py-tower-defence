"""
Phase module
"""


class Phase:
    """
    Base class for phase
    """

    def initialise(self, **kwargs):
        """
        Initialise phase
        :param kwargs:
        :return:
        """
        pass

    def update(self, dt):
        """
        Update phase
        :param dt:
        :return:
        """
        pass

    def draw(self, surface):
        """
        Draw any elements to the screen
        :param surface:
        :return:
        """
        pass

    def on_destroy(self):
        """
        Called when phase is destroyed
        :return:
        """
        pass
