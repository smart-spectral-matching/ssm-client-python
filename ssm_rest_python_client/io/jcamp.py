import numpy as np
import re

from .scidata import get_scidata_base

_DATA_FORMAT_XYXY = '(XY..XY)'
_DATA_FORMAT_XYYY = '(X++(Y..Y))'
_DATA_FORMATS = (_DATA_FORMAT_XYXY, _DATA_FORMAT_XYYY)
_DATA_TYPE_KEY = "data type"
_DATA_XY_TYPE_KEY = "xy data type"
_DATA_XY_TYPES = ('xydata', 'xypoints', 'peak table')
_DATA_LINK = "link"
_CHILDREN = "children"
_XUNIT_MAP = {
    "1/CM": "qudt:PER-CentiM",
}
_PRESSURE_UNIT_MAP = {
    "mmHg": "qudt:MilliM_HG",
}
_LENGTH_UNIT_MAP = {
    "cm": "qudt:CentiM",
}


class UnknownCharacterException(Exception):
    """Exception for unknown character in line of JCAMP-DX file"""


class UnsupportedDataTypeConfigException(Exception):
    """Exception for an unsupported data type configuration for parsing"""


class MultiHeaderKeyException(Exception):
    """Exception for finding multiple header keys in a single line"""


# Compression encoding dictionaries for JCAMP
# Reference found on following site under "Compression Table"
#   - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

# Represents the value with a preceding space (compresses whitespace)
SQZ_digits = {
    '@': '+0',
    'A': '+1',
    'B': '+2',
    'C': '+3',
    'D': '+4',
    'E': '+5',
    'F': '+6',
    'G': '+7',
    'H': '+8',
    'I': '+9',
    'a': '-1',
    'b': '-2',
    'c': '-3',
    'd': '-4',
    'e': '-5',
    'f': '-6',
    'g': '-7',
    'h': '-8',
    'i': '-9',
    '+': '+',  # For PAC
    '-': '-',  # For PAC
    ',': ' ',  # For CSV
}

# Difference agaisnt previous character
DIF_digits = {
    '%': 0,
    'J': 1,
    'K': 2,
    'L': 3,
    'M': 4,
    'N': 5,
    'O': 6,
    'P': 7,
    'Q': 8,
    'R': 9,
    'j': -1,
    'k': -2,
    'l': -3,
    'm': -4,
    'n': -5,
    'o': -6,
    'p': -7,
    'q': -8,
    'r': -9,
}

# Duplicates the previous character by value
DUP_digits = {
    'S': 1,
    'T': 2,
    'U': 3,
    'V': 4,
    'W': 5,
    'X': 6,
    'Y': 7,
    'Z': 8,
    's': 9,
}


def _is_float(strings):
    '''
    Test if a string, or list of strings, contains a numeric value(s).

    Args:
        strings (str or list[str]): The string or list of strings to test.

    Returns:
        is_float_bool (bool or list[bool]): A single boolean or list of boolean
             values indicating whether each input can be converted into float.

    Raises:
        TypeError: If passing a list and elements are not strings or single
            element is not a string
        ValueError: If passing empty list
    '''
    if isinstance(strings, tuple) or isinstance(strings, list):
        if not all(isinstance(i, str) for i in strings):
            raise TypeError("Input {} not a list of strings".format(strings))

        if not strings:
            raise ValueError('Input {} empty'.format(strings))

        bool_list = list(True for i in range(0, len(strings)))
        for i in range(0, len(strings)):
            try:
                float(strings[i])
            except ValueError:
                bool_list[i] = False
        return bool_list

    else:
        if not isinstance(strings, str):
            raise TypeError("Input '%s' is not a string" % (strings))

        try:
            float(strings)
            return True
        except ValueError:
            return False


def _parse_dataset_duplicate_characters(line):
    """
    Parse duplicate character compression for a line (i.e. DUP characters).
    Valid DUP characters are: [S, T, U, V, W, X, Y, Z]

    Example: Repeat 9 character 3 times with 'U'
        "9U" == "999"

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file with duplicate characters (DUP)

    Returns:
        new_line (str): Processed line with duplicates added in
    """
    new_line = ""
    for i, char in enumerate(line):
        if (char in DUP_digits):
            # Get number of duplicates to multiply by
            # NOTE: subtract one since we will already have one character from
            #       the original one we are duplicating from.
            nduplicates = DUP_digits[char] - 1
            new_line += line[i-1] * nduplicates
        else:
            new_line += char
    return "".join(new_line)


