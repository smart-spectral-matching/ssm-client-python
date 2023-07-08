from scidatalib.scidata import SciData


def read_ssm_json(filename: str) -> dict:
    """
    Reader for SSM JSON files to SciData JSON-LD dictionary

    Args:
        filename (str): Filename to read from for SSM JSON
    Return:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    with open(filename, 'r') as fileobj:
        ssm_json_dict = json.load(fileobj)
    scidata_obj = _ssm_json_to_scidata(ssm_json_dict)
    return scidata_obj.output


def write_ssm_json(filename: str, scidata_dict: dict) -> dict:
    """
    Writer for SciData JSON-LD dictionary to SSM JSON files.

    Args:
        filename: Filename for SSM JSON file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    ssm_json_dict = _scidata_to_ssm_json(scidata_dict)
    with open(filename, "w") as fileobj:
        json.dump(ssm_json_dict, fileobj, indent=2)


def _scidata_to_ssm_json(scidata: SciData) -> dict:
    """
    Convert from SciData JSON-LD to SSM abbreviated JSON

    Args:
        scidata (dict): SciData JSON-LD dictionary to convert to SSM JSON
    Return:
        ssm_json (dict): SSM JSON dictionary
    """
    output = dict()
    output["title"] = scidata.output["@graph"]["title"]
    if scidata.output["@id"]:
        output["url"] = scidata.output["@id"]
    output["created"] = scidata.output["generatedAt"]
    output["modified"] = scidata.output["generatedAt"]
    output["description"] = scidata.output["@graph"]["description"]

    # sources
    if "sources" in scidata.output["@graph"]:
        sources_list = scidata.output["@graph"]["sources"]
        output_sources_list = list()
        for source in sources_list:
            source.pop("@id")
            source.pop("@type")
            output_sources_list.append(source)

        output["sources"] = output_sources_list

    sd = scidata.output["@graph"]["scidata"]

    output["scidata"] = dict()

    #   property
    properties = sd.get("property", None)
    if properties:
        properties = ','.join(properties)
        output["scidata"]["property"] = properties

    #   methodology
    methodology = sd.get("methodology", None)

    if methodology:
        output_methodology = dict()

        evaulation = methodology.get("evaluation", None)
        if evaulation:
            output_methodology["evaluationMethod"] = evaulation

        aspects_list = methodology.get("aspects", list())
        if aspects_list:
            output_aspect_list = list()
            for aspect in aspects_list:
                aspect.pop("@id")
                aspect.pop("@type")
                output_aspect_list.append(aspect)

            if output_aspect_list:
                for aspect_dict in output_aspect_list:
                    for k, v in aspect_dict.items():
                        output_methodology[k] = v

        output["scidata"]["methodology"] = output_methodology

    #   system
    system = sd.get("system", None)
    if system:
        output_system = dict()

        facets_list = system.get("facets", list())
        if facets_list:
            output_facet_list = list()
            for facet in facets_list:
                facet.pop("@id")
                facet.pop("@type")
                output_facet_list.append(facet)

            if output_facet_list:
                for facet_dict in output_facet_list:
                    for k, v in facet_dict.items():
                        output_system[k] = v

        output["scidata"]["system"] = output_system

    #   dataset
    dataset = sd.get("dataset", None)
    if dataset:

        dataseries_list = dataset.get("dataseries", list())
        if dataseries_list:
            output_dataseries_list = list()
            for dataseries in dataseries_list:
                output_dataseries = dict()

                label = dataseries.get("label", None)
                if label:
                    output_dataseries["label"] = label

                axisType = dataseries.get("axisType", None)
                if axisType:
                    output_dataseries["axisType"] = axisType

                parameter_list = dataseries.get("parameter", None)
                if parameter_list:
                    for i, parameter in enumerate(parameter_list):
                        output_parameter = dict()

                        parameter.pop("@id")
                        parameter.pop("@type")

                        quantity = parameter.get("quantity", None)
                        if quantity:
                            output_parameter["quantity"] = quantity

                        sd_property = parameter.get("property", None)
                        if sd_property:
                            output_parameter["property"] = sd_property

                        units = parameter.get("units", None)
                        if units:
                            output_parameter["units"] = units

                        unitref = parameter.get("unitref", None)
                        if unitref:
                            output_parameter["unitref"] = unitref

                        datatype = parameter.get("datatype", None)
                        if datatype:
                            output_parameter["datatype"] = datatype

                        dataarray = parameter.get("dataarray", None)
                        if dataarray:
                            output_parameter["numericValueArray"] = [
                                {"numberArray": dataarray}
                            ]

                        axis = parameter.get("axis", f"axis-{i}")
                        output_dataseries_list.append({
                            f'{axis}': {"parameter": output_parameter},
                            "hasAxisType": axis
                        })

        output_dataseries = output_dataseries_list
        output["scidata"]["dataseries"] = output_dataseries
        # TODO: need to fix that we use 'dataseries' instead of 'dataset'

    return output


