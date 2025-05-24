# dojima-appstore

## About

An App Store project built on Django that focuses on providing

## Building

First, create a virtual environment for the project.

```bash
python -m venv venv
```

And activate it:

```bash
#  on Windows
venv\Scripts\activate

# on macOS and Linux
source venv/bin/activate
```

Then, install all needed dependencies by running:

```bash
pip install -r requirements.txt
```

Don't forget to set up a MySQL DB server.

You're done!

Run the app with:

```bash
python appstore/manage.py runserver
```

## Debugging

Entering the MySQL shell:

```bash
mysql -u root -p
```

Reset the DB:

```bash
DROP DATABASE appstore;
CREATE DATABASE appstore;
```