def _num_dif_factory(char, line):
    """
    Helper utility factory function to `parse_dataset_line_single_x_multi_y`
    to use the current character to give the next numeric value
    and flag if we are processing using DIF compression.

    Args:
        char (str): Character we are currently processing.
        line (str): Line we are processing, used for raising exception.

    Returns:
        (num, DIF) (tuple): Updated values for numeric character and DIF flag.

    Raises:
        UnkownCharacterException: If we find a character that is neither
            a valid compression character or number.
    """
    if char == ' ':
        num = ''
        DIF = False

    elif char in SQZ_digits:
        num = SQZ_digits[char]
        DIF = False

    elif char in DIF_digits:
        num = str(DIF_digits[char])
        DIF = True

    else:
        msg = f"Unknown character {char} encountered in line {line}"
        raise UnknownCharacterException(msg)

    return (num, DIF)


def _parse_dataset_line_single_x_multi_y(line):
    """
    Parse a JCAMP data line when using the format '(X++(Y..Y))',
    where we have one X column and multiple Y columns on one line.
    Handles decoding JCAMP compression encoding.

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line from JCAMP for data of '(X++(Y..Y))' format

    Returns:
        values (list[float]): List of float values for the line

    Raises:
        UnkownCharacterException: If we find a character that is neither
            a valid compression character or number.
    """
    # process the duplicate characters (DUP_digits)
    DUP_set = set(DUP_digits)
    if any(char in DUP_set for char in line):
        line = _parse_dataset_duplicate_characters(line)

    DIF = False
    num = ''
    values = []
    for char in line:
        if char.isdigit() or char == '.':
            num += char
            continue

        if num:
            value = float(num)
            if DIF:
                value = float(num) + values[-1]
            values.append(value)

        num, DIF = _num_dif_factory(char, line)

    if num:
        value = float(num)
        if DIF:
            value = float(num) + values[-1]
        values.append(value)
    return values


def _parse_dataset_line(line, data_format):
    """
    Parse a data line of the JCAMP-DX file format for the given data format.
    Handles decoding JCAMP compression encoding.

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file to parse
        data_format (str): Format of data. Choices: ['(XY..XY)', '(X++(Y..Y))']

    Returns:
        values (list[float]): List of float values for the line
    """
    if data_format not in _DATA_FORMATS:
        msg = f'Data format {data_format} not supported type: {_DATA_FORMATS}'
        raise UnsupportedDataTypeConfigException(msg)

    if data_format == _DATA_FORMAT_XYXY:
        values = [float(v.strip()) for v in re.split(r"[,;\s]", line) if v]

    if data_format == _DATA_FORMAT_XYYY:
        line = ' '.join(line.split())
        values = _parse_dataset_line_single_x_multi_y(line)

    return values


def _parse_header_get_dict(line, datastart):
    """
    Parse the header line, returning a dictionary for the key-value found
    and if we are starting into the data section.

    Args:
        line (str): Line to parse as a JCAMP header
        datastart (bool): Current flag for if we are in a data section

    Returns:
       header_dict (dict): Dictionary with header keys found.
                           Will mostly return a single key-value pair but
                           for some will return multiple pairs
                           Example: A compound file will return the extra
                           {'children': []} pair when detected.
        datastart (bool): Updated flag for if we are inside a data section
    """
    header_dict = {}

    if line.startswith('##'):
        # Get key-value from header line
        line = line.strip('##')
        (key, value) = line.split('=', 1)
        key = key.strip().lower()
        value = value.strip()

        # Convert 'datatype' key -> _DATA_TYPE_KEY
        if key == 'datatype' or key == 'data type':
            key = _DATA_TYPE_KEY

        # Detect compound files.
        # See table XI in http://www.jcamp-dx.org/protocols/dxir01.pdf
        if (key == _DATA_TYPE_KEY) and (value.lower() == _DATA_LINK):
            header_dict[_CHILDREN] = []

        # Put key-value into JCAMP header dictionary for output
        if value.isdigit():
            header_dict[key] = int(value)
        elif _is_float(value):
            header_dict[key] = float(value)
        else:
            header_dict[key] = value

        # Figure out if we are starting a new data entry
        if (key in _DATA_XY_TYPES):
            datastart = True
            header_dict[_DATA_XY_TYPE_KEY] = value
        elif (key == 'end'):
            datastart = True
        elif datastart:
            datastart = False

    return header_dict, datastart


def _parse_header_line(line, jcamp_dict, datastart=False, last_key=None):
    """
    Parse the JCAMP header line and update the output JCAMP dictionary.

    Args:
        line (str):
        jcamp_dict (dict):
        datastart (bool, optional):
        last_key (str, optional):

    Returns:
        (jcamp_dict, datastart, last_key) (tuple): Tuple
            of the modified JCAMP dictionary, the updated flag for if we are
            in a data section and the last key entered used for updating a
            multiline comment in the header.

    Raises:
        MultiHeaderKeyException: If multiple header keys parsed (should be one)
    """
    output_dict = dict(jcamp_dict)
    header_dict, datastart = _parse_header_get_dict(line, datastart)

    # Get the header key, stripping 'children' key if it is a compound file
    remove_keys = (_CHILDREN, _DATA_XY_TYPE_KEY)
    keys = [k for k in header_dict.keys() if k not in remove_keys]
    if len(keys) > 1:
        msg = f'Found multiple header keys: {keys}'
        raise MultiHeaderKeyException(msg)

    # Check if this is a multiline entry in the header
    is_multiline = last_key and not line.startswith('##') and not datastart
    if is_multiline:
        output_dict[last_key] += '\n{}'.format(line.strip())

    # Just do normal update of jcamp w/ header if not multiline
    elif header_dict:
        output_dict.update(header_dict)
        last_key = keys[0]

    return output_dict, datastart, last_key


