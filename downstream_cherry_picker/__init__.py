import logging
import os
import re
import stat
import subprocess
import sys
import requests

__version__ = '1.1.0'

USAGE = """
%(cmd)s github-url rhbz-number

Example:
%(cmd)s https://github.com/ceph/ceph/pull/1234 1234567

...to insert "Resolves: rhbz#1234567" into each cherry-pick.
"""

API_BASE = 'https://api.github.com'

PR_URL_REGEX = r'https://github.com/([^/]+)/([^/]+)/pull/(\d+)$'

HOOK_URL = 'https://gist.githubusercontent.com/alfredodeza/252d66dbf4a5c36cfb7b1cb3c0faf445/raw/08cff9560328c0c03b11b9f6ac9db98dbad0a6e4/prepare-commit-msg'  # NOQA

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger()


class PRParseException(Exception):
    pass


def usage_error():
    """ Show the usage text and exit with non-zero exit code. """
    raise SystemExit(USAGE % {'cmd': os.path.basename(sys.argv[0])})


def current_branch():
    """ Get our current branch's name """
    cmd = ('git', 'rev-parse', '--abbrev-ref', 'HEAD')
    return subprocess.check_output(cmd, universal_newlines=True).rstrip()


def current_sha():
    """ Get our current sha1 """
    cmd = ('git', 'rev-parse', 'HEAD')
    return subprocess.check_output(cmd, universal_newlines=True).rstrip()


def get_sha_range(owner, repo, number):
    """
    Get a range of SHAs for a particular GitHub pull request.

    To correctly determine the first and last commits in a PR, we have to ask
    the main Pull Request API endpoint to give us the "base" and "head", and
    then use those values. "head" is of course the final commit in the PR
    (returned as "last" here). The "first" commit is the one in our list that
    has "base" as its parent.

    :return: tuple, ('first', 'last'). For example ('123abc', '456def')
    """
    # Find the "base" and "head" of this pull request.
    api_endpoint = '%s/repos/%s/%s/pulls/%d'
    r = requests.get(api_endpoint % (API_BASE, owner, repo, number))
    r.raise_for_status()

    base = r.json()['base']['sha']
    head = r.json()['head']['sha']

    # Find the first commit (the one that has "base" as a parent.)
    api_endpoint = '%s/repos/%s/%s/pulls/%d/commits'
    r = requests.get(api_endpoint % (API_BASE, owner, repo, number))
    r.raise_for_status()

    first = None
    for commit in r.json():
        if base in [parent['sha'] for parent in commit['parents']]:
            if first is None:
                first = commit['sha']
            else:
                # Not sure this can ever happen, but let's bail if it does:
                msg = 'Commits %s and %s are both children of base commit %s'
                raise RuntimeError(msg % (first, commit['sha'], base))

    return (first, head)


def parse_pr_url(url):
    """ Return the owner, repo, and PR number for a PR URL string. """
    m = re.match(PR_URL_REGEX, url)
    if not m:
        raise PRParseException(url)
    if not m.group(1):
        raise PRParseException('could not find owner in %s' % url)
    if not m.group(2):
        raise PRParseException('could not find repo in %s' % url)
    if not m.group(3):
        raise PRParseException('could not find PR # in %s' % url)
    return (m.group(1), m.group(2), int(m.group(3)))


def git(*args):
    """ Run a git shell command. """
    args = ('git',) + args
    log.info('+ ' + ' '.join(args))
    subprocess.check_call(args)


def ensure_hook():
    """ Ensure that the .git/hooks/prepare-commit-msg file is ready """
    hook = '.git/hooks/prepare-commit-msg'
    # https://gist.github.com/alfredodeza/252d66dbf4a5c36cfb7b1cb3c0faf445
    if not os.path.isfile(hook):
        log.warn('%s not found, downloading from Gist' % hook)
        r = requests.get(HOOK_URL)
        fh = open(hook, 'w')
        fh.write(r.text)
        fh.close()
    if not os.access(hook, os.X_OK):
        st = os.stat(hook)
        os.chmod(hook, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main(argv):
    try:
        url_arg = argv[1]
    except IndexError:
        log.error('Missing GitHub PR argument')
        usage_error()

    try:
        bz = argv[2]
    except IndexError:
        log.error('Missing RHBZ number argument')
        usage_error()

    # Parse the GitHub PR URL.
    try:
        owner, repo, number = parse_pr_url(url_arg)
    except PRParseException as e:
        log.error('Could not parse GitHub PR argument:')
        raise SystemExit(e)

    ensure_hook()

    # The sha1 range to cherry-pick:
    (first, last) = get_sha_range(owner, repo, number)

    try:
        git('cat-file', '-e', '%s^{commit}' % first)
    except subprocess.CalledProcessError as e:
        log.info("First upstream commit not found. Fetching from github.com.")
        git('fetch',
            'https://github.com/%s/%s' % (owner, repo),
            'pull/%d/head' % number)

    starting_branch = current_branch()

    # Log our PR and starting ref, in case the user wants to reset to this
    # ref later, for some reason.
    starting_ref = current_sha()
    msg = 'Cherry-picking https://github.com/%s/%s/pull/%d to %s (%s)'
    log.info(msg % (owner, repo, number, starting_branch, starting_ref))

    # Use an rhbz branch so our prepare-commit-msg hook will fire.
    git('checkout', '-b', 'rhbz-' + bz)

    # Cherry-pick the range of commits.
    # EDITOR=/bin/true causes the prepare-commit-msg hook to run.
    git('-c', 'core.editor=/bin/true', 'cherry-pick', '-x',
        '%s~..%s' % (first, last))

    # Merge this rhbz branch back into our starting branch.
    git('checkout', starting_branch)
    git('merge', '--ff-only', 'rhbz-' + bz)
    git('branch', '-d', 'rhbz-' + bz)
