# reference tutorial: http://docs.fabfile.org/en/1.12/tutorial.html

from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
import os

def static_analysis():
	# ignore error from static analysis so files can be pushed to git
	try:
		local("pylint app.py >> static_analysis.txt")
	except:
		pass

def commit():
	local("git add -u && git add static_analysis.txt")
	local("git commit")

def push():
	local("git push")

def tests():
	local("python test.py")

def prepare_deploy():
	static_analysis()
	tests()
	commit()
	push()
	local("sudo pip install passlib")
	local("sudo pip install git+https://github.com/pymssql/pymssql.git")

# start server for web app
def deploy():
    with cd(os.getcwd()):
        local("git pull")
        local("python app.py")