def _post_process_data_xy(jcamp_dict, x, y, xstart, xnum):
    """
    Utility function for _reader to format the XY data in a
    post-process manner after we parse out this data from the file.

    Args:
        jcamp_dict (dict): JCAMP dictionary parsed from file
        x (list): X-axis data
        y (list): Y-axis data
        xstart (list): Starting X-axis values for multi-datasets
        xnum (list): Number of starting X-axis value for multi-datasets

    Returns:
        (x, y) (tuple): Post-processed XY data
    """
    if jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYYY:
        xstart.append(jcamp_dict['lastx'])
        x = np.array([])
        for n in range(len(xnum)-1):
            dx = (xstart[n+1] - xstart[n]) / xnum[n]
            x = np.append(x, xstart[n]+(dx*np.arange(xnum[n])))

        if (xnum[len(xnum)-1] > 1):
            numerator = (jcamp_dict['lastx'] - xstart[len(xnum)-1])
            denominator = (xnum[len(xnum)-1] - 1.0)
            dx = numerator / denominator

            xnext = xstart[len(xnum)-1]+(dx*np.arange(xnum[len(xnum)-1]))
            x = np.append(x, xnext)
        else:
            x = np.append(x, jcamp_dict['lastx'])

        y = np.array([float(yval) for yval in y])

    else:
        x = np.array([float(xval) for xval in x])
        y = np.array([float(yval) for yval in y])

    if ('xfactor' in jcamp_dict):
        x = x * jcamp_dict['xfactor']
    if ('yfactor' in jcamp_dict):
        y = y * jcamp_dict['yfactor']
    return x, y


def _reader(filehandle):
    """
    File reader for JCAMP-DX file format

    Args:
        filehandle (list): JCAMP-DX file to read from

    Returns:
        jcamp_dict (dict): Dictionary parsed from JCAMP-DX file
    """
    jcamp_dict = dict()
    xstart = []
    xnum = []
    y = []
    x = []
    datastart = False
    in_compound_block = False
    compound_block_contents = []
    last_key = None
    for line in filehandle:
        # Skip blank or comment lines
        if not line.strip():
            continue
        if line.startswith('$$'):
            continue

        # ===================================
        # Detect the start of a compound block
        is_compound = _CHILDREN in jcamp_dict
        if is_compound and line.upper().startswith('##TITLE'):
            in_compound_block = True
            compound_block_contents = [line]
            continue

        # If we are reading a compound block, collect lines into an array to be
        # processed by a recursive call this this function.
        if in_compound_block:
            compound_block_contents.append(line)

            # Detect the end of the compound block.
            if line.upper().startswith('##END'):
                # Process the entire block and put it into the children array.
                jcamp_dict[_CHILDREN].append(_reader(compound_block_contents))
                in_compound_block = False
                compound_block_contents = []
            continue

        # ===================================
        # Parse header line
        jcamp_dict, datastart, last_key = _parse_header_line(
            line,
            jcamp_dict,
            datastart=datastart,
            last_key=last_key)

        if datastart and not line.startswith('##'):
            if jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYYY:
                datavals = _parse_dataset_line(line, _DATA_FORMAT_XYYY)
                xstart.append(float(datavals[0]))
                xnum.append(len(datavals) - 1)
                y.extend([float(f) for f in datavals[1:]])

            elif jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYXY:
                datavals = _parse_dataset_line(line, _DATA_FORMAT_XYXY)
                x.extend(datavals[0::2])
                y.extend(datavals[1::2])

            else:
                msg = f"Unable to parse data: {jcamp_dict[_DATA_XY_TYPE_KEY]}"
                raise UnsupportedDataTypeConfigException(msg)

    # ===================================
    x, y = _post_process_data_xy(jcamp_dict, x, y, xstart, xnum)
    jcamp_dict['x'] = list(x)
    jcamp_dict['y'] = list(y)

    return jcamp_dict


