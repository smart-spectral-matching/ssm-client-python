import pathlib
import ssm_client as ssm
import time
from typing import List
import warnings

import metadata


def upload_file(
    rester: ssm.SSMRester,
    collection_title: str,
    location: pathlib.Path,
    file_summary_dict: dict,
    curies: str,
    workbook: str,
):
    print("    reading...")
    try:
        scidata_dict = metadata.get_scidata(
            location, file_summary_dict, curies, workbook
        )
    except KeyError:
        print(f"ERROR: {location} not found in file summary dict")

    # Upload file to dataset
    print("    uploading..")
    while True:
        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                dataset = rester.dataset.create(scidata_dict)
                print(
                    f"    {hostname}/collections/{collection_title}/datasets/{dataset.uuid}\n"
                )  # noqa
                break
            except Warning as w:
                print(f"ERROR: {w}")
                print("  dataset not uploaded!!!")
                print()
                break
            except Exception as e:
                print(f" ERROR: {e}")
                print("Retrying...")
                time.sleep(5)


def upload_directories(
    curies: str,
    groups: List[str],
    hostname: str,
    workbook: str,
    limit_spectra: int = None,
    blacklist: List[str] = None,
    collection_title: str = None,
):
    """ """
    curies_path = pathlib.Path(curies)

    # Black list of files that are not in RRUFF file format
    if not blacklist:
        blacklist = []

    # Create rest client
    rester = ssm.SSMRester(hostname=hostname)

    # Setup dataset
    if collection_title:
        collection = rester.collection.get_by_title(collection_title)
    else:
        collection = rester.collection.create("curies")

    # Get file summary dict
    file_summary_dict = metadata.get_file_summary_dict(curies, workbook)

    # Loop over directories
    total_spectra = 0
    for directory in groups:
        print(f"***********\n{directory}\n***********")

        # Create dataset in database to hold directory data
        rester.initialize_dataset_for_collection(collection)

        # Glob the spectra file paths
        directory = pathlib.Path(curies_path, directory, "Spectra")
        locations = directory.glob("*.txt")

        # Tally up total spectra for group and overall
        total_group_spectra = len(list(locations))
        total_spectra += total_group_spectra
        locations = directory.glob("*.txt")

        if limit_spectra:
            locations = list(locations)[0:limit_spectra]

        print(f"  Collection URI: {hostname}/collections/{collection.title}")
        print(f"  Number of spectra: {total_group_spectra}\n")

        # Loop over spectra for the directory
        for i, location in enumerate(locations):
            print(f"  {location.name} {i+1} of {total_group_spectra}")

            # Skip non-RRUFF files for now
            if location.name in blacklist or str(location) in blacklist:
                print(f"    {location.name} skipped... ***")
                continue

            upload_file(
                rester,
                collection.title,
                location,
                file_summary_dict,
                curies,
                workbook,
            )


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
    group_directories = ["Phosphates"]
    workbook = "Master.xlsx"

    # Select hostnames
    local_hostname = "http://localhost:8080/catalog/api"
    dev_hostname = "http://ssm-dev.ornl.gov:8080/api"
    qa_hostname = "http://ssm-qa.ornl.gov/api"

    hostname = local_hostname

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
        blacklist=blacklist,
        collection_title = "phosphates"
    )
