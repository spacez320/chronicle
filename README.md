chronicle
=========

This is an app to get some information out of Destiny 2.

It's in the toy stage and may not work well, or at all.

Usage
-----

To run the CLI:

```sh
export $(cat .env)
poetry run python main.py
```

To run the web app:

```sh
export $(cat .env)
poetry run flask --app main run --reload --extra-files chronicle/templates/*
```