def _ssm_json_to_scidata(ssm_json: dict) -> SciData:
    """
    Convert from SSM JSON to SciData JSON-LD

    Args:
        ssm_json (dict): SSM JSON to convert to SciData JSON-LD dictionary
    Return:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    # Construct UID for SciData document from title
    title = ssm_json.get("title", "ssm:dataset")
    uid = ssm_json.get("uid", f'scidata:jsonld:{title}')

    # Setup SciData object
    sd = SciData(uid)
    sd.title = title
    sd.docid = ssm_json.get("url", "")

    #   sources
    sources = ssm_json.get("sources", list())
    if sources:
        for source in sources:
            source["@id"] = "source"
            source["@type"] = "dc:source"
        sd.sources(sources)

    properties = ssm_json.get("scidata").get("property", "").split(",")
    sd.meta['@graph']['scidata']['property'] = properties

    description = ssm_json.get("description", "")
    sd.description(description)

    #   methodology
    methodology = ssm_json.get("scidata").get("methodology")

    if methodology:
        if "evaluationMethod" in methodology:
            sd.evaluation(methodology.get("evaluationMethod"))
        elif "evaluation" in methodology:
            sd.evaluation(methodology.get("evaluation"))

        # aspects
        aspects = list()
        if "aspects" in methodology:
            aspects = methodology.get("aspects")
            for aspect in aspects:
                # default to make everything a "measurement"
                aspect["@id"] = "measurement"
                aspect["@type"] = "sdo:measurement"

        # technique aspect
        technique = None
        if "techniqueType" in methodology:
            technique = methodology.get("techniqueType")

        instrument = None
        if "instrument" in methodology:
            instrument = methodology.get("instrument")

        if technique or instrument:
            aspect = dict()
            if technique:
                aspect["techniqueType"] = technique
            if instrument:
                aspect["instrument"] = instrument

            # default to make everything a "measurement"
            aspect["@id"] = "measurement"
            aspect["@type"] = "sdo:measurement"
            aspects.append(aspect)

        if aspects:
            sd.aspects(aspects)

    #   system
    system = ssm_json.get("scidata").get("system", None)

    if system:
        if "facets" in system:
            facets = system.get("facets")
            for facet in facets:
                aspect["@id"] = ""
                aspect["@type"] = "facet/"
            sd.aspects(aspects)

    #   dataset
    # TODO: need to fix that we use 'dataseries' instead of 'dataset'
    # (i.e. need ssm_json.get("scidata").get("dataset"))
    dataset = ssm_json.get("scidata")

    dataseries_list = dataset.get("dataseries", None)
    if dataseries_list:
        for dataseries_json in dataseries_list:
            output_dataseries_list = list()
            for axis, dataseries in dataseries_json.items():
                # skip the non-axis dataseries (i.e. "hasAxisType" key)
                if "-axis" not in axis:
                    continue
                output_dataseries = dict()
                output_dataseries["@id"] = "dataseries"

                label = dataseries.get("label", None)
                if label:
                    output_dataseries["label"] = label

                parameter_list = dataseries.get("parameter", None)
                if parameter_list:
                    output_parameter = dict()
                    for key, parameter in parameter_list.items():
                        output_parameter[key] = parameter
                    output_dataseries["parameter"] = output_parameter

            output_dataseries_list.append(output_dataseries)

        sd.dataseries(output_dataseries_list)

    return sd