def _copy_from_dict_to_dict(dict_a, key_a, dict_b, key_b):
    """
    Using dict_a and key_a, add dict_a[key_a] to dict_b[key_b].
    If key_a does not exist in dict_a, just return

    Args:
        dict_a (dict): Dictionary to copy from using key_a
        key_a (str): Key for dict_a to access value to copy to dict_b
        dict_b (dict): Dictionary to copy to at key_b
        key_b (dict): Key for dict_b to store value from dict_a[key_a]
    Returns:
        dict_b (dict): Dictionary w/ new key added (if it exists in dict_a)
    """
    if key_a in dict_a:
        dict_b[key_b] = dict_a[key_a]
    return dict_b


def _get_graph_source_citation_section(jcamp_dict):
    """
    Extract and translate from the JCAMP-DX dictionary the SciData JSON-LD
    citations in the 'sources' section from the '@graph' scection.

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary to extract citations from
    Return:
        citations (list): citations from SciData JSON-LD
    """
    citation = []
    if "$ref author" in jcamp_dict:
        citation.append(f'{jcamp_dict["$ref author"]} :')
    if "$ref title" in jcamp_dict:
        citation.append(f'{jcamp_dict["$ref title"]}.')
    if "$ref journal" in jcamp_dict:
        citation.append(f'{jcamp_dict["$ref journal"]} ')
    if "$ref volume" in jcamp_dict:
        citation.append(f'{jcamp_dict["$ref volume"]}')
    if "$ref date" in jcamp_dict:
        citation.append(f'({jcamp_dict["$ref date"]})')
    if "$ref page" in jcamp_dict:
        citation.append(f'{jcamp_dict["$ref page"]}')
    return citation


def _get_graph_source_section(jcamp_dict):
    """
    Extract and translate from the JCAMP-DX dictionary the SciData JSON-LD
    'sources' section from the '@graph' scection.

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary to extract sources section from
    Return:
        sources (list): 'sources' section of SciData JSON-LD from translation
    """
    sources = []

    citation = _get_graph_source_citation_section(jcamp_dict)
    if citation:
        sources.append({
            "@id": f'source/{len(sources) + 1}',
            "@type": "dc:source",
            "citation": ' '.join(citation),
            "reftype": "journal article",
            "doi": "",
            "url": ""
        })

    if "source reference" in jcamp_dict:
        sources.append({
            "@id": f'source/{len(sources) + 1}',
            "@type": "dc:source",
            "citation": jcamp_dict.get("source reference"),
        })

    if "$nist source" in jcamp_dict or "$nist image" in jcamp_dict:
        citation = ""
        if "$nist source" in jcamp_dict:
            citation += f'NIST SOURCE: {jcamp_dict.get("$nist source")}, '
        if "$nist image" in jcamp_dict:
            citation += f'NIST IMAGE: {jcamp_dict.get("$nist image")}, '
        sources.append({
            "@id": f'source/{len(sources) + 1}',
            "@type": "dc:source",
            "citation": citation,
        })

    return sources


def _get_graph_section(jcamp_dict):
    """
    Extract and translate from the JCAMP-DX dictionary the SciData JSON-LD
    '@graph' section

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary to extract graph section from
    Return:
        graph (dict): '@graph' section of SciData JSON-LD from translation
    """
    # Start translating the JCAMP dict -> SciData dict
    graph = {}
    graph = _copy_from_dict_to_dict(jcamp_dict, "title", graph, "title")
    graph = _copy_from_dict_to_dict(jcamp_dict, "origin", graph, "publisher")
    graph = _copy_from_dict_to_dict(jcamp_dict, "date", graph, "generatedAt")
    if "time" in jcamp_dict:
        graph["generatedAt"] += f' - {jcamp_dict.get("time")}'

    # Description
    description = ""
    description_keywords = [
        "jcamp-dx",
        "class",
        "cas registry no",
        "sample description",
        "xydata"
    ]
    for key in description_keywords:
        if key in jcamp_dict:
            value = jcamp_dict.get(key)
            description += f'{key.upper()}: {value}, '
    graph = _copy_from_dict_to_dict(
            {"description": description}, "description",
            graph, "description")

    # Authors
    graph['author'] = []
    author_keywords = ["owner", "$ref author"]
    for author_keyword in author_keywords:
        if author_keyword in jcamp_dict:
            graph['author'].append({
                "@id": "author/{}".format(len(graph['author']) + 1),
                "@type": "dc:creator",
                "name": jcamp_dict[author_keyword]
            })

    # Sources / references
    sources = _get_graph_source_section(jcamp_dict)

    if sources:
        graph["sources"] = sources

    return graph


