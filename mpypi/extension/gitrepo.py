from __future__ import unicode_literals

from ..util import cd, run
from ..package import PackageBase

import os
import logging
import re

from functools import partial

log = logging.getLogger(__name__)

# set our default configuration
run = partial(run, fail_on_error=True, encoding='utf-8')

class GitRepoPackage(PackageBase):
    """
    Package index for a git repository stored on the filesystem.
    """
    p_branch = re.compile(r'^\s*\*')
    p_version = re.compile('^\d|v\d')

    def __init__(self, packagename, location, strip_v=False):
        self.name = packagename

        self.location = os.path.abspath(location)
        self.strip_v = strip_v

        with cd(self.location):
            root = run('git rev-parse --show-toplevel').stdout.strip()
            self.gitroot = os.path.abspath(root)

    @property
    def tags(self):
        with cd(self.location):
            raw_tags = run('git tag').stdout.split('\n')

        tags = []
        for t in raw_tags:
            t = t.strip()
            if not t: continue
            tags.append(t)
        return tags

    @property
    def branches(self):
        with cd(self.location):
            raw_branches = run('git branch').stdout.split('\n')

        branches = []
        for b in raw_branches:
            b = self.p_branch.sub('', b).strip()
            if not b: continue

            branches.append(b)
        return branches

    @property
    def urlformat(self):
        return 'git+file:///{path}@{ref}#egg={package}'

    def _build_link_entry(self, reporoot, ref, refname=None, **extra_url_params):
        refname = refname or ref
        package = '{}-{}'.format(self.name, refname)

        # most likely a filepath
        if reporoot.startswith('/'):
            reporoot = reporoot[1:]

        params = {
            'package': package,
            'path': reporoot,
            'ref': ref,
        }
        params.update(extra_url_params)

        return (package, self.urlformat.format(**params))

    @property
    def links(self):
        for tag in self.tags:
            # Only consume tags that look like versions
            if self.p_version.search(tag):
                tname = tag
                if self.strip_v:
                    tname = tname.lstrip('v')

                yield self._build_link_entry(self.gitroot, tag, tname) 
            else:
                log.warn('ignore non sematic version tag: %s', tag)

        for branch in self.branches:
            yield self._build_link_entry(self.gitroot, branch)


if __name__ == '__main__':
    from .. import main
    base = os.path.dirname(os.path.abspath(__file__))

    import sys
    log.setLevel(logging.DEBUG)
    log.addHandler(logging.StreamHandler(sys.stderr))

    repo = GitRepoPackage('mpypi', base)
    for l in repo.links:
        print("%s --> %s" % (l[0], l[1]))

    main([repo])
