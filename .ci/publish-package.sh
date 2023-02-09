#!/bin/bash

USERNAME=$1
TOKEN=$2
PROJECT_ID=4557

poetry build
poetry config repositories.code "https://code.ornl.gov/api/v4/projects/$PROJECT_ID/packages/pypi"
poetry config http-basic.code "$USERNAME" "$TOKEN"
poetry publish --repository code


