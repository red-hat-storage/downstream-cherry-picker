import pytest
import os
import json
import requests
from downstream_cherry_picker import get_sha_range

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, 'fixtures')


# https://help.github.com/articles/why-are-my-commits-in-the-wrong-order/


class MockResponse(object):
    def raise_for_status(self):
        pass

    def json(self):
        # Return data from our static fixture file
        # (eg from https://api.github.com/repos/ceph/ceph/pulls/12917)
        # (or from https://api.github.com/repos/ceph/ceph/pulls/12917/commits)
        path = self.url.replace('https://api.github.com/repos/ceph/ceph',
                                FIXTURES_DIR)
        filename = path + '.json'
        with open(filename) as fp:
            return json.load(fp)


def mock_get(url):
    m = MockResponse()
    m.url = url
    return m


class TestGetShaRange(object):

    @pytest.mark.parametrize('pr,expected_first,expected_last', [
        (12917, '386640865dee30d38f17e55fc87535e419bc3cb5',
                '14a6aabe22f68436ea3297ce0851700f86ee5b12'),
    ])
    def test_get_sha_range(self, monkeypatch, pr, expected_first,
                           expected_last):
        monkeypatch.delattr('requests.sessions.Session.request')
        monkeypatch.setattr(requests, 'get', mock_get)
        (got_first, got_last) = get_sha_range('ceph', 'ceph', pr)
        assert got_first == expected_first
        assert got_last == expected_last
