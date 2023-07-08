import scidatalib.io
from scidatalib.scidata import SciData

_DEFAULT_UID = "scidata:jsonld"


def read_rruff(filename: str) -> dict:
    """
    Reader for RRUFF database files to SciData JSON-LD dictionary
    RRUFF file format is a modified version of JCAMP, so re-use jcamp module

    Args:
        filename (str): Filename to read from for RRUFF files

    Returns:
        scidata_dict (dict): SciData JSON-LD dictionary read from RRUFF file
    """
    scidata_obj = scidatalib.io.read(filename, ioformat="rruff")
    return scidata_obj.output


def write_rruff(filename: str, scidata_dict: dict) -> dict:
    """
    Writer SciData JSON-LD dictionary to RRUFF database files
    RRUFF file format is a modified version of JCAMP, so re-uses jcamp module

    Args:
        filename (str): Filename for RRUFF file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    uid = scidata_dict.get("@graph").get("uid", _DEFAULT_UID)
    scidata = SciData(uid)
    scidata.meta = scidata_dict
    if "toc" not in scidata.meta["@graph"]:
        scidata.meta["@graph"]["toc"] = list()
    scidatalib.io.write(filename, scidata, ioformat="rruff")
