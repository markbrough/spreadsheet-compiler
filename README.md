# Spreadsheet compiler

Allows users from different departments to upload one sheet that is then compiled into a single file. Each department will not be able to see the sheets of other departments. Only managers and compilers can see the full compiled file. It allows data to be uploaded and captured for multiple time periods -- currently once per week.

[Jump straight to Installation instructions below](#installation)

## Rationale
Excel is great! Very many people can use it, it's cheap and flexible to collect, manage and analyse data. However, combining data from multiple sources on a frequent basis requires a number of steps of human intervention, including:

* ensure various people are working from the same version of the file;
* sharing files via email;
* accurately copying data from each source workbook into the target workbook;
* saving, labelling and safely storing the target workbook;
* making sure all the people who should have access to this target workbook have access whenever they need it.

The aim of this tool is to simplify this process in a very light-weight way. A template file can be uploaded; users can then upload a sheet of data that will feed into that template. In this case, users don't get to see other users' data. Only those responsible for compiling the final workbook, and managers, can see the final compiled (complete) version.

Eventually, you might want to settle on a more rigid structure, validation, etc., and have the Excel file feed into that data structure (e.g. so that you can compare particular variables over time). However, particularly at the beginning of data collection, it's good to be able to play around with the format or required data and Excel is great at providing this flexibility.

## Detailed explanation
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
