# Altspell

Flask web app for converting traditional English spelling to an alternative spelling.

## Quick Start

Execute the following commands to get the web API up and running:

```sh
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install main program
pip install git+https://github.com/njohnson-oss/altspell

# Install plugin dependency
pip install git+https://github.com/njohnson-oss/nlp-provider

# Install a few plugins
pip install git+https://github.com/njohnson-oss/altspell-lytspel  \
            git+https://github.com/njohnson-oss/altspell-portul  \
            git+https://github.com/njohnson-oss/altspell-universal-lojikl-inglish

# Start web API
flask --app altspell run
```

Example HTTP requests:

```sh
# List plugins
curl -X GET -H "Accept: application/json" http://127.0.0.1:5000/api/plugins

# Perform forward conversion and save the result in the database
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" -d  '{
    "tradspell_text": "Hello, world!",
    "altspelling": "lytspel",
    "to_altspell": true,
    "save": true
}' http://127.0.0.1:5000/api/conversions

# Retrieve the saved result from the database
# conversion_id comes from the HTTP response of the previous command
curl -X GET -H "Accept: application/json" http://127.0.0.1:5000/api/conversions/{conversion_id}
```
