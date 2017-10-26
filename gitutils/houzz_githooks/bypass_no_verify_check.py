#!/usr/bin/python
# Author:yue.zhang@houzz.com

import sys
import subprocess
import ast
import json 
import re
 


def get_git_branch_name():
	return subprocess.check_output(["git", "rev-parse","--abbrev-ref","HEAD"]).decode('utf-8')

def get_git_revision_hash():
	return subprocess.check_output("git log -0 --pretty='%H%n%ci' | head -1",shell=True).decode('utf-8')
	
def get_commit_time():
	return subprocess.check_output("git log -1 --pretty='%H%n%ci' | head -2 | tail -1",shell=True).decode('utf-8')

if __name__ == '__main__':
	branch_name = get_git_branch_name()
	commit_hash = get_git_revision_hash()
	commit_time = get_commit_time()

	print(branch_name)
	print(commit_hash)
	print(commit_time)


