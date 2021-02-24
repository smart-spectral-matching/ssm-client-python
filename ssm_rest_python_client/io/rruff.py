import numpy as np

from .jcamp import (
    _copy_from_dict_to_dict,
    _DATA_FORMAT_XYXY,
    _DESCRIPTION_KEY_SPLIT_CHAR,
    _extract_description_section,
    _parse_header_line,
    _parse_dataset_line,
    _write_jcamp_data_section,
)
from .scidata import get_scidata_base


def _reader(filehandle):
    rruff_dict = {}
    y = []
    x = []
    for line in filehandle:
        # Skip blank or comment lines
        if not line.strip():
            continue
        if line.startswith("$$"):
            continue

        rruff_dict, _, _ = _parse_header_line(line, rruff_dict)

        if not line.startswith("##"):
            datavals = _parse_dataset_line(line, _DATA_FORMAT_XYXY)
            x.extend(datavals[0::2])
            y.extend(datavals[1::2])

    x = np.array([float(xval) for xval in x])
    y = np.array([float(yval) for yval in y])

    if ("xfactor" in rruff_dict):
        x = x * rruff_dict["xfactor"]
    if ("yfactor" in rruff_dict):
        y = y * rruff_dict["yfactor"]

    rruff_dict["x"] = list(x)
    rruff_dict["y"] = list(y)

    return rruff_dict


def _get_graph_section(rruff_dict):
    """
    Extract and translate from the RRUFF dictionary the SciData JSON-LD
    '@graph' section

    Args:
        rruff_dict (dict): RRUFF dictionary to extract graph section from
    Return:
        graph (dict): '@graph' section of SciData JSON-LD from translation
    """
    # Start translating the RRUFF dict -> SciData dict
    graph = {}
    graph = _copy_from_dict_to_dict(rruff_dict, "names", graph, "title")
    graph = _copy_from_dict_to_dict(rruff_dict, "owner", graph, "publisher")

    # Description
    description = []
    if "description" in rruff_dict:
        description.append(f'DESCRIPTION: {rruff_dict.get("description")}')
    if "locality" in rruff_dict:
        description.append(f'LOCALITY: {rruff_dict.get("locality")}')
    if "status" in rruff_dict:
        description.append(f'STATUS: {rruff_dict.get("status")}')

    description = _DESCRIPTION_KEY_SPLIT_CHAR.join(description)
    graph = _copy_from_dict_to_dict(
            {"description": description}, "description",
            graph, "description")

    # UID
    rruff_dict.update({"rruffid": f'rruff:{rruff_dict.get("rruffid")}'})
    graph = _copy_from_dict_to_dict(
        rruff_dict, "rruffid",
        graph, "uid")

    # Authors
    graph['author'] = []
    author_keywords = ["source"]
    for author_keyword in author_keywords:
        if author_keyword in rruff_dict:
            graph['author'].append({
                "@id": "author/{}".format(len(graph['author']) + 1),
                "@type": "dc:creator",
                "name": rruff_dict[author_keyword]
            })

    # Sources / references
    sources = []
    sources.append({
        "@id": "source/1/",
        "@type": "dc:source",
        "citation": "Highlights in Mineralogical Crystallography 2015 1-30",
        "reftype": "journal article",
        "doi": "10.1515/9783110417104-003",
        "url": "https://doi.org/10.1515/9783110417104-003"
    })

    if "url" in rruff_dict:
        sources.append({
                "@id": f"source/{len(sources) + 1}",
                "@type": "dc:source",
                "citation": "RRUFF project database entry",
                "url": "https://rruff.info/R060361",
            })
    graph["sources"] = sources

    return graph


def _get_methodology_section(rruff_dict):
    """
    Extract and translate from the RRUFF dictionary the SciData JSON-LD
    'methodology' section

    Args:
        rruff_dict (dict): RRUFF dictionary to extract methodology section from
    Return:
        graph (dict): 'methodology' section of SciData JSON-LD from translation
    """
    methodology = {}
    methodology["evaluation"] = ["experimental"]

    methodology["aspects"] = []
    if "laser_wavelength" in rruff_dict:
        methodology["aspects"].append({
            "@id": "measurement/1/",
            "@type": "cao:CAO_000152",
            "techniqueType": "obo:CHMO_0000228",
            "technique": "obo:CHMO_0000656",
            "instrumentType": "raman spectrometer",
            "instrument": "Unknown",
            "settings": [{
                "@id": "setting/1",
                "@type": "sdo:setting",
                "quantity": "wavelength",
                "property": "Laser Wavelength",
                "value": {
                    "@id": "setting/1/value/",
                    "number": rruff_dict.get("laser_wavelength"),
                    "unitstr": "qubt:NanoM",
                }
            }]
        })
    return methodology


