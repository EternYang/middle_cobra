# COBRA CRM

## Porject Structure
| directory | description |
|--|--|
| api/ | Django Backend API Services |
| web/ | React Frontend Web Client |
| docs/ | API Documentation with [Slate](https://github.com/lord/slate) |

## Setup Local Env

### Backend
> Using pyenv
- Download and setup [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- Change directory `cd api/`
- Setup pyenv: `pyenv virtualenv 3.6.4 cobra && pyenv local cobra`
> Using virtualenv
- Download and setup [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- Change directory `cd api/`
- Setup virtualenv: `virtualenv --python=python3.6 .cobraenv && source .cobraenv/bin/activate`
> Installing dependencies && run server
- Install dependencies: `pip install -r requirements/dev.txt`
- Migrate database: `./manage.py makemigrations` and then `./manage.py migrate`
- Run server: `./manage.py runserver`

> Using PyCharm
- [Adding Existing Virtual Environment](https://www.jetbrains.com/help/pycharm-edu/adding-existing-virtual-environment.html)

### Fronend
- Change directory: `cd web`
- Install and run server: `yarn && yarn start`
