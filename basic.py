"""Provide a set of basic functions"""
import sys

def perror(text, exit_code=1, **kwargs):
    """ Prints to standard error. If status is non-zero exits """

    print("ERROR: {}".format(text), file=sys.stderr, **kwargs)
    if exit_code != 0:
        sys.exit(exit_code)


def assure_startswith(word, prefix):
    """Assure that a string starts with a given prefix"""
    if not word.startswith(prefix):
        word = prefix + word
    return word
