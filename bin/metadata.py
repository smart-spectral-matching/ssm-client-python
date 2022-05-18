import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
import pathlib
import ssm_rest_python_client as ssm
from typing import List


def _get_worksheet_data(
    worksheet: Worksheet,
    key_name: str = None,
) -> dict:
    data = list(worksheet.values)
    labels = data[0]
    entries = data[1:]

    data_dict = {}
    for i, row in enumerate(entries):
        entry = {k: v for k, v in zip(labels, row)}
        key = i
        if key_name:
            key = entry.get(key_name)
        data_dict[key] = entry

    return data_dict


def _get_filenames_to_remove(file_summary_dict: dict) -> List[str]:
    remove_list = []
    for k, v in file_summary_dict.items():
        if not v["File Type"]:
            remove_list.append(k)
            continue
        if not v["File Type"].startswith("Spectra"):
            remove_list.append(k)
            continue
        if "Raman" not in v["File Type"]:
            remove_list.append(k)
    return remove_list


def _get_mineral_data_worksheet(curies: str, workbook: str) -> Worksheet:
    '''
    Get the mineral data workbook
    '''
    curies_path = pathlib.Path(curies)
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)
    mineral_data_worksheet = wb['Mineral Data']
    return mineral_data_worksheet


def _get_functional_group_list(curies: str, workbook: str) -> list:
    '''
    Pull out the functional group list from the workbook
    '''
    # Constants
    first_functional_group_label = "U"
    last_functional_group_label = "Th"

    # Get "Mineral Data" worksheet and functional group labels from worksheet
    ws = _get_mineral_data_worksheet(curies, workbook)
    labels = list(ws.values)[0]

    # Get functional group list
    start = labels.index(first_functional_group_label)
    stop = labels.index(last_functional_group_label)
    functional_group_list = labels[start:stop]

    return functional_group_list


def _get_formula_dict(file_summary_dict, location):
    formula = file_summary_dict[location]["Formula"]
    mineral_name = file_summary_dict[location]["Mineral Name"]
    formula_dict = {
        "@id": "compound/1/",
        "@type": "sdo:compound",
        "formula": formula,
        "name": mineral_name,
    }
    return formula_dict


def _get_structure_type_dict(file_summary_dict, location):
    structure_type = file_summary_dict[location]["Structure type"]
    structure_type_dict = {
        "@id": "structuretype/1/",
        "@type": "sdo:value",
        "structure type": structure_type,
    }
    return structure_type_dict


def _get_crystal_system_dict(file_summary_dict, location):
    crystal_system = file_summary_dict[location]["Crystal System"]
    crystal_system_dict = {
        "@id": "crystalsystem/1/",
        "@type": "sdo:value",
        "crystal system": crystal_system,
    }
    return crystal_system_dict


def _get_uranium_coordination_chemistry(
    file_summary_dict: dict,
    location: str,
    coordination_type: str,
    index: int = 1,
) -> dict:
    coordination_dict = {}
    coordination = file_summary_dict[location][coordination_type]
    if coordination > 0:
        coordination_dict = {
            "@id": f'coordinationchemistry/{index}/',
            "@type": "sdo:value",
            "uranium coordination chemistry": coordination_type,
            "multiplicity": coordination,
        }
    return coordination_dict


def get_file_summary_dict(curies: str, workbook: str) -> dict:
    '''
    Get the file summary dict for metadata from the workbook for all of CURIES
    '''
    curies_path = pathlib.Path(curies)

    # Master workbook with additional metadata
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)

    # Get the dict for the files summary worksheet
    file_summary_dict = _get_worksheet_data(wb['Files Summary'], key_name=None)

    # Get the dict for the mineral data worksheet + list of functional groups
    mineral_data_dict = _get_worksheet_data(
        wb['Mineral Data'],
        key_name='Mineral Name')

    # Filter out non-spectra data from file summary
    remove_list = _get_filenames_to_remove(file_summary_dict)
    for remove_key in remove_list:
        file_summary_dict.pop(remove_key)

    # Refactor file summary data to include mineral data + re-index
    new_dict = {}
    for value in file_summary_dict.values():
        filename = curies_path / value["Filename"]
        new_dict[filename] = value
        mineral_data = mineral_data_dict[value.get("Mineral Name")]
        new_dict[filename].update(mineral_data)
    file_summary_dict = new_dict

    return file_summary_dict


def get_scidata(
    location: pathlib.Path,
    file_summary_dict: dict,
    curies: str,
    workbook: str
) -> dict:
    # Get SciData dictionary from file
    scidata_dict = ssm.io.read(location.absolute(), ioformat="rruff")

    # Add space group to SciData
    space_group = file_summary_dict[location]["Space Group"]
    space_group_dict = {
        "@id": "datapoint/1/",
        "@type": "sdo:datapoint",
        "url": "http://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Ispace_group_IT_number.html", # noqa
        "quantity": "space group descriptor",
        "property": "space_group_IT_number",
        "value": {
            "@id": "datapoint/1/value/",
            "@type": "sdo:value",
            "text": space_group
        }
    }
    scidata_dict["@graph"]["scidata"]["dataset"].update(
        {"datapoint": [space_group_dict]}
    )

    # Add formula to SciData
    formula_dict = _get_formula_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    facets.append(formula_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add functional groups to SciData
    functional_group_list = _get_functional_group_list(curies, workbook)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    functional_groups = {}
    for fgroup in functional_group_list:
        multiplicity = file_summary_dict[location][fgroup]
        if multiplicity != 0:
            functional_groups[fgroup] = multiplicity
    for i, (fgroup, multiplicity) in enumerate(functional_groups.items()):
        new_facet = {
            "@id": f'functionalgroup/{i+1}',
            "@type": "sdo:molsystem",
            "atoms": fgroup,
            "multiplicity": multiplicity
        }
        facets.append(new_facet)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add structure type
    structure_type_dict = _get_structure_type_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    facets.append(structure_type_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add crystal system
    crystal_system_dict = _get_crystal_system_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    facets.append(crystal_system_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add square coordination chemistry
    square = _get_uranium_coordination_chemistry(
        file_summary_dict,
        location,
        coordination_type="square",
        index=1
    )
    pentagonal = _get_uranium_coordination_chemistry(
        file_summary_dict,
        location,
        coordination_type="pentagonal",
        index=2
    )
    hexagonal = _get_uranium_coordination_chemistry(
        file_summary_dict,
        location,
        coordination_type="hexagonal",
        index=3
    )
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    if square:
        facets.append(square)
    if pentagonal:
        facets.append(pentagonal)
    if hexagonal:
        facets.append(hexagonal)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    return scidata_dict
