``downstream-cherry-picker``
============================

A tool to quickly cherry-pick whole GitHub pull requests that correspond to Red
Hat Bugzilla bugs.

This is tool is suitable for cherry-picking upstream patches into downstream
``-patches`` branches for rdopkg to consume.

Example::

    $ git checkout ceph-1.3-rhel-patches
    $ downstream-cherry-picker https://github.com/ceph/ceph/pull/10699 1335564
    ...
    $ git log
    (shows the new cherry-pick for that PR/bug.)

Features:

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

* Automatically fetches the pull request's commits if you don't have the
  commits in your local clone already.
