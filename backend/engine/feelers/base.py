from ..yielders import base

class Feeler(base.BaseYielder):
    """Implements IFeelYielder.

    Provides a formula for calculating a feeling and a generate method for yielding the feeling

    NOTE: for less (or better) coupling the feeler should *use* a yielder, instead of *extending* from a yielder, but this way you create just one class for each type of feeling that you want to be able to calculate """

    def calculate(power):
        """Transform power into feeling.

        power -- np.array of shape (n_chs, n_freqs)
        """

        # REVIEW: use a dict to transform to JSON? depends on formatters to yield

        feeling1 = 0
        feeling2 = 1

        return [feeling1, feeling2] # could be more than 2

    # DEPRECATED
    # def generate(self, timestamp, feeling):
    #     """Yields the feeling
    #
    #     feeling -- same type that the return type of calculate()"""
    #     yield "data: {}, {}, {}\n\n".format(timestamp, *feeling)
