#!/usr/bin/python
# Author:yue.zhang@houzz.com
import sys
import subprocess
import ast
import json 
import re
import datetime
import base64
import calendar



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

def get_lines_changed_commit(rev):
	count = 0 
	stat = subprocess.check_output("git diff --numstat "+rev+"^ "+rev,shell=True).decode('utf-8').splitlines()
	for line in stat:
		try:
			count += int(re.search(r'\d+', line).group())
		except Exception as e:
			print("Error occur when counting lines changed")
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

def edit_last_commit_msg(lines_changed,commit):
    time = datetime.datetime.utcnow()
    unixtime = calendar.timegm(time.utctimetuple())
    print(unixtime)
    enc  = encode(str(unixtime),"commit")
    ori_msg = get_commit_message(commit)
    new_msg = ori_msg+"\nlineschanged:"+str(lines_changed)+"\n"+"encryption:"+enc
    subprocess.check_output("git commit --amend -m \""+new_msg+"\"",shell=True)

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))