def _get_methodology_section(jcamp_dict):
    """
    Extract and translate from the JCAMP-DX dictionary the SciData JSON-LD
    'methodology' section

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary to extract methodology
                           section from
    Return:
        methodology (dict): 'methodology' section of SciData JSON-LD
                            from translation
    """
    methodology = {}
    methodology["evaluation"] = ["experimental"]

    measurement = {}
    if "spectrometer/data system" in jcamp_dict:
        measurement = {
            "@id": "measurement/1/",
            "@type": "sdo:measurement",
            "techniqueType": "cao:spectroscopy",
            "instrument":  f'{jcamp_dict.get("spectrometer/data system")}',
        }

    settings = []
    if "instrument parameters" in jcamp_dict:
        settings.append({
            "@id": f'setting/{len(settings) + 1}',
            "@type": "sdo:setting",
            "property": "instrument parameters",
            "value": {
                "@id": f'setting/{len(settings) + 1}/value',
                "number": jcamp_dict.get("instrument parameters"),
            }
        })

    if "path length" in jcamp_dict:
        pl_value = jcamp_dict.get("path length").split(" ")[0]
        pl_unit = jcamp_dict.get("path length").split(" ")[1]
        pl_unitref = _LENGTH_UNIT_MAP.get(pl_unit.lower())
        settings.append({
            "@id": f'setting/{len(settings) + 1}',
            "@type": "sdo:setting",
            "quantity": "length",
            "property": "path length",
            "value": {
                "@id": f'setting/{len(settings) + 1}/value',
                "number": pl_value,
                "unitref": pl_unitref,
            }
        })

    if "resolution" in jcamp_dict:
        settings.append({
            "@id": f'setting/{len(settings) + 1}',
            "@type": "sdo:setting",
            "quantity": "resolution",
            "property": "resolution",
            "value": {
                "@id": f'setting/{len(settings) + 1}/value',
                "number": jcamp_dict.get("resolution"),
            }
        })

    if settings:
        measurement["settings"] = settings

    aspects = []
    if measurement:
        aspects.append(measurement)
    if "sampling procedure" in jcamp_dict:
        sampling_procedure = {
            "@id": "procedure/1",
            "@type": "sdo:procedure",
            "description": jcamp_dict.get("sampling procedure")
        }
        aspects.append(sampling_procedure)
    if "data processing" in jcamp_dict:
        data_processing_procedure = {
            "@id": "resource/1",
            "@type": "sdo:resource",
            "description": jcamp_dict.get("data processing")
        }
        aspects.append(data_processing_procedure)

    if aspects:
        methodology["aspects"] = aspects

    return methodology


def _get_system_section(jcamp_dict):
    """
    Extract and translate from the JCAMP-DX dictionary the SciData JSON-LD
    'system' section

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary to extract system
                           section from
    Return:
        system (dict): 'system' section of SciData JSON-LD from translation
    """

    system = {}
    system["discipline"] = "w3i:Chemistry"
    system["subdiscipline"] = "w3i:AnalyticalChemistry"

    facets = []
    compound_dict = {}
    if "molform" in jcamp_dict or "cas registry no" in jcamp_dict:
        compound_dict = {
            "@id": "compound/1/",
            "@type": ["sdo:facet", "sdo:material"]
        }
        compound_dict = _copy_from_dict_to_dict(
            jcamp_dict, "title",
            compound_dict, "name")
        if "molform" in jcamp_dict:
            compound_dict = _copy_from_dict_to_dict(
                jcamp_dict, "molform",
                compound_dict, "formula")
        if "cas registry no" in jcamp_dict:
            compound_dict = _copy_from_dict_to_dict(
                jcamp_dict, "cas registry no",
                compound_dict, "casrn")

        facets.append(compound_dict)

    substances_dict = {}
    if "state" in jcamp_dict:
        substances_dict = {
            "@id": "substance/1/",
            "@type": ["sdo:constituent"],
        }
        substances_dict = _copy_from_dict_to_dict(
            jcamp_dict, "title",
            substances_dict, "name")
        substances_dict = _copy_from_dict_to_dict(
            jcamp_dict, "state",
            substances_dict, "phase")

        facets.append(substances_dict)

    if "partial_pressure" in jcamp_dict:
        pp_value = jcamp_dict.get("partial_pressure").split(" ")[0]
        pp_unit = jcamp_dict.get("partial_pressure").split(" ")[1]
        pp_unitref = _PRESSURE_UNIT_MAP.get(pp_unit)
        condition_dict = {
            "@id": "condition/1/",
            "@type": ["sdo:condition"],
            "quantity": "pressure",
            "property": "Partial pressure",
            "value": {
                "@id": "condition/1/value",
                "@type": "sdo:value",
                "number": pp_value,
                "unitref": pp_unitref
            }
        }

        facets.append(condition_dict)

    if facets:
        system["facets"] = facets

    return system


