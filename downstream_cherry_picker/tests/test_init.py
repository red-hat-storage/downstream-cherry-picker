import pytest
import downstream_cherry_picker
from downstream_cherry_picker import current_branch, git
from downstream_cherry_picker import parse_pr_url, PRParseException


class TestInit(object):
    def test_init(self):
        assert downstream_cherry_picker

    def test_parse_pr_url(self):
        url = 'https://github.com/octocat/Hello-World/pull/1347'
        (owner, repo, pr) = parse_pr_url(url)
        assert owner == 'octocat'
        assert repo == 'Hello-World'
        assert pr == 1347

    @pytest.mark.parametrize('url', [
        '',
        'https://foobar.com/',
        'https://github.com/octocat/',
        'https://github.com/octocat/Hello-World',
        'https://github.com/octocat/Hello-World/pull',
        'https://github.com/octocat/Hello-World/pull/123/garbage',
    ])
    def test_parse_pr_url_failures(self, url):
        with pytest.raises(PRParseException) as e:
            parse_pr_url(url)
        print(e)

    def test_git(self):
        # Test assumes git is in $PATH.
        # Just assert that this doesn't blow up:
        git('--version')
        assert True

    def test_current_branch(self):
        # Test assumes we're running from a Git branch.
        assert current_branch() == 'master'
