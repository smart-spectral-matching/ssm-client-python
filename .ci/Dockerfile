FROM code.ornl.gov:4567/rse/images/python-pyenv-tox:0.0.1

ARG APP=/home/app

WORKDIR $APP

COPY . $APP

RUN pipenv install --dev