def _get_datagroup_subsection(jcamp_dict):
    xunits = jcamp_dict.get("xunits", "")
    xunitref = _XUNIT_MAP.get(xunits)

    yunitref = jcamp_dict.get("yunits", "")

    datagroup = [
        {
            "@id": "datagroup/1/",
            "@type": "sdo:datagroup",
            "type": "spectrum",
            "attributes": [
                {
                    "@id": "attribute/1/",
                    "@type": "sdo:attribute",
                    "quantity": "count",
                    "property": "Number of Data Points",
                    "value": {
                        "@id": "attribute/1/value/",
                        "@type": "sdo:value",
                        "number": str(len(jcamp_dict['x'])),
                    }
                },
                {
                    "@id": "attribute/2/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "First X-axis Value",
                    "value": {
                        "@id": "attribute/2/value/",
                        "@type": "sdo:value",
                        "number": str(jcamp_dict['x'][0]),
                        "unitref": xunitref,
                    }
                },
                {
                    "@id": "attribute/3/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Last X-axis Value",
                    "value": {
                        "@id": "attribute/3/value/",
                        "@type": "sdo:value",
                        "number": str(jcamp_dict['x'][-1]),
                        "unitref": xunitref,
                    }
                },
                {
                    "@id": "attribute/4/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Minimum X-axis Value",
                    "value": {
                        "@id": "attribute/4/value/",
                        "@type": "sdo:value",
                        "number": str(min(jcamp_dict['x'])),
                        "unitref": xunitref,
                    }
                },
                {
                    "@id": "attribute/5/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Maximum X-axis Value",
                    "value": {
                        "@id": "attribute/5/value/",
                        "@type": "sdo:value",
                        "number": str(max(jcamp_dict['x'])),
                        "unitref": xunitref,
                    }
                },
                {
                    "@id": "attribute/6/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "First Y-axis Value",
                    "value": {
                        "@id": "attribute/6/value/",
                        "@type": "sdo:value",
                        "number": str(jcamp_dict['y'][0]),
                        "unitref": yunitref,
                    }
                },
                {
                    "@id": "attribute/7/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Last Y-axis Value",
                    "value": {
                        "@id": "attribute/7/value/",
                        "@type": "sdo:value",
                        "number": str(jcamp_dict['y'][-1]),
                        "unitref": yunitref,
                    }
                },
                {
                    "@id": "attribute/8/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Minimum Y-axis Value",
                    "value": {
                        "@id": "attribute/8/value/",
                        "@type": "sdo:value",
                        "number": str(min(jcamp_dict['y'])),
                        "unitref": yunitref,
                    }
                },
                {
                    "@id": "attribute/9/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Maximum Y-axis Value",
                    "value": {
                        "@id": "attribute/9/value/",
                        "@type": "sdo:value",
                        "number": str(max(jcamp_dict['y'])),
                        "unitref": yunitref,
                    }
                },
                {
                    "@id": "attribute/10",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "X-axis Scaling Factor",
                    "value": {
                        "@id": "attribute/10/value/",
                        "@type": "sdo:value",
                        "number": f'{jcamp_dict.get("xfactor", "1")}'
                    }
                },
                {
                    "@id": "attribute/11/",
                    "@type": "sdo:attribute",
                    "quantity": "metric",
                    "property": "Y-axis Scaling Factor",
                    "value": {
                        "@id": "attribute/11/value/",
                        "@type": "sdo:value",
                        "number": f'{jcamp_dict.get("yfactor", "1")}'
                    }
                },
            ],
            "dataserieses": [
                "dataseries/1/",
                "dataseries/2/"
            ]
        }
    ]
    return datagroup


def _get_dataseries_subsection(jcamp_dict):
    xunits = jcamp_dict.get("xunits", "")
    xunitref = _XUNIT_MAP.get(xunits)

    dataseries = [
        {
            "@id": "dataseries/1/",
            "@type": "sdo:independent",
            "label": "Wave Numbers (cm^-1)",
            "axis": "x-axis",
            "parameter": {
                "@id": "dataseries/1/parameter/",
                "@type": "sdo:parameter",
                "quantity": "wavenumbers",
                "property": "Wave Numbers",
                "valuearray": {
                    "@id": "dataseries/1/parameter/valuearray/",
                    "@type": "sdo:valuearray",
                    "datatype": "decimal",
                    "numberarray": jcamp_dict['x'],
                    "unitref": xunitref,
                }
            }
        },
        {
            "@id": "dataseries/2/",
            "@type": "sdo:dependent",
            "label": "Intensity (Arbitrary Units)",
            "axis": "y-axis",
            "parameter": {
                "@id": "dataseries/2/parameter/",
                "@type": "sdo:parameter",
                "quantity": "intensity",
                "property": "Intensity",
                "valuearray": {
                    "@id": "dataseries/2/parameter/valuearray/",
                    "@type": "sdo:valuearray",
                    "datatype": "decimal",
                    "numberarray": jcamp_dict['y']
                }
            }
        }
    ]

    return dataseries


def _get_dataset_section(jcamp_dict):
    dataset = {}
    dataset["source"] = "measurement/1"
    dataset["scope"] = "material/1"

    datagroup = _get_datagroup_subsection(jcamp_dict)
    dataseries = _get_dataseries_subsection(jcamp_dict)

    dataset.update({
        "datagroup": datagroup,
        "dataseries": dataseries,
    })

    return dataset


