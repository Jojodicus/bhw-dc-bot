#!/bin/sh
uvx ruff check --select I --fix
uvx ruff format
