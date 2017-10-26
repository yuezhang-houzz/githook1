#!/usr/bin/python
# Author:yue.zhang@houzz.com
import sys
import subprocess
import ast
import json 
import re

def get_lines_changed_commit(rev):
	count = 0 
	stat = subprocess.check_output("git diff --numstat "+rev+"^ "+rev,shell=True).decode('utf-8').splitlines()
	for line in stat:
		count += int(re.search(r'\d+', line).group())
	return count

def get_git_branch_name():
	return subprocess.check_output(["git", "rev-parse","--abbrev-ref","HEAD"]).decode('utf-8')

def get_git_remote_revision_hash(branch):
    return subprocess.check_output(['git', 'rev-parse', 'origin/'+branch]).decode('utf-8')

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')

def get_unpushed_commits(remote_sha,local_sha):
	return subprocess.check_output(["git", "rev-list",remote_sha+".."+local_sha]).decode('utf-8')

def get_total_lines_changed(revs_list):
	lines_changed = 0
	for rev in revs_list:
		line = get_lines_changed_commit(rev)
		if line is not None:
			lines_changed = lines_changed + int(line)
	return lines_changed

def commit_to_Release_alert():
	alert = """\n
	Hi,you are committing changes directly on Release branch,
	a code review is required before push.
	1.If you haven't install the code review tool Arcanist,please go
	to : https://cr.houzz.net/w/dev-introduction/workflow/
	2.Then you can type 'arc diff' command to request a code review.
	Only after your review is approved then you can push code.
	3.Finally, you are able to push your commits.\n
	"""
	print (alert)

def commit_to_master_alert():
	alert = """\n
	Hi,as your total changes of current commit is over 500 lines,
	a code review is required before push.
	1.If you haven't install the code review tool Arcanist,please go
	to : https://cr.houzz.net/w/dev-introduction/workflow/
	2.Then you can type 'arc diff' command to request a code review.
	Only after your review is approved then you can push code.
	3.Finally, you are able to push your commits.\n
	"""
	print (alert)

if __name__ == '__main__':
	MAX_LINES  = 100

	git_branch = get_git_branch_name()

	if "master" in git_branch:
		local_sha  = get_git_revision_hash()
		remote_sha = get_git_remote_revision_hash(git_branch.rstrip())
		revs_list 		= get_unpushed_commits(remote_sha.rstrip(),local_sha.rstrip()).splitlines()
		lines_changed 	= get_total_lines_changed(revs_list)
		print (lines_changed)
		if lines_changed >= MAX_LINES:
			commit_to_master_alert()
	elif "Release" in git_branch:
		print("You are trying to commit code at Release branch.")
		commit_to_Release_alert()




	















