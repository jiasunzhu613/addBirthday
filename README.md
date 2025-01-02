# addBirthday.py
a simple python script that add birthdays from local text files to google calendar


<!-- TODO: 
~~- pip usage / installation~~
- supported date formats
- file formatting
- command options --> 
## System Requirements
1. Python 3.7 or higher
2. virtualenv (`pip install virtualenv`)   

## Quick Start
1. `git clone https://github.com/jiasunzhu613/addBirthday.git`
2. Set up a Google Workspace environment
    - Follow [Google's Python quick start guide](https://developers.google.com/calendar/api/quickstart/python) to set up your Google Workspace environment
3. Add the `credentials.json` file into your working directory
4. `python{version} -m venv env` to create virtual environment
5. `source env/bin/activate` to activate virtualenv
6. `pip install -r requirements.txt` to get module imports

## Usage
1. `python3 addBirthday.py [-r] -file /path/to/file` to add new birthdays or update birthdays of existing people in calendar. 
    - `-r` toggles ability to override birthdays of existing people in calendar
    - see [how to format your file to add/update birthdays](#Add/Update-Birthdays)
2. `python3 addBirthday.py -d [-file /path/to/file]`
    - If a file is included only birthdays of people with name included inside the file will be delete.
        - see [how to format your file to delete birthdays](#Delete-Birthdays)
    - If no file is included all existing birthdays will be deleted
3. `python3 addBirthday.py --logout`
    - Logs out of current user's account
    - (NOTE: it is possible to add more arguments to this command in practice but `--logout` will be prioritized and always executed first)

NOTE: whenever command 1 or 2 is used, user will be prompted to log in first if not already logged in.

### Detailed Usage and command structure
`python3 addBirthday.py [-h] [--l | -r | -d] [-f F]`

add birthdays stored locally in text files to a google calendar

optional arguments:
    -h, --help     show this help message and exit
    --l, --logout  logout of currently signed in user
    -r, -replace   Toggle ability to replace existing calendar birthdays
    -d, -delete    delete existing birthdays in calendar
    -f F, -file FILE  text file containing names and respective birthdays

`-file FILE` is only optional for `--logout` and `-delete`. When using the command alone (`python3 addBirthday.py [-r] -file /path/to/file`), `-file FILE` must be included.


## File Formatting
Currently, only `.txt` files are supported.

For birth dates, see [what birth date formats are supported](#birth-date-formats).

#### Add/Update Birthdays
Each line of the `.txt` file must follow the format 
>`{name[,name...]}: {birth date}`.

The name(s) and birth date must be separated by a colon and a space.

There may be more than one comma-separated name for the name field (however note that it is best to not include a space after the comma).

Example of valid lines of input: 
`Opi: Jan 10`
`John Doe,Jane Doe: March 19`
`Upi: Dec 19`

#### Delete Birthdays
Each line of the `.txt` is simply the name of the person's birthday you are trying to delete. 

For example if I wanted to delete `John Doe` and `Opi`, the file would look something like:
```
John Doe
Opi
```

## Birth Date Formats
Currently only 3 birth date formats are supported, all others will be considered as invalid birth dates. Birth dates follow the python datetime module [format codes](https://docs.python.org/3/library/datetime.html#format-codes).

1. `%b %d` format (3 letter month abbreviation with day; first letter of month must be capitalized)
    - e.g. Jan 1, Apr 19, Feb 25
2. `%B %d` format (month with day)
    - e.g. January 1, April 19, February 25
3. `%Y/%m/$d` format (year/month/day)
    - e.g. 2000/05/15, 2024/12/20, 2025/01/01



