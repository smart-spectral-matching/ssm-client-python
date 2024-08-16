import scidatalib.io
from scidatalib.scidata import SciData

_DEFAULT_UID = "scidata:jsonld"


def read_jcamp(filename: str) -> dict:
    """
    Reader for JCAMP-DX files to SciData JSON-LD dictionary
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
    JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename to read from for JCAMP-DX files
    Returns:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    scidata_obj = scidatalib.io.read(filename, ioformat="jcamp")
    return scidata_obj.output


def write_jcamp(filename: str, scidata_dict: dict):
    """
    Writer for SciData JSON-LD dictionary to JCAMP-DX files.
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
    JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename for JCAMP-DX file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    uid = scidata_dict.get("@graph").get("uid", _DEFAULT_UID)
    scidata = SciData(uid)
    scidata.meta = scidata_dict
    if "toc" not in scidata.meta["@graph"]:
        scidata.meta["@graph"]["toc"] = list()
    scidatalib.io.write(filename, scidata, ioformat="jcamp")
