# [Eve](http://python-eve.org/)  

This repo is related with `Running Guide` `Part 2.5`

[MongoDB](https://www.mongodb.com/) is used as the database. To operate it, we use the REST API framework Eve to offer support for MongoDB. 

The code offered is very simple, running on port `5000`, without auth.

## File Tree

```txt
Eve_MongoDB/
├── __init__.py
├── mongo_eve.py
├── README.md
├── requirements.txt
└── settings.py

0 directories, 5 files
```

**mongo_eve.py**

The script for starting Eve.

**settings.py**

The setting of Eve. In this setting, we set the following parameters:

- Port of MongoDB: `27017` (Default)
- DB to be connected: `db_faas_bot`
- HTTP method allowed for Resource (Collection) and Item (Document)
- Two unconstraint collection: `product_info` and `session_info`

## Dependencies

```sh
$ pip install eve
```

or

```sh
$ pip install -r requirements.txt
```

### How to Run

To start the Eve,  use: 

```bash
$ python mongo_eve.py
```

