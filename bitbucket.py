from mpypi import cd, run, PackageBase, URLPackage, main
"""
A sample BitBucket Repository backed index that supports the use
of private ssh authorized repositories.

NOTE
----

If you get any of the following warnings

 > site-packages/requests/packages/urllib3/util/ssl_.py:334: SNIMissingWarning: 
 >     An HTTPS request has been made, but the SNI (Subject Name Indication) extension 
 >     to TLS is not available on this platform. This may cause the server to present an incorrect TLS certificate, 
 >     which can cause validation failures. 
 >     You can upgrade to a newer version of Python to solve this. 
 >     For more information, see https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
 > site-packages/requests/packages/urllib3/util/ssl_.py:132: InsecurePlatformWarning: 
 >     A true SSLContext object is not available. 
 >     This prevents urllib3 from configuring SSL appropriately and may cause 
 >     certain SSL connections to fail. You can upgrade to a newer version of Python 
 >     to solve this. For more information, 
 >     see https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings

then the SSL libraries of your Python version are outdated.
Do a `pip install pyopenssl ndg-httpsclient pyasn1` to fix this.
"""

# Requires
# - pybitbucket
#
from pybitbucket.auth import BasicAuthenticator
from pybitbucket.bitbucket import Client
from pybitbucket.repository import Repository
from pybitbucket.ref import Tag, Branch

from getpass import getpass

import logging

log = logging.getLogger('bitbucket')

class BitBucketPackage(PackageBase):
    """
        Exposes GIT bitbucket repositories with tags as PyPi packages.
    """
    # issue with `{owner}:` as discussed in http://stackoverflow.com/questions/18883430/trouble-installing-private-github-repository-using-pip
    BB_SSH_URL = "git+ssh://git@bitbucket.org/{owner}/{repo}.git@{ref}#egg={package}"

    def __init__(self, package_name, owner_name, repo_name, client, strip_v=True): 
        """
        Arguments
        ---------
        repository_name: str
            of the form username/repo
        """
        # XXX test repository resolution
        Repository.find_repository_by_name_and_owner(repo_name, owner_name, client=client)

        self.name = package_name
        self.owner_name = owner_name
        self.repo_name = repo_name

        self.client = client

        self.do_strip_v = strip_v

    @property
    def tags(self):
        return list(Tag.find_tags_in_repository(self.repo_name,
                                                self.owner_name,
                                                client=self.client))
    @property
    def branches(self):
        return list(Branch.find_branches_in_repository(self.owner_name, 
                                                       self.repo_name, 
                                                       client=self.client))
    @property
    def links(self):
        for tag in self.tags:
            tname = tag.name
            if tname[0].isdigit() or tname[0] == 'v':
                pkg_tname = tname

                if self.do_strip_v:
                    pkg_tname = pkg_tname.lstrip('v')

                package = '{}-{}'.format(self.name, pkg_tname) 

                params = {
                    'owner': self.owner_name,
                    'repo': self.repo_name,
                    'ref': tname, 
                    'package': package
                }
                yield (package, self.BB_SSH_URL.format(**params))

            else:
                log.warn('ignore non sematic version tag: %s', tname)


def load_packages(packages, username, email, password=None):
    """
    Creates BitBucketPackage instances for the given list of packages,
    using the given credentials to authenticate requests against the API.

    Arguments
    ---------
    packages: list of tuple
        tuples are of the format (package_name, owner_name, repository_name)
    """
    if password is None:
        password = getpass('password for {}@bitbucket: '.format(username))

    bitbucket = Client(BasicAuthenticator(username, password, email))
    del password

    bb_packages = []

    for (pkg, owner, repo) in packages:
        bb_packages.append(BitBucketPackage(pkg, owner, repo, bitbucket))
    
    return bb_packages 


if __name__ == '__main__':
    packages = [
        ('pybitbucket', 'atlassian', 'python-bitbucket')
    ]

    username = raw_input("bitbucket username: ")
    email = raw_input("bitbucket email: ")

    bbs = load_packages(packages, username, email)
    main(bbs)
