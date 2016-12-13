from mpypi import cd, run, PackageBase, URLPackage, main

packages = [
    URLPackage('pysorter', [('pyrunner-develop', 'git+file:///home/chris/Desktop/development/project_public/pysorter/pysorter@develop')])
]

main(packages)
