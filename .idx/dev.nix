
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python311Packages.altair
    pkgs.python311Packages.asgiref
    pkgs.python311Packages.attrs
    pkgs.python311Packages.blinker
    pkgs.python311Packages.cachetools
    pkgs.python311Packages.certifi
    pkgs.python311Packages.charset-normalizer
    pkgs.python311Packages.click
    pkgs.python311Packages.colorama
    pkgs.python311Packages.django
    pkgs.python311Packages.djangorestframework
    pkgs.python311Packages.gitdb
    pkgs.python311Packages.gitpython
    pkgs.python311Packages.idna
    pkgs.python311Packages.jinja2
    pkgs.python311Packages.jsonschema
    pkgs.python311Packages.jsonschema-specifications
    pkgs.python311Packages.markupsafe
    pkgs.python311Packages.narwhals
    pkgs.python311Packages.numpy
    pkgs.python311Packages.packaging
    pkgs.python311Packages.pandas
    pkgs.python311Packages.pillow
    pkgs.python311Packages.protobuf
    pkgs.python311Packages.pyarrow
    pkgs.python311Packages.pydeck
    pkgs.python311Packages.pypdf2
    pkgs.python311Packages.python-dateutil
    pkgs.python311Packages.python-dotenv
    pkgs.python311Packages.pytz
    pkgs.python311Packages.referencing
    pkgs.python311Packages.requests
    pkgs.python311Packages.rpds-py
    pkgs.python311Packages.six
    pkgs.python311Packages.smmap
    pkgs.python311Packages.sqlparse
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.tenacity
    pkgs.python311Packages.toml
    pkgs.python311Packages.tornado
    pkgs.python311Packages.typing-extensions
    pkgs.python311Packages.tzdata
    pkgs.python311Packages.urllib3
    pkgs.python311Packages.validate-email
    pkgs.python311Packages.watchdog
    pkgs.python311Packages.whoosh
  ];
}
