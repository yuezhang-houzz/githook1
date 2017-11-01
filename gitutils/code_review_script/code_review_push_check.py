#!/usr/bin/python
# Author:yue.zhang@houzz.com

import sys
import subprocess
import ast
import json 
import re
import utils_code_review as utils 

pre_push_alert="""
===========================================================================
You're unable to push because you need approval for code review.
There are certain scenarios needs that:
---Changed over 200 lines in master branch.
---Making changes directly in Release branch.\n
In case of emergency,you can use "--no-verify" option to bypass code review,
yet all team leads will be notified.
===========================================================================
"""

def arc_installed_check():
	if "not" in subprocess.check_output("arc --version",shell=True).decode('utf-8'):
		sys.exit(1)

def return_to_shell(lines_changed,local_sha,need_approval,git_branch):
	if need_approval:
		print(pre_push_alert)
		sys.exit(1)
	else:
		utils.edit_last_commit_msg(lines_changed,local_sha)
		print("Great job! Your code review was accepted and it can now be pushed to "+git_branch+" :) ")

def check_if_needApproval(over_200_lines,ids):
	need_approval = False
	if over_200_lines:
		if len(ids) == 0: return True	
		result = json.loads(utils.check_code_reviews_apicall(ids))
		for code_review in result["response"]:
			need_approval |= code_review["statusName"] != "Accepted"
	return need_approval
	

if __name__ == '__main__':
	arc_installed_check()

	need_approval  = False
	over_200_lines = False
	MAX_LINES  	   = 200

	git_branch = utils.get_git_branch_name()
	local_sha  = utils.get_git_revision_hash()
	remote_sha = utils.get_git_remote_revision_hash(git_branch.rstrip())

	revs_list 		= utils.get_unpushed_commits(remote_sha.rstrip(),local_sha.rstrip()).splitlines()
	ids 			= utils.get_review_ids_from_msg(revs_list)
	lines_changed 	= utils.get_total_lines_changed(revs_list)

	if lines_changed >= MAX_LINES: over_200_lines = True

	if "master" in git_branch:
		need_approval = check_if_needApproval(over_200_lines,ids)
	elif "Release" in git_branch:
		need_approval = check_if_needApproval(True,ids)

	return_to_shell(lines_changed,local_sha,need_approval,git_branch)


