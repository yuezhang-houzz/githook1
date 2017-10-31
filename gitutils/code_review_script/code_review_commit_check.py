#!/usr/bin/python
# Author:yue.zhang@houzz.com
import sys
import subprocess
import ast
import json 
import re
import utils_code_review as utils 


def commit_to_Release_alert():
	alert = """
Hi,you are committing changes directly to Release branch,a code review is required before push.
1.If you haven't install the code review tool Arcanist,please follow link: https://cr.houzz.net/w/dev-introduction/workflow/ to install it.
2.Then type 'arc diff' command to request a code review.
3.After your review is approved then you are able to push code.
	"""
	print (alert)

def commit_to_master_alert():
	alert = """
Hi,as your total changes of current commit is over 500 lines,
a code review is required before push.
1.If you haven't install the code review tool Arcanist,please follow link: https://cr.houzz.net/w/dev-introduction/workflow/ to install it.
2.Then type 'arc diff' command to request a code review.
3.After your review is approved then you are able to push code.
	"""
	print (alert)

if __name__ == '__main__':
	MAX_LINES  = 200

	git_branch = utils.get_git_branch_name()

	if "master" in git_branch:
		local_sha  = utils.get_git_revision_hash()
		remote_sha = utils.get_git_remote_revision_hash(git_branch.rstrip())
		revs_list 		= utils.get_unpushed_commits(remote_sha.rstrip(),local_sha.rstrip()).splitlines()
		lines_changed 	= utils.get_total_lines_changed(revs_list)
		print ("lines changed : "+str(lines_changed))
		if lines_changed >= MAX_LINES:
			commit_to_master_alert()
	elif "Release" in git_branch:
		commit_to_Release_alert()




	















