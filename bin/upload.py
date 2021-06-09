import json
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
import pathlib
import ssm_rest_python_client as ssm
import time
from typing import List


def get_worksheet_data(
    worksheet: Worksheet,
    key_name: str = None,
) -> dict:
    data = list(worksheet.values)
    labels = data[0]
    entries = data[1:]

    data_dict = {}
    for i, row in enumerate(entries):
        entry = { k:v for k, v in zip(labels, row)}
        key = i
        if key_name:
            key = entry.get(key_name)
        data_dict[key] = entry

    return data_dict
    

def get_filenames_to_remove(file_summary_dict: dict) -> List[str]:
    remove_list = []
    for k, v in file_summary_dict.items():
        if not v["File Type"]:
            remove_list.append(k)
            continue
        if not v["File Type"].startswith("Spectra"):
            remove_list.append(k)
            continue
        if not "Raman" in v["File Type"]:
            remove_list.append(k)
    return remove_list


def get_functional_group_list(curies: str, workbook: str) -> list:
    '''
    Pull out the functional group list from the workbook
    '''
    # Master workbook with additional metadata
    curies_path = pathlib.Path(curies)
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)

    # Get functional group list
    functional_groups_start_index = 12
    labels = list(wb['Mineral Data'].values)[0]
    functional_group_list = labels[functional_groups_start_index:]

    return functional_group_list

def get_file_summary_dict(curies: str, groups: List[str], workbook: str) -> dict:
    '''
    Get the file summary dictionary for metadata from the workbook for all of CURIES
    '''
    curies_path = pathlib.Path(curies)

    # Master workbook with additional metadata
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)

    # Get the dictionary for the files summary worksheet 
    file_summary_dict = get_worksheet_data(wb['Files Summary'], key_name=None)

    # Get the dictionary for the mineral data worksheet + list of functional groups
    mineral_data_dict = get_worksheet_data(wb['Mineral Data'], key_name='Mineral Name')

    # Filter out non-spectra data from file summary
    remove_list = get_filenames_to_remove(file_summary_dict)
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


def get_scidata(location: pathlib.Path, file_summary_dict: dict, curies: str, workbook: str) -> dict:
    # Get SciData dictionary from file
    scidata_dict = ssm.io.read(location.absolute(), ioformat="rruff")

    # Add space group to SciData
    space_group = file_summary_dict[location]["Space Group"]
    space_group_dict = {
        "@id": "datapoint/1/",
        "@type": "sdo:datapoint",
        "url": "http://www.iucr.org/__data/iucr/cifdic_html/1/cif_core.dic/Ispace_group_IT_number.html",
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
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    formula = file_summary_dict[location]["Formula"]
    mineral_name = file_summary_dict[location]["Mineral Name"]
    formula_dict = {
        "@id": "compound/1/",
        "@type": "sdo:compound",
        "formula": formula,
        "name": mineral_name ,
    }
    facets.append(formula_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add functional groups to SciData
    functional_group_list = get_functional_group_list(curies, workbook)
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

    return scidata_dict


def upload_directories(curies, groups, hostname, workbook, limit_spectra=None, blacklist=None, dataset_uuid=None):
    """
    """
    curies_path = pathlib.Path(curies)

    # Black list of files that are not in RRUFF file format
    if not blacklist:
        blacklist = []

    # Create rest client
    rester = ssm.SSMRester(hostname=hostname)

    # Setup dataset
    if dataset_uuid:
        dataset = rester.dataset.get_by_uuid(dataset_uuid)
    else:
        dataset = rester.dataset.create()

    # Get file summary dict
    file_summary_dict = get_file_summary_dict(curies, groups, workbook)

    # Loop over directories
    total_spectra = 0
    for directory in groups:
        print(f'***********\n{directory}\n***********')

        # Create dataset in database to hold directory data
        rester.initialize_model_for_dataset(dataset)

        # Glob the spectra file paths
        directory = pathlib.Path(curies_path, directory, "Spectra")
        locations = directory.glob("*.txt")

        # Tally up total spectra for group and overall
        total_group_spectra = len(list(locations))
        total_spectra += total_group_spectra
        locations = directory.glob("*.txt")

        if limit_spectra:
            locations = list(locations)[0:limit_spectra]

        print(f'  Dataset URI: {hostname}/datasets/{dataset.uuid}')
        print(f'  Number of spectra: {total_group_spectra}\n')


        # Loop over spectra for the directory
        for i, location in enumerate(locations):
            print(f'  {location.name} {i+1} of {total_group_spectra}')
            # Skip non-RRUFF files for now
            if location.name in blacklist:
                print(f'    {location.name} skipped... ***')
                continue

            # Skip duplicates
            duplicate_path = curies / location
            if duplicate_path in blacklist:
                print(f'    {location} skipped... ***')
                continue

            print(f'    reading...')
            try:
                scidata_dict = get_scidata(location, file_summary_dict, curies, workbook)
            except KeyError:
                print(f'ERROR: issue with {location} not found in file summary dictionary')

            # Upload file to dataset
            print(f'    uploading..')
            while True:
                try:
                    model = rester.model.create(scidata_dict)    
                    print(f'    {hostname}/datasets/{dataset.uuid}/models/{model.uuid}\n')
                    break
                except Exception as e:
                    print(f' ERROR: {e}')
                    print('Retrying...')
                    time.sleep(5)


if __name__ == "__main__":
    curies_directory = "CURIES_20210601"
    group_directories = [
        "Arsenates",
        "Carbonates",
        "Hydroxides",
        "Phosphates",
        "Silicates",
        "Sulfates",
        "Other U Minerals",
        "Vanadates",
        "U Oxides",
    ]
    workbook = "Master_v2_add_filenames.xlsx"

    hostname = "http://ssm-dev.ornl.gov/api"

    blacklist = [
        "enr1_100.dpt",
        "enr1_200.dpt",
        "enr1_300.dpt",
        "enr1_400.dpt",
        "nat1_100.dpt",
        "nat1_200.dpt",
        "nat1_300.dpt",
        "nat1_400.dpt",
        "nat_ir_new.txt",
        "enr_ir_new.txt",
    ]

    upload_directories(curies_directory, group_directories, hostname, workbook, blacklist=blacklist)
