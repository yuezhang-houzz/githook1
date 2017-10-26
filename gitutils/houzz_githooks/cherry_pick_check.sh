#!/bin/sh

if ! git branch |grep '* Release' &> /dev/null ; then
    # Apply the hook only on the Release branch.
    git lfs pre-push "$@"
    exit 0;
fi

function error_exit() {
    cat >&2 <<\EOF
Only merges and cherry picks from the master branch are allowed. Follow these steps to create an acceptable cherry pick:
1. Push your commit to the master branch.
2. Check out the Release branch, and do "git cherry-pick -x <commit hash in master>". Do not omit the "-x" option.
3. Push the cherry pick to the Release branch.
Contact the release manager if you need to make an exception.
EOF
    exit 1;
}

cherry='cherry picked from commit'

while read local_ref local_sha remote_ref remote_sha
do
    # echo $local_ref $local_sha $remote_ref $remote_sha
	range="$remote_sha..$local_sha"
    commits=`git rev-list --ancestry-path --no-merges --grep="$cherry" --invert-grep "$range"`
    if [ -n "$commits" ]; then
        echo >&2 'The following commits are rejected:'
        echo >&2 $commits
        error_exit;
    fi
    orig_commits=`git log --ancestry-path --no-merges --grep="$cherry" "$range" |grep "$cherry" |awk '{print $5}' |tr -d ')'`
    for orig_commit in $orig_commits; do
        if ! git branch --contains $orig_commit |grep -w master &> /dev/null ; then
            echo >&2 "Original commit $orig_commit is not in the master branch."
            error_exit;
        fi
    done
done

git lfs pre-push "$@"

exit 0