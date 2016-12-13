from mpypi import URLPackage, main
"""
To execute, do the following:
    $ python example.py 
    $ pip install pysorter==develop -i http://localhost:7890
"""
packages = [
    URLPackage('pysorter', [('pysorter-develop', 'git+file:///home/chris/Desktop/development/project_public/pysorter/pysorter@develop')])
]

main(packages)
