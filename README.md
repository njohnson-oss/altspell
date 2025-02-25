# Altspell

Flask web app for translating traditional English to respelled English and vice versa.

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
# List available spelling systems
curl -X GET -H "Accept: application/json" http://127.0.0.1:5000/api/spelling-systems

# Perform forward translation and save the result in the database
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" -d  '{
    "text": "Hello, world!",
    "spellingSystem": "lytspel",
    "forward": true,
    "save": true
}' http://127.0.0.1:5000/api/translations

# Retrieve the saved result from the database
# translation_id comes from the HTTP response of the previous command
curl -X GET -H "Accept: application/json" http://127.0.0.1:5000/api/translations/{translation_id}
```
