# Column Types - /dtable-server vs /api-gateway

Note: Everything in this document was tested against v5.0 on stage.seatable.io

## Changes from v4.4 to v5.0
- `getRow` and `listRows` return column IDs **by default** -> `convert_keys` needs to be set to `true` to keep the existing behavior
    - The default value of `convert_keys` should be specified in the API specification
- `getRow` and `listRows` always return `date` columns in ISO format with TZ information (good, but a breaking change to keep in mind!)
