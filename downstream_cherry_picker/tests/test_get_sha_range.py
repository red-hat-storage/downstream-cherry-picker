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

    def test_get_sha_range(self, monkeypatch):
        monkeypatch.delattr('requests.sessions.Session.request')
        monkeypatch.setattr(requests, 'get', mock_get)
        (first, last) = get_sha_range('ceph', 'ceph', 12917)
        assert first == '386640865dee30d38f17e55fc87535e419bc3cb5'
        assert last == '14a6aabe22f68436ea3297ce0851700f86ee5b12'
