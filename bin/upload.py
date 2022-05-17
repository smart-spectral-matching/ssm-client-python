import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.workbook.workbook import Workbook
import pathlib
import ssm_rest_python_client as ssm
import time
from typing import List
import warnings


def get_worksheet_data(
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


def get_filenames_to_remove(file_summary_dict: dict) -> List[str]:
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


def get_mineral_data_worksheet(curies: str, workbook: str) -> Worksheet:
    '''
    Get the mineral data workbook
    '''
    curies_path = pathlib.Path(curies)
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)
    mineral_data_worksheet = wb['Mineral Data']
    return mineral_data_worksheet


def get_functional_group_list(curies: str, workbook: str) -> list:
    '''
    Pull out the functional group list from the workbook
    '''
    # Constants
    first_functional_group_label = "U"
    last_functional_group_label = "Th"

    # Get "Mineral Data" worksheet and functional group labels from worksheet
    ws = get_mineral_data_worksheet(curies, workbook)
    labels = list(ws.values)[0]

    # Get functional group list
    start = labels.index(first_functional_group_label)
    stop = labels.index(last_functional_group_label)
    functional_group_list = labels[start:stop]

    return functional_group_list


def get_file_summary_dict(
    curies: str,
    groups: List[str],
    workbook: str
) -> dict:
    '''
    Get the file summary dict for metadata from the workbook for all of CURIES
    '''
    curies_path = pathlib.Path(curies)

    # Master workbook with additional metadata
    wb_path = curies_path / workbook
    wb = openpyxl.load_workbook(filename=wb_path, read_only=True)

    # Get the dict for the files summary worksheet
    file_summary_dict = get_worksheet_data(wb['Files Summary'], key_name=None)

    # Get the dict for the mineral data worksheet + list of functional groups
    mineral_data_dict = get_worksheet_data(
        wb['Mineral Data'],
        key_name='Mineral Name')

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


def get_formula_dict(file_summary_dict, location):
    formula = file_summary_dict[location]["Formula"]
    mineral_name = file_summary_dict[location]["Mineral Name"]
    formula_dict = {
        "@id": "compound/1/",
        "@type": "sdo:compound",
        "formula": formula,
        "name": mineral_name,
    }
    return formula_dict


def get_structure_type_dict(file_summary_dict, location):
    structure_type = file_summary_dict[location]["Structure type"]
    structure_type_dict = {
        "@id": "structuretype/1/",
        "@type": "sdo:value",
        "structure type": structure_type,
    }
    return structure_type_dict