def _translate_jcamp_to_scidata(jcamp_dict):
    """
    Main translation of JCAMP-DX to SciData JSON-LD

    Args:
        jcamp_dict (dict): JCAMP-DX dictionary extracted from read
    Returns:
        scidata_dict (dict): SciDat JSON-LD from translation
    """
    scidata_dict = {}
    scidata_dict = get_scidata_base()

    graph = _get_graph_section(jcamp_dict)
    scidata_dict["@graph"].update(graph)

    scidata_dict["@graph"]["scidata"]["type"] = ["property value"]
    data_type = jcamp_dict.get("data type")
    scidata_dict["@graph"]["scidata"]["property"] = [data_type]

    methodology = _get_methodology_section(jcamp_dict)
    scidata_dict["@graph"]["scidata"]["methodology"].update(methodology)

    system = _get_system_section(jcamp_dict)
    scidata_dict["@graph"]["scidata"]["system"].update(system)

    dataset = _get_dataset_section(jcamp_dict)
    scidata_dict["@graph"]["scidata"]["dataset"].update(dataset)

    return scidata_dict


def _get_description_section(desc, section):
    results = [x for x in desc.split(',') if x.strip().startswith(section)]
    if not results:
        return None
    element = results[0]
    value = element.split(':')[1].strip()
    return value


def _add_header_lines_general(scidata_dict):
    graph = scidata_dict.get("@graph")
    description = graph.get("description", "")
    jcamp_dx = _get_description_section(description, "JCAMP-DX")
    lines = []
    lines.append(f'##JCAMP-DX={jcamp_dx}\n')
    lines.append(f'##DATA TYPE={graph["scidata"]["property"][0]}\n')
    lines.append(f'##ORIGIN={graph["publisher"]}\n')
    lines.append(f'##OWNER={graph["author"][0]["name"]}\n')

    date_and_time = graph.get("generatedAt").split("-")
    date = date_and_time[0].strip()
    lines.append(f'##DATE={date}\n')

    if len(date_and_time) > 1:
        time = date_and_time[1].strip()
        lines.append(f'##TIME={time}\n')

    the_class = _get_description_section(description, "CLASS")
    if the_class:
        lines.append(f'##CLASS={the_class}\n')

    sources = graph.get("sources")
    if sources:
        citation = graph.get("sources")[0]["citation"]
        lines.append(f'##SOURCE REFERENCE={citation}\n')

        for source in sources:
            nist_description = source.get("citation", "")
            if nist_description.startswith("NIST"):
                nist_source = _get_description_section(
                    nist_description,
                    "NIST SOURCE")
                lines.append(f'##$NIST SOURCE={nist_source}\n')

                nist_image = _get_description_section(
                    nist_description,
                    "NIST IMAGE")
                lines.append(f'##$NIST IMAGE={nist_image}\n')

    return lines


def _add_header_lines_methodology(scidata_dict):
    lines = []
    scidata = scidata_dict.get("@graph").get("scidata")
    methodology = scidata.get("methodology")

    # Aspects
    aspects = methodology.get("aspects")
    measurement = ""
    for aspect in aspects:
        if aspect.get("@id").startswith("procedure"):
            lines.append(f'##SAMPLING PROCEDURE={aspect["description"]}\n')

        if aspect.get("@id").startswith("resource"):
            lines.append(f'##DATA PROCESSING={aspect["description"]}\n')

        if aspect.get("@id").startswith("measurement"):
            measurement = aspect
            instrument = measurement.get("instrument")
            lines.append(f'##SPECTROMETER/DATA SYSTEM={instrument}\n')

    # Settings
    settings = measurement.get("settings", "")
    for setting in settings:
        if setting.get("property").startswith("instrument parameters"):
            parameters = setting["value"]["number"]
            lines.append(f'##INSTRUMENT PARAMETERS={parameters}\n')
        if setting.get("property").startswith("path length"):
            reverse_length_map = {v: k for k, v in _LENGTH_UNIT_MAP.items()}
            scidata_path_unit = settings[1]["value"]["unitref"]
            jcamp_path_unit = reverse_length_map[scidata_path_unit]
            path_length = f'{settings[1]["value"]["number"]} '
            path_length += f'{jcamp_path_unit.upper()}'
            lines.append(f'##PATH LENGTH={path_length}\n')
        if setting.get("property").startswith("resolution"):
            resolution = setting["value"]["number"]
            lines.append(f'##RESOLUTION={resolution}\n')

    return lines


