import pytest
import downstream_cherry_picker
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
