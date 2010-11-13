googlecode2github
=================

googlecode2github is a project designed to facilitate migrating a Google Code project to GitHub.

Dependencies
------------
The GData Python client: [http://code.google.com/p/gdata-python-client/downloads/list](http://code.google.com/p/gdata-python-client/downloads/list)

The python-github2 client: [https://github.com/ask/python-github2](https://github.com/ask/python-github2)

Usage
-----

The issue-transfer.py script transfers issues from Google Code to GitHub.

If you were transferring issues from a Google Code project named foobar1 to a GitHub project named foobar2, and your username is zippy, you would run the script like this:

	$ python issue-transfer.py 
		--google_username=zippy@gmail.com
		--google_project=foobar1
		--github_username=zippy
		--github_project=zippy/foobar2
		--github_api_token=4a9e[...]23b1

You will be prompted for your Google password so as not to require it on the command line and leave it in your .bash_history.

I've successfully migrated issues from 17 Google Code projects to GitHub with this script, but as always, proceed with caution. [Here](https://github.com/cfinke/TwitterBar/issues#issue/16) is an example of an issue (with comments) that was migrated with the script.