def _get_system_section(rruff_dict):
    system = {}
    system["discipline"] = "w3i:Chemistry"
    system["subdiscipline"] = "w3i:AnalyticalChemistry"

    facets_dict = {
        "@id": "material/1/",
        "@type": ["sdo:facet", "sdo:material"]
    }
    facets_dict = _copy_from_dict_to_dict(
        rruff_dict, "names",
        facets_dict, "name")
    facets_dict = _copy_from_dict_to_dict(
        rruff_dict, "ideal chemistry",
        facets_dict, "materialType")

    system["facets"] = [facets_dict]
    return system


def _get_datagroup_subsection(rruff_dict):
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
                        "number": str(len(rruff_dict['x'])),
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
                        "number": str(rruff_dict['x'][0]),
                        "unitref": "qudt:PER-CentiM",
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
                        "number": str(rruff_dict['x'][-1]),
                        "unitref": "qudt:PER-CentiM",
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
                        "number": str(min(rruff_dict['x'])),
                        "unitref": "qudt:PER-CentiM",
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
                        "number": str(max(rruff_dict['x'])),
                        "unitref": "qudt:PER-CentiM",
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
                        "number": str(rruff_dict['y'][0]),
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
                        "number": str(rruff_dict['y'][-1]),
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
                        "number": str(min(rruff_dict['y'])),
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
                        "number": str(max(rruff_dict['y'])),
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
                        "number": "1"
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
                        "number": "1"
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


def _get_dataseries_subsection(rruff_dict):
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
                    "numberarray": rruff_dict['x'],
                    "unitref": "qudt:PER-CentM",
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
                    "numberarray": rruff_dict['y']
                }
            }
        }
    ]

    return dataseries


def _get_dataset_section(rruff_dict):
    dataset = {}
    dataset["source"] = "measurement/1"
    dataset["scope"] = "material/1"

    datagroup = _get_datagroup_subsection(rruff_dict)
    dataseries = _get_dataseries_subsection(rruff_dict)

    dataset.update({
        "datagroup": datagroup,
        "dataseries": dataseries,
    })

    return dataset


def _translate_rruff_to_scidata(rruff_dict):
    """
    Main translation of RRUFF to SciData JSON-LD

    Args:
        rruff_dict (dict): RRUFF dictionary extracted from read
    Returns:
        scidata_dict (dict): SciDat JSON-LD from translation
    """
    scidata_dict = get_scidata_base()

    graph = _get_graph_section(rruff_dict)
    scidata_dict["@graph"].update(graph)

    scidata_dict["@graph"]["scidata"]["type"] = ["property value"]
    scidata_dict["@graph"]["scidata"]["property"] = ["raman spectroscopy"]

    methodology = _get_methodology_section(rruff_dict)
    scidata_dict["@graph"]["scidata"]["methodology"].update(methodology)

    system = _get_system_section(rruff_dict)
    scidata_dict["@graph"]["scidata"]["system"].update(system)

    dataset = _get_dataset_section(rruff_dict)
    scidata_dict["@graph"]["scidata"]["dataset"].update(dataset)

    return scidata_dict


def _write_rruff_header_section(filename, scidata_dict, mode='w'):
    lines = []

    graph = scidata_dict.get("@graph")
    lines.append(f'##NAMES={graph.get("title")}\n')

    rruffid = graph.get("uid").strip("rruff:")
    lines.append(f'##RRUFFID={rruffid}\n')

    description = scidata_dict.get("@graph").get("description")

    system = graph.get('scidata').get('system')
    for facet in system.get('facets'):
        if facet.get('@id').startswith('material'):
            chemistry = facet.get('materialType')
            lines.append(f'##IDEAL CHEMISTRY={chemistry}\n')

    locality = _extract_description_section(description, "LOCALITY")
    if locality:
        lines.append(f'##LOCALITY={locality}\n')

    with open(filename, mode) as fileobj:
        for line in lines:
            fileobj.write(line)


def read_rruff(filename):
    """
    Reader for RRUFF database files to SciData JSON-LD dictionary
    RRUFF file format is a modified version of JCAMP, so re-use jcamp module

    Args:
        filename (str): Filename to read from for RRUFF files

    Returns:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    # Extract rruff file data
    with open(filename, "r") as fileobj:
        rruff_dict = _reader(fileobj)
    scidata_dict = _translate_rruff_to_scidata(rruff_dict)
    return scidata_dict


def write_rruff(filename, scidata_dict):
    """
    Reader for RRUFF database files to SciData JSON-LD dictionary
    RRUFF file format is a modified version of JCAMP, so re-use jcamp module

    Args:
        filename (str): Filename for RRUFF file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    _write_rruff_header_section(filename, scidata_dict, mode='w')
    _write_jcamp_data_section(filename, scidata_dict, mode='a')
    with open(filename, 'a') as fileobj:
        fileobj.write('##END=\n')
