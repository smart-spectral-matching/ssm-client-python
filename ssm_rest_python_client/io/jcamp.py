from .scidata import get_scidata_base


def read_jcamp(filename):
    """
    Reader for JCAMP files to SciData JSON-LD dictionary
        JCAMP is for Joint Committee on Atomic and Molecular Physical Data.
        JCAMP URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename to read from for JCAMP files
    Return:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    scidata_dict = get_scidata_base()
    return scidata_dict


def write_jcamp(filename, scidata_dict):
    """
    Writer for SciData JSON-LD dictionary to JCAMP files.
        JCAMP is for Joint Committee on Atomic and Molecular Physical Data.
        JCAMP URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename for JCAMP file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    pass
