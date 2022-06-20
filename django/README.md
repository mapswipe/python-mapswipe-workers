## Host (Optional)

### Virtualenv setup
Install pyenv https://github.com/pyenv/pyenv and setup your system.
```
# Install the used python version if not already
pyenv install $(cat .python-version)

poetry install
# For psycopg2, install dependencies (For arch: https://github.com/archlinux/svntogit-community/blob/packages/python-psycopg2/trunk/PKGBUILD)
```


### Adding new app in django
```
poetry shell
django-admin startapp <app-name>
```


### Adding dependencies.
```
poetry add package
```
