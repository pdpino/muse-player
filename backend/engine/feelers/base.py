from ..yielders import base

class BaseFeeler(base.BaseYielder):
    """Implements IFeelYielder.

    Provides a formula for calculating a feeling and a generate method for yielding the feeling

    NOTE: for less (or better) coupling the feeler should *use* a yielder, instead of *extending* from a yielder, but this way you create just one class for each type of feeling that you want to be able to calculate"""

    def calculate(power):
        """Transform power into feeling. (Abstract)

        power -- np.array of shape (n_chs, n_freqs)

        Override this method to return the raw feeling calculated from power array
        """

        feeling1 = 0
        feeling2 = 1

        return [feeling1, feeling2] # could be more than 2
