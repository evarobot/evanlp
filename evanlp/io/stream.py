import pickle
from evanlp.config import ConfigIO


def save(data, fname):
    """ Save data to specific path.

    Parameters
    ----------
    fname : str, file name, including data path.

    Returns
    -------
    bool.

    """
    if ConfigIO.type == "FILE":
        with open(fname, "wb") as f:
            pickle.dump(data, f)
    else:
        assert False


def load(fname):
    """ Load model from specific path.

    Parameters
    ----------
    fname : str, file name, including data path.

    Returns
    -------
    bool.

    """
    if ConfigIO.type == "FILE":
        with open(fname, "rb") as fobj:
            return pickle.load(fobj)
    else:
        assert False
