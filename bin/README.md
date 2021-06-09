# SSM Python Client Scripts

This holds scripts that use the SSM Python Client project

Table of Contents:
  - [`upload.py`](#upload.py): Script to upload the raw CURIES data to a given API URL

## upload.py

Pre-requisite steps:
  1) Create a python virtual environment and activate
    ```
    python -m venv env
    source env/bin/activate
    ```
  2) Install SSM Python Client in virtual environment + extra deps
    ```
    cd ../
    pip install .
    cd bin
    pip install openpyxl
    ```
  3) Download the CURIES directory from [SSM OneDrive](https://ornl-my.sharepoint.com/personal/o9s_ornl_gov/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fo9s%5Fornl%5Fgov%2FDocuments%2FLDRD%2FSmart%5FSpectral%5FMatching%2FSSM%5FLDRD%5FShared&FolderCTID=0x012000FFFEF3294CD90D419E96367FC98F9ED5) and put it next to this `upload.py` file
  4) Modify the `__main__` section for API hostname, directories to upload, etc.
  5) Upload CURIES data to database
    ```
    python upload.py
    ```
