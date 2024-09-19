# Auth service
***
## Python version
3.12
## Local
***
### Installation
* create a virtual environment
```bash
python -m venv .venv
```
* activate .venv
```bash
source .venv/bin/activate
```
* install requirements
```bash
pip install -r ./src/requirements/dev.txt
```
* create an .env file from the .env.example file
```bash
cp ./src/.example.env ./src/.env
```
* change variable values as needed
### Migrations
* generate new migration
```bash
make migrations m="<migration_name>"
```
* apply migrations
```bash
make migrate
```
### Testing
* run tests
```bash
make test
```


### Deploy
* use shortcut script
```bash
make local
```

## Production
***
### Deploy
* use shortcut script:
```bash
make
```

## Test and Lint

* run linters(ruff)
```bash
make lint 
```