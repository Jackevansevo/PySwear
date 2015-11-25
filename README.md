#Pyswear
Web Project to count the occurrences of swear words in popular rap artists' songs

##Instructions
The website isn't currently hosted anywhere but can be viewed locally

###Requirements

####Python libraries
Install the necessary python libraries with the following command
```
pip install -r requirements.txt
```

####Bootstrap & JQuery
Use bower to install JavaScript dependencies
```
bower install
```

###Running flask to view the  site locally
Edit the artist names in artists.txt to your choosing, I've provided some
popular artists as example defaults

Then populate the database (depending on the size of your artists.txt file this
could take while)
```
python3 populate_database.py
```

Then fire up the flask server with:

```
python3 app.py
```

Then simply visit [http://127.0.0.1:5000/] (http://127.0.0.1:5000/)

---
If anyone tries this on their machine and it doesn't work please tell me and
I'll update the documentation
