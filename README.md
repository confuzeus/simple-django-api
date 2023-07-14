# Simple Django API Project Template

This template contains everything you need to bootstrap a new Django based API.

## Features

- Authentication with JWT.
- Full signup with email confirmation, login, and logout flow.
- User model and CRUD.

## Requirements

- [Poetry](https://python-poetry.org/)
- (Optional) [Docker](https://www.docker.com/)
- (Optional) [Docker Compose](https://docs.docker.com/compose/install/)

## Quick start

[Download](https://github.com/confuzeus/simple-django-api/releases) the latest release.

Or, clone the project and delete `.git` so that you can initialize your own:

```shell
rm -rf .git
git init
```

Copy the sample environment file. Then edit it as per your needs.

```shell
cp appconfig.example.env appconfig.env
```

You should also rename the project now unless you really
like the name *Simple Django*.

To rename, simply execute the script named `rename.sh`.

Bootstrap the project with make:

```shell
make
```

This will install dependencies, start the docker services, run tests,
and finally, migrate the database.

## License and Copyright

License is MIT

Copyright 2022 Josh Michael Karamuth
