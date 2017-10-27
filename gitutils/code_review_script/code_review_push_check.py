#!/usr/bin/python
# Author:yue.zhang@houzz.com
import sys
import subprocess
import ast
import json 
import re
import base64

def arc_installed_check():
	result = subprocess.check_output("arc --version",shell=True).decode('utf-8')
	print (result)
	if "not" in result:
		sys.exit(1)

def get_git_revision_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')

def get_git_remote_revision_hash(branch):
    return subprocess.check_output(['git', 'rev-parse', 'origin/'+branch]).decode('utf-8')

def get_git_revision_short_hash():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8')

def get_git_branch_name():
	return subprocess.check_output(["git", "rev-parse","--abbrev-ref","HEAD"]).decode('utf-8')

def get_unpushed_commits(remote_sha,local_sha):
	return subprocess.check_output(["git", "rev-list",remote_sha+".."+local_sha]).decode('utf-8')

def get_lines_changed_commit(rev):
	count = 0 
	stat = subprocess.check_output("git diff --numstat "+rev+"^ "+rev,shell=True).decode('utf-8').splitlines()
	for line in stat:
		count += int(re.search(r'\d+', line).group())
	return count

def get_commit_message(rev):
	return subprocess.check_output("git log --format=%B -n 1 "+rev,shell=True).decode('utf-8')

def check_code_reviews_apicall(ids):
	json = "{\"ids\":"+str(ids)+"}"
	return subprocess.check_output("echo '"+json+"\' | arc call-conduit --conduit-uri https://cr.houzz.net/ differential.query",shell=True)

def get_review_ids_from_msg(revs_list):
	ids = []
	for rev in revs_list:
		for line in get_commit_message(rev).splitlines():
			if "Differential Revision:" in line:
				ID =  line[-4:]
				ids.append(int(ID))
	return ids

def get_total_lines_changed(revs_list):
	lines_changed = 0
	for rev in revs_list:
		line = get_lines_changed_commit(rev)
		if line is not None:
			lines_changed = lines_changed + int(line)
	
	return lines_changed
	
def edit_last_commit_msg(lines_changed,commit):
	time = get_git_commit_time(commit)
	print(time)
	enc  = encode(time,commit)
	ori_msg = get_commit_message(commit)
	new_msg = "\nlineschanged:"+str(lines_changed)+"\n"+"encryption:"+enc
	subprocess.check_output("git commit --amend -m \""+new_msg+"\"",shell=True)

def get_git_commit_time(commit):
	return subprocess.check_output("git rev-list --format=format:'%at' --max-count=1 `git rev-parse HEAD`",shell=True).decode('utf-8')

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def check_if_needApproval(over_500_lines,ids):
	need_approval = False
	if over_500_lines:
		if len(ids) == 0: return True	
		result = json.loads(check_code_reviews_apicall(ids))
		for code_review in result["response"]:
			need_approval |= code_review["statusName"] != "Accepted"
	return need_approval

def return_to_shell(need_approval,git_branch):
	if need_approval:
		print("Needs approval for code review.")
		sys.exit(1)
	else:
		print("Great job! Your code review was accepted and it can now be pushed to "+git_branch+" :) ")
	
	

if __name__ == '__main__':
	arc_installed_check()

	need_approval  = False
	over_500_lines = False
	MAX_LINES  	   = 100

	git_branch = get_git_branch_name()
	local_sha  = get_git_revision_hash()
	remote_sha = get_git_remote_revision_hash(git_branch.rstrip())

	revs_list 		= get_unpushed_commits(remote_sha.rstrip(),local_sha.rstrip()).splitlines()
	ids 			= get_review_ids_from_msg(revs_list)
	lines_changed 	= get_total_lines_changed(revs_list)

	if lines_changed >= MAX_LINES: over_500_lines = True
	edit_last_commit_msg(lines_changed,local_sha)
	if "master" in git_branch:
		need_approval = check_if_needApproval(over_500_lines,ids)
	elif "Release" in git_branch:
		print("You are trying to push code directly to Release branch.")
		need_approval = check_if_needApproval(True,ids)

	return_to_shell(need_approval,git_branch)


