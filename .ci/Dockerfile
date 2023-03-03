FROM code.ornl.gov:4567/rse/images/python-pyenv-tox:0.1.0

ARG APP=/home/app

WORKDIR $APP

COPY . $APP

RUN poetry install
