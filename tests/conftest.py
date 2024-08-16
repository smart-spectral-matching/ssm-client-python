import json
import pathlib
import pytest


from . import TEST_DATA_DIR

@pytest.fixture
def hnmr_ethanol_jcamp():
    """
    Hydrogen NMR JCAMP-DX file for ethanol
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/hnmr_spectra/ethanol_nmr.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "hnmr_ethanol.jdx")
    return p


@pytest.fixture
def infrared_ethanol_jcamp():
    """
    Infrared JCAMP-DX file for ethanol
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/ethanol.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_ethanol.jdx")
    return p


@pytest.fixture
def infrared_ethanol_compressed_jcamp():
    """
    Infrared JCAMP-DX file for ethanol using compression
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/ethanol2.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_ethanol_compressed.jdx")
    return p


@pytest.fixture
def infrared_compound_jcamp():
    """
    Infrared JCAMP-DX compound file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/example_compound_file.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_compound_file.jdx")
    return p


@pytest.fixture
def infrared_multiline_jcamp():
    """
    Infrared JCAMP-DX multiline file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/example_multiline_datasets.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_multiline_datasets.jdx")
    return p


@pytest.fixture
def mass_ethanol_jcamp():
    """
    Mass spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/mass_spectra/ethanol_ms.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "mass_ethanol.jdx")
    return p


@pytest.fixture
def neutron_emodine_jcamp():
    """
    Inelastic neutron spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/neutron_scattering_spectra/emodine.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "neutron_emodine.jdx")
    return p


@pytest.fixture
def raman_tannic_acid_jcamp():
    """
    Raman spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/raman_spectra/tannic_acid.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "raman_tannic_acid.jdx")
    return p


@pytest.fixture
def uvvis_toluene_jcamp():
    """
    UV-Visible spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/uvvis_spectra/toluene.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "uvvis_toluene.jdx")
    return p


@pytest.fixture
def raman_soddyite_rruff():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm
    Retrieved on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "rruff", "raman_soddyite.rruff")
    return p


@pytest.fixture
def scidata_nmr_jsonld():
    """
    NMR SciData JSON-LD file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/stuchalk/scidata/master/examples/nmr.jsonld
    """
    p = pathlib.Path(TEST_DATA_DIR, "scidata", "nmr.jsonld")
    return json.loads(p.read_text())


@pytest.fixture
def metazeunerite_jsonld():
    """
    Metazeunerite SciData JSON-LD file from CURIES
    """
    p = pathlib.Path(TEST_DATA_DIR, "scidata", "metazeunerite.jsonld")
    return json.loads(p.read_text())


@pytest.fixture
def metazeunerite_ssm_json():
    """
    Metazeunerite SSM JSON file from CURIES
    """
    p = pathlib.Path(TEST_DATA_DIR, "ssm_json", "metazeunerite.json")
    return json.loads(p.read_text())