def _add_header_lines_system(scidata_dict):
    lines = []
    scidata = scidata_dict.get("@graph").get("scidata")
    system = scidata.get("system")

    # Facets
    facets = system.get("facets")
    if facets:
        for facet in facets:
            if facet.get("@id").startswith("compound"):
                if "casrn" in facet:
                    lines.append(f'##CAS REGISTRY NO={facet["casrn"]}\n')

                if "formula" in facet:
                    lines.append(f'##MOLFORM={facet["formula"]}\n')

            if facet.get("@id").startswith("substance"):
                if "phase" in facet:
                    lines.append(f'##STATE={facet["phase"]}\n')

            if facet.get("@id").startswith("condition"):
                items = _PRESSURE_UNIT_MAP.items()
                reverse_pressure_map = {v: k for k, v in items}
                scidata_punit = facet["value"]["unitref"]
                jcamp_punit = reverse_pressure_map[scidata_punit]
                partial_pressure = f'{facet["value"]["number"]} '
                partial_pressure += f'{jcamp_punit}'
                lines.append(f'##PARTIAL_PRESSURE={partial_pressure}\n')

    return lines


def _add_header_lines_dataset(scidata_dict):
    lines = []

    scidata = scidata_dict.get("@graph").get("scidata")
    dataset = scidata.get("dataset")

    attributes = dataset["datagroup"][0]["attributes"]

    reverse_xunit_map = {v: k for k, v in _XUNIT_MAP.items()}
    scidata_xunits = attributes[1]["value"]["unitref"]
    xunits = reverse_xunit_map[scidata_xunits]

    yunits = attributes[5]["value"]["unitref"]
    xfactor = attributes[9]["value"]["number"]
    yfactor = attributes[10]["value"]["number"]
    first_x = attributes[1]["value"]["number"]
    last_x = attributes[2]["value"]["number"]
    first_y = attributes[5]["value"]["number"]
    max_x = attributes[4]["value"]["number"]
    min_x = attributes[3]["value"]["number"]
    max_y = attributes[8]["value"]["number"]
    min_y = attributes[7]["value"]["number"]
    npoints = attributes[0]["value"]["number"]
    delta_x = (float(last_x) - float(first_x)) / (float(npoints) - 1)

    lines.append(f'##XUNITS={xunits}\n')
    lines.append(f'##YUNITS={yunits}\n')
    lines.append(f'##XFACTOR={xfactor}\n')
    lines.append(f'##YFACTOR={yfactor}\n')
    lines.append(f'##DELTAX={delta_x:.6f}\n')
    lines.append(f'##FIRSTX={first_x}\n')
    lines.append(f'##LASTX={last_x}\n')
    lines.append(f'##FIRSTY={first_y}\n')
    lines.append(f'##MAXX={max_x}\n')
    lines.append(f'##MINX={min_x}\n')
    lines.append(f'##MAXY={max_y}\n')
    lines.append(f'##MINY={min_y}\n')
    lines.append(f'##NPOINTS={npoints}\n')

    description = scidata_dict.get("@graph").get("description")
    xydata = _get_description_section(description, "XYDATA")
    lines.append(f'##XYDATA={xydata}\n')

    return lines


def _write_header(filename, scidata_dict, mode='w'):
    lines = []

    graph = scidata_dict.get("@graph")
    lines.append(f'##TITLE={graph.get("title")}\n')

    lines += _add_header_lines_general(scidata_dict)
    lines += _add_header_lines_methodology(scidata_dict)
    lines += _add_header_lines_system(scidata_dict)
    lines += _add_header_lines_dataset(scidata_dict)

    with open(filename, mode) as fileobj:
        for line in lines:
            fileobj.write(line)


def _write_data(filename, scidata_dict, mode='w'):
    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    dataseries = dataset.get("dataseries")
    with open(filename, mode) as fileobj:
        xdata = []
        ydata = []
        for data in dataseries:
            if data.get("axis") == "x-axis":
                xdata = data["parameter"]["valuearray"]["numberarray"]
            if data.get("axis") == "y-axis":
                ydata = data["parameter"]["valuearray"]["numberarray"]

        for x, y in zip(xdata, ydata):
            fileobj.write(f' {x:.3f},   {y:.3f}\n')


def read_jcamp(filename):
    """
    Reader for JCAMP-DX files to SciData JSON-LD dictionary
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
    JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename to read from for JCAMP-DX files

    Returns:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    # Extract jcamp file data
    with open(filename, 'r') as fileobj:
        jcamp_dict = _reader(fileobj)
    scidata_dict = _translate_jcamp_to_scidata(jcamp_dict)
    return scidata_dict


def write_jcamp(filename, scidata_dict):
    """
    Writer for SciData JSON-LD dictionary to JCAMP-DX files.
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
    JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename for JCAMP-DX file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    _write_header(filename, scidata_dict, mode='w')
    _write_data(filename, scidata_dict, mode='a')
    with open(filename, 'a') as fileobj:
        fileobj.write('##END=\n')
