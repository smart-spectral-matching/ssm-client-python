FROM code.ornl.gov:4567/rse/docker-containers/docker-pyenv-tox/master

ARG APP=/home/app

WORKDIR $APP

COPY . $APP

RUN pipenv install --dev
