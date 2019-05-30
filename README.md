# Spreadsheet compiler

Allows users from different departments to upload one sheet that is then compiled into a single file. Each department will not be able to see the sheets of other departments. Only managers and compilers can see the full compiled file. It allows data to be uploaded and captured for multiple time periods -- currently once per week.

There are three roles:

* **user**: can upload files contributing to the main template
* **compiler**: can upload a spreadsheet template, see all users' uploaded files and draft files throughout the course of data collection (i.e. during the week), as well as previous weeks' final compliled files
* **manager**: can see finalised compiled files for previous weeks.

Uploading users have to be assigned to a particular user group. That user group has to have the same name as the name of the sheet they should edit in the spreadsheet template.

For example:
* the **compiler** uploads a template with three sheets: `SUMMARY`, `DEPARTMENT A`, `DEPARTMENT B` (`SUMMARY` contains data imported from the other two sheets)
* the **compiler** creates _user groups_ for `DEPARTMENT A` and `DEPARTMENT B`
* the compiler creates users `Bob` who works in `DEPARTMENT A` and `Kate` who works in `DEPARTMENT B`
* user `Bob` downloads this template. He sees only the sheet named `DEPARTMENT A`. Bob edits the file, and then uploads again.
* user `Kate` does the same for her department.
* Bob and Kate cannot see each others' sheets.
* the **compiler** can see that both Bob and Kate have uploaded their files on time
* the **compiler** then downloads the compiled version of the template. The sheet `DEPARTMENT A` has been updated with the data that Bob uploaded, and the sheet `DEPARTMENT B` has been updated with the data that Kate entered.
* the following Monday morning, the **manager** logs in and can see the compiled version from the previous week.


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