def get_crystal_system_dict(file_summary_dict, location):
    crystal_system = file_summary_dict[location]["Crystal System"]
    crystal_system_dict = {
        "@id": "crystalsystem/1/",
        "@type": "sdo:value",
        "crystal system": crystal_system,
    }
    return crystal_system_dict


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
    formula_dict = get_formula_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
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

    # Add structure type
    structure_type_dict = get_structure_type_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    facets.append(structure_type_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    # Add crystal system
    crystal_system_dict = get_crystal_system_dict(file_summary_dict, location)
    facets = scidata_dict["@graph"]["scidata"]["system"]["facets"]
    facets.append(crystal_system_dict)
    scidata_dict["@graph"]["scidata"]["system"]["facets"] = facets

    return scidata_dict


def upload_file(
    rester: ssm.SSMRester,
    dataset_title: str,
    location: pathlib.Path,
    file_summary_dict: dict,
    curies: str,
    workbook: str
):
    print('    reading...')
    try:
        scidata_dict = get_scidata(
            location,
            file_summary_dict,
            curies,
            workbook)
    except KeyError:
        print(f'ERROR: {location} not found in file summary dict')

    # Upload file to dataset
    print('    uploading..')
    while True:
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                model = rester.model.create(scidata_dict)
                print(f'    {hostname}/datasets/{dataset_title}/models/{model.uuid}\n') # noqa
                break
            except Warning as w:
                print(f'ERROR: {w}')
                print("  Model not uploaded!!!")
                print()
                break
            except Exception as e:
                print(f' ERROR: {e}')
                print('Retrying...')
                time.sleep(5)


def upload_directories(
    curies: str,
    groups: List[str],
    hostname: str,
    workbook: str,
    limit_spectra: int = None,
    blacklist: List[str] = None,
    dataset_title: str = None
):
    """
    """
    curies_path = pathlib.Path(curies)

    # Black list of files that are not in RRUFF file format
    if not blacklist:
        blacklist = []

    # Create rest client
    rester = ssm.SSMRester(hostname=hostname)

    # Setup dataset
    if dataset_title:
        dataset = rester.dataset.get_by_title(dataset_title)
    else:
        dataset = rester.dataset.create("curies")

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

        print(f'  Dataset URI: {hostname}/datasets/{dataset.title}')
        print(f'  Number of spectra: {total_group_spectra}\n')

        # Loop over spectra for the directory
        for i, location in enumerate(locations):
            print(f'  {location.name} {i+1} of {total_group_spectra}')

            # Skip non-RRUFF files for now
            if location.name in blacklist or str(location) in blacklist:
                print(f'    {location.name} skipped... ***')
                continue

            upload_file(
                rester,
                dataset.title,
                location,
                file_summary_dict,
                curies,
                workbook)


if __name__ == "__main__":
    curies_directory = "CURIES"
    group_directories = [
        "Arsenates",
        "Carbonates",
        "Hydroxides",
        "Phosphates",
        "Silicates",
        "Sulfates",
        "Other U Minerals",
        "Vanadates",
        # "U Oxides",
    ]
    workbook = "Master.xlsx"

    # Select hostnames
    local_hostname = "http://localhost:8080/api"
    dev_hostname = "http://ssm-dev.ornl.gov/api"
    qa_hostname = "http://ssm-qa.ornl.gov/api"

    hostname = dev_hostname

    # Put together blacklist
    bad_format_files = [
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
    new_sulfates_bad_format = [
        "ammoniomathesiusite_R_785.txt",
        "ammoniozippeite1_R_785.txt",
        "ammoniozippeite2_R_785.txt",
        "ammoniozippeite3_R_785.txt",
        "ammoniozippeite4_R_785.txt",
        "belakovskiite1_R_785.txt",
        "belakovskiite2_R_785.txt",
        "bluelizardite1_R_785.txt",
        "bluelizardite2_R_785.txt",
        "CoZippeite1_R_532.txt",
        "CoZippeite1_R_785.txt",
        "CoZippeite2_R_785.txt",
        "CoZippeite3_R_785.txt",
        "fermiite_R_785.txt",
        "johannite1_R_785.txt",
        "johannite2_R_785.txt",
        "lussierite_R_785.txt",
        "marecottite1_R_785.txt",
        "marecottite2_R_785.txt",
        "meisserite1_R_785.txt",
        "messierite_R_532.txt",
        "natrozippeiteBlueLizard1_R_785.txt",
        "natrozippeiteBlueLizard2_R_785.txt",
        "natrozippeiteBlueLizard3_R_785.txt",
        "natrozippeiteBlueLizard4_R_785.txt",
        "natrozippeiteBlueLizard5_R_785.txt",
        "natrozippeiteBurro_R_785.txt",
        "natrozippeiteMarkey1_R_785.txt",
        "natrozippeiteMarkey2_R_785.txt",
        "navrotskyite1_R_785.txt",
        "navrotskyite2_R_785.txt",
        "plasilite1_R_785.txt",
        "plasilite2_R_785.txt",
        "reitveldite_R_785.txt",
        "uranopilite_R_785.txt",
        "ZnZippeite1_R_785.txt",
        "ZnZippeite2_R_785.txt",
        "ZnZippeite3_R_785.txt",
    ]
    ir_spectra_files = [
        "curienite_IR.txt",
        "finchite_IR.txt",
        "metaautunite1_IR.txt",
        "metatorbernite1_IR.txt",
        "schrockingerite1_IR.txt",
        "sklodowskite_IR.txt",
        "vanuralite_IR.txt",
    ]
    duplicate_files = [
        curies_directory + "/Carbonates/Spectra/schrockingerite1_R_780.txt",
        curies_directory + "/Carbonates/Spectra/schrockingerite2_R_780.txt",
        curies_directory + "/Carbonates/Spectra/schrockingerite1_R_532.txt",
        curies_directory + "/Carbonates/Spectra/schrockingerite2_R_532.txt",
        curies_directory + "/Phosphates/Spectra/coconinoite_R_532.txt",
        curies_directory + "/Phosphates/Spectra/coconinoite_R_785.txt",
        curies_directory + "/Vanadates/Spectra/ammoniomathesiusite_R_532.txt",
        curies_directory + "/Vanadates/Spectra/ammoniomathesiusite_R_780.txt",
    ]

    # Create aggregated blacklist of files
    blacklist = list()
    blacklist += bad_format_files
    blacklist += ir_spectra_files
    blacklist += duplicate_files
    blacklist += new_sulfates_bad_format

    # Upload CURIES
    upload_directories(
        curies_directory,
        group_directories,
        hostname,
        workbook,
        blacklist=blacklist)
