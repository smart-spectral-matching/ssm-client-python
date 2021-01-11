import json


def read_scidata_jsonld(filename):
    """
    Reader for SciData JSON-LD files to SciData JSON-LD dictionary
        SciData URL: http://stuchalk.github.io/scidata/

    Args:
        filename (str): Filename to read from for SciData JSON-LD
    Return:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    with open(filename, 'r') as fileobj:
        scidata_dict = json.load(fileobj)
    return scidata_dict


def write_scidata_jsonld(filename, scidata_dict):
    """
    Writer for SciData JSON-LD dictionary to SciData JSON-LD files
        SciData URL: http://stuchalk.github.io/scidata/

    Args:
        filename (str): Filename for SciData JSON-LD
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    with open(filename, 'w') as fileobj:
        json.dump(scidata_dict, fileobj, indent=2)
