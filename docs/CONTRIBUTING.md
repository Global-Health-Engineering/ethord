# Contribute

## Architecture

- `py/ghe_extract`: general python library using `llama_cloud_services`
  to extract JSONs from pdfs and produce a flat CSV
- `py/`: ORD specific files containing the schemas describing the
  extracted variables and the `main.py` used to execute the extraction
- `R/`: contains code to clean the flattened JSON resulting from
  extraction

## Setup

### Unzip

Place `ORD - YYYYMMDD.zip` files in `raw/` and run:

``` bash
./unzip.sh
```

The script will create `raw/ORD_files` with the following tree
structure:

    ORD files
    ├── Contribute
    │   ├── Tilley
    │   │   ├── application
    │   │   └── final report
    │   ...
    ├── Establish
    └── Explore

and containing all docs in the zip files

### Installation

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### llama cloud API key

- Get an API key here: <https://cloud.llamaindex.ai/login>

### Usage

- Save API key
  - Either as environmental variable to `LLAMA_CLOUD_API_KEY`
  - or edit `main.py` to pass through `LlamaCloudExtractor(api_key='')`
- run main code

&nbsp;

    source venv/bin/activate
    python3 py/main.py raw/ORD_files

### Work with nested dir structures

Delete files:

``` bash
find "dir" -name "*.pdf" -type f -delete
```

The command will delete all pdfs in `dir` recursively
