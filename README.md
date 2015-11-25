#Pyswear
Web Project to count the occurrences of swear words in popular rap artists' songs

View a live demo of the website at [pyswear.herokuapp.com](pyswear.herokuapp.com)

## Building and Running Project Locally
This project was built in Python3 so may not be 100% backwards compatible with older versions. To install Python3 see: (https://www.python.org/downloads/)

## Installing Requirements
If you don't want to make a mess of your local Python installation I recommend
using [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)

To install virtualenv

    sudo -H pip3 install virtualenv

To create a virtual environment (in the folder you cloned)

    virtualenv venv --python=`which python3`

To activate the virtual environment

    source venv/bin/activate

To automatically install all the python requirements simply run

    pip install -r requirements.txt

To host the site locally run:

    python3 app.py

Then simply visit [http://127.0.0.1:5000/] (http://127.0.0.1:5000/)


## Modifying the artist database

To change which artists are displayed on the website simply alter the names in
**artists.txt**

Then repopulate the database with the new artists by running

    python3 populate_database.py -v
