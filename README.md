# Perfin

Personal Finance Transaction Management.

This repo aims to aid in the munging, ingestion, and viewing of personal finance transactions gathered through bank csv report exports.

It originally used plaid for data pipe but I've found working with csv's more reliable (working with source vs. middleman).


## TODO

[ ] make deployment env (terraform/aws/digitalocean/azure)
[ ] setup circleci
[ ] setup sentry
[ ] document build commands/images etc
[ ] github project
[x] local development/ingesting
[ ] pypi cli package
[x] tests/setup


## Steps

1. Get transaction exports
2. Drop the files on the desktop
3. Set account names in the config/accounts.json
4. Turn on local ingestion
5. run the upload


## Stack

- python3.7
- elasticsearch/kibana 7.10.2 (database and visualization)
- aws/ec2 micro (free tier? or Digitalocean) running elasticsearch/kibana
- Sentry (bug reporting)
- Circle ci (tests and deploy automation)
- Local development (docker/docker-compose)


## Quick Start

Assuming osx >= 10.13.4 and docker is installed.

```bash
# setup virtualenv
make .venv

# start elasticsearch/kibana
make start

# assuming you have transactions downloaded locally and have set config/accounts.json
make cli CMD=upload

# go to kibana and make some charts
open http://localhost:5601
```


## Tests


```bash
make test
```
