``downstream-cherry-picker``
============================

.. image:: https://travis-ci.org/ktdreyer/downstream-cherry-picker.svg?branch=master
          :target: https://travis-ci.org/ktdreyer/downstream-cherry-picker


A tool to quickly cherry-pick whole GitHub pull requests that correspond to Red
Hat Bugzilla bugs.

This is tool is suitable for cherry-picking upstream patches into downstream
``-patches`` branches for rdopkg to consume.

Example::

    $ git checkout ceph-1.3-rhel-patches && git pull

    $ downstream-cherry-picker https://github.com/ceph/ceph/pull/10699 1335564
    ...

    $ git log
    (shows the new cherry-pick for that PR/bug.)


Installing:
-----------

The easiest way to get ``downstream-cherry-picker`` is use
[ktdreyer/downstream-cherry-picker
copr](https://copr.fedoraproject.org/coprs/ktdreyer/downstream-cherry-picker/) on Fedora or el7::

    dnf copr enable ktdreyer/downstream-cherry-picker

After you've enabled the repo, install the package::

    dnf -y install downstream-cherry-picker

Or, if you want to hack on the code, install it in a Python virtualenv directly
from GitHub::

     virtualenv venv
     . venv/bin/activate
     git clone https://github.com/ktdreyer/downstream-cherry-picker
     python setup.py develop

You will now have a ``downstream-cherry-picker`` utility in your ``$PATH``.


Features:
---------

* Uses GitHub's API to determine the range of commits to cherry-pick for a
  particular pull request.

* Cherry-picks each commit in a PR using standard conventions:

   * Adds "``(cherry-picked from commit foo)``" to each cherry-pick.

   * Adds "``Resolves: rhbz#``" to each cherry-pick.

* Does all the work on a separate "rhbz-" Git branch, so you can clean up if
  things go wrong or you have to resolve conflicts by hand. This branch name
  convention will trigger the Git commit hook that inserts the rhbz number into
  each changelog. If you do not have the Git commit hook installed into your
  repository, ``downstream-cherry-picker`` will download and install it for
  you.

* If everything cherry-picked cleanly, ``downstream-cherry-picker`` will merge
  the temporary rhbz- branch back into your original branch and delete the
  rhbz- branch, so that you're all ready to push your changes to the remote.

* Automatically fetches the pull request's commits if you don't have the
  commits in your local clone already.
