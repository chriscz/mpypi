import re

class PackageBase(object):
    """
    Base class used by all package implementations
    """

    """unique name string."""
    name = None
    def links(self): 
        """
        Return an interable of (name, url) pairs
        """
        raise NotImplementedError()

class URLPackage(PackageBase):
    """
    Implementation of a simple name --> links package mapping

    NOTES
    -----
        - #egg= will be added to all urls that start git/svn etc a git+, if
          it is NOT already present
    """
    EGG_FMT = "#egg={}"

    p_egg = re.compile("#egg=")
    # add #egg to urls that start on something like git+ or svn+
    p_starts = re.compile('^\w+\+')

    def __init__(self, name, links):
        """
        Arguments
        ---------
        name: str
            name of this package

        links: iterable of 2-tuples
            tuples are of the form (name: str, url: str)
        """
        self.name = name
        self.links = list(links)

        # update URLS using #egg={} 
        for i in xrange(len(links)):
            name, url = self.links[i]
            if self.p_starts.match(url) and not self.p_egg.search(url):
                url += self.EGG_FMT.format(name)
                self.links[i] = (name, url)
