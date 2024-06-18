# ZamZam v3

## Prerequisites

1. Python 3.11+
2. Odoo 17
3. PostgreSQL (Docker is recommended for easy installation)

## Getting Started

1. Create a new python virtual environment for this project
2. Activate the virtual env you've just created
3. Install `wheel` package
```
python -m pip install wheel
```
4. Upgrade pip
```
pip install --upgrade pip
```
5. Install all packages as listed within the `requirements.txt`
```
pip install -r requirements.txt
```
6. Start PostgreSQL (it's better for using docker on this)
```
docker container run -d --name odoopg -p 5432:5432 -e POSTGRES_PASSWORD=test123 postgres:14
```
7. Entering into the `psql` command line interface
```
docker container exec -it odoopg psql -h localhost -U postgres
```
8. Subsequently execute these following commands:
```
create user odoo17;
create database odoo17;
alter user odoo17 with password 'test123';
grant all privileges on database odoo17 to odoo17;
alter user odoo17 with CREATEDB;
```
9. Run Odoo in your local machine with this command:
```
python ./odoo-bin --addons-path=addons --db_user odoo17 --db_password test123 --db_host localhost --db_port 5432
```

## Got Trouble ?

Contact [Yauri Attamimi](https://yauritux.link)