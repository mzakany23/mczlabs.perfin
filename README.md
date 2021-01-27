
# Perfin

[![CircleCI](https://circleci.com/gh/mzakany23/mczlabs.perfin.svg?style=svg&circle-token=7cf7c24bd0574883c1c2a0abf849736a1126395f)](https://circleci.com/gh/mzakany23/mczlabs.perfin)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Personal Finance Transaction Management.

This repo aims to aid in the munging, ingestion, and viewing of personal finance transactions gathered through bank csv report exports.

It originally used plaid for data pipe but I've found working with csv's more reliable.

**Github Project Board**
https://github.com/mzakany23/mczlabs.perfin/projects/2

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

## Deploy to aws

Deploy an elastcsearch cluster on aws. Make sure you have a terraform_perfin aws user (or change this in makefile). Always run terraform commands using the makefile so you don't accidentally use the wrong aws profile.

**setup and apply**
```bash
make terraform_init
make terraform_plan
make terraform_apply
```

**destroy**
```bash
make terraform_destroy
```

## How to upload files

1. Log into your bank and get csv transaction exports
2. Save/drop the files on your desktop
3. Make sure config/accounts.json is updated
4. Turn on local ingestion (make run CMD=start)
5. run the upload command (e.g. make run CMD=upload)


## Stack

- python3.7+
- elasticsearch/kibana 7.10.2 (database and visualization)
- Amazon Web Services managed es cluster built with https://github.com/cloudposse/terraform-aws-vpc  terraform modules
- Sentry (bug reporting)
- Circle ci (tests and deploy automation)
- Local development (docker/docker-compose)


## Tests


```bash
make test
```
