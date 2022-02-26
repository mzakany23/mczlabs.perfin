#!/bin/bash

function ensure_poetry() {
	POETRY=$(which poetry)
	if ! [ $POETRY ]; then
		curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
		source $HOME/.poetry/env
		poetry config virtualenvs.in-project true
	else
		echo "poetry already installed"
	fi
}
