from mpypi import cd, run, PackageBase, URLPackage, main

packages = [
    URLPackage('pyrunner', [('pyrunner-1.0', 'git+file:///home/chris/Desktop/development/project_public/pysorter/pysorter')])
]

main(packages)
