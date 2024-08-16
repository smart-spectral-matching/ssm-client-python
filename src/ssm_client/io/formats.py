from importlib import import_module


_MODULE_BASE = "ssm_client.io."


class UnknownFileTypeError(Exception):
    pass


ioformats = {
    "jcamp": "jcamp",
    "rruff": "rruff",
    "scidata-jsonld": "scidata_jsonld",
    "ssm-json": "ssm_json",
}


def _get_ioformat(name):
    if name not in ioformats:
        raise UnknownFileTypeError(name)
    module = _MODULE_BASE + ioformats[name]
    fmt = import_module(module)
    return fmt


def _readfunc(module, name):
    return getattr(module, "read_" + name)


def _writefunc(module, name):
    return getattr(module, "write_" + name)


def read(filename, ioformat=None, **kwargs) -> dict:
    """
    Read SciData dict from file format
    """
    module = _get_ioformat(ioformat)
    function = _readfunc(module, ioformats.get(ioformat))
    return function(filename, **kwargs)


def write(filename, scidata_dict, ioformat=None, **kwargs) -> None:
    """
    Write SciData dict to file format
    """
    module = _get_ioformat(ioformat)
    function = _writefunc(module, ioformats.get(ioformat))
    return function(filename, scidata_dict, **kwargs)
