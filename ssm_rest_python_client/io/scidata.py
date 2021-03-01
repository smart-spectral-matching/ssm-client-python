import copy
import datetime

__CONTEXT_HEADER = {
    "@context": [
        "https://stuchalk.github.io/scidata/contexts/scidata.jsonld",
        {
            "sdo": "https://stuchalk.github.io/scidata/ontology/scidata.owl#",
            "sub": "https://stuchalk.github.io/scidata/ontology/substance.owl#",  # noqa: E501
            "chm": "https://stuchalk.github.io/scidata/ontology/chemical.owl#",
            "w3i": "https://w3id.org/skgo/modsci#",
            "cao": "http://champ-project.org/images/ontology/cao.owl#",
            "qudt": "http://qudt.org/vocab/unit/",
            "obo": "http://purl.obolibrary.org/obo/",
            "dc": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
    ]
}

__DEFAULTS = {
    "version": 2,
    "@id": "",
    "@graph": {
        "@id": "",
        "@type": "sdo:scidataFramework",
        "scidata": {
            "@id": "scidata",
            "@type": "sdo:scientificData",
            "methodology": {
                "@id": "methodology",
                "@type": "sdo:methodology",
            },
            "system": {
                "@id": "system/",
                "@type": "sdo:system",
            },
            "dataset": {
                "@id": "dataset/",
                "@type": "sdo:dataset",
            },
        }
    }
}


def get_context_header():
    """
    Get the JSON-LD context (i.e. '@context') header
    for the SciData JSON-LD dict.
        URL: https://json-ld.org/spec/latest/json-ld/#the-context

    Return:
        context (dict): JSON-LD context header (i.e. '@context' entry)
    """
    return copy.deepcopy(__CONTEXT_HEADER)


def get_scidata_defaults():
    """
    Get the JSON-LD defaults for the SciData JSON-LD dict.

    Return:
        defaults (dict): SciData JSON-LD defaults
    """
    return copy.deepcopy(__DEFAULTS)


def get_scidata_base():
    """
    Get a base SciData JSON-LD dictionary to modify for different file formats

    Return:
        scidata_base_dict (dict): Base SciData JSON-LD to modify for output
    """
    scidata_dict = {}

    # Add context
    context = get_context_header()
    scidata_dict.update(context)

    # Add generatedAt key
    dt = datetime.datetime.now()
    generated_at = dt.strftime("%Y-%m-%d %H:%M:%S")
    scidata_dict.update({"generatedAt": generated_at})

    # Add defaults
    defaults = get_scidata_defaults()
    scidata_dict.update(defaults)

    return scidata_dict
