# Local conversion workbench

Run from the repository root:

```sh
.venv/bin/uvicorn crosswalk_api.app:create_app --factory --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001/workspace/ and choose **Try a claims example**.
Review the five mappings, then select **Run conversion**. The inspector shows
each original record beside its converted result. Download the converted JSON
or a standalone Python adapter that runs on other records of the same shape:

```sh
python adapter.py < records.json > converted.json
```

For your own integration, paste or load an array of source records and one
example object in your desired target format. No OpenAPI file is required.
The target example establishes field names and JSON types, not business rules
or allowed enum values. All fields start as required; unchecking Required allows
missing fields to be omitted and nulls to pass through. Explicitly omit any
target you do not want in the output.

Name matches are suggestions that must be reviewed. Conversion choices include
copy, text, number, integer without rounding, cents to dollars, and explicit
ISO, US, or day-first date formats. Nested object paths use JSON Pointer escaping.
Arrays copy as a whole; array item transformations are not supported.

The preview supports 200 records, 100 distinct source fields, 100 target fields,
and 800 KB of data. Numeric values must fit within JavaScript’s safe range;
encode large IDs as strings. Numbers use JSON numeric representation, not
arbitrary-precision financial arithmetic. Invalid records show field errors
and block both downloads until fixed. Editing any mapping clears its review
and invalidates the preview. The exported adapter shares the preview runtime
and exits unsuccessfully without writing output if a record fails.

**Save mapping** downloads target examples and rules, without source records.
Use **Open saved mapping**, add source records, and set up the mapping to restore
the rules. Review them against the new data before running. Reloading clears
the tab. No data is stored in localStorage or sent to a model provider.

No frontend build, CDN, font service, or model provider is needed. The Python
API serves the HTML, CSS, and JavaScript on the same origin. This is a local
tool, without customer authentication, hosted project storage, or live API connections.

The existing `/workbench/analyze` OpenAPI and `/reviews` APIs remain available;
the conversion screen uses `/workbench/conversion/suggest`, `/preview`, and `/export`.
