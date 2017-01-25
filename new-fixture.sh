#!/bin/bash

# Easy way to quickly add more tests using real API data.

set -ex

if [ -z $1 ]; then
  echo "Specify a ceph PR URL (eg https://github.com/ceph/ceph/pull/12917)."
  exit 1
fi

PR=$1

ORG=$(echo $PR | awk -F/ '{ print $4 }')
REPO=$(echo $PR | awk -F/ '{ print $5 }')
PULL=$(echo $PR | awk -F/ '{ print $7 }')

cd downstream_cherry_picker/tests/fixtures/pulls
curl -q https://api.github.com/repos/$ORG/$REPO/pulls/$PULL > $PULL.json
mkdir -p $PULL
curl -q https://api.github.com/repos/$ORG/$REPO/pulls/$PULL/commits > $PULL/commits.json

git add $PULL.json
git add $PULL/commits.json
