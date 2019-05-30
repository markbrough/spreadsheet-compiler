# Spreadsheet compiler

Allows users from different departments to upload one sheet that is then compiled into a single file. Each department will not be able to see the sheets of other departments. Only managers and compilers can see the full compiled file.

## Installation

1. Get the repository, set up a virtualenv and install requirements:
   ```
   git clone git@github.com:markbrough/spreadsheet-compiler.git
   cd spreadsheet-compiler
   virtualenv -p python3 ./pyenv
   source ./pyenv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy and edit config.py:
   ```
   cp config.py.tmpl config.py
   ```

3. Setup the database:
   ```
   flask db upgrade
   ```

4. Start the server:
   ```
   flask run
   ```
