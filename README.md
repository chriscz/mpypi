# Description
Mpypi is an extensible private pypi index.
The tool was written because I needed a private pypi index
that dynamically generates a package index based on the
tags in a private bitbucket repository.

# Python versions
- Python 2.7
- Python 3.5

# Custom Package Types
To create a custom Packge type is very straightforward. For an example, look
at the `mpypi/extension/bitbucket.py` file.  

# Usage
To make use of mpypi you will need to write a bootstrapping script.
This repository has several examples of bootstrapping scripts.
Here is a short summary of the procedure:

1. Install `mpypi` by doing a `pip install https://github.com/chriscz/mpypi.git`
2. Create your bootstrapping code in a file, say `bootmpypi.py`
3. Use the existing `URLPackage` class or write your own package classes
   by extending `PackageBase`
4. Create several package instances and store them in a *list*
5. Optionally, instead of pre-creating packages, you may want to create a custom
   **index** instead. see **TODO** for an example of a custom index.
6. call `mpypi.main` with your list of packages (and / or your custom index) right at the end
   of the file. Look at the signature of `mpypi.main` for additional parameters.
7. execute `python bootmpypi.py` to host your local pypi index server.

# Configuring pip
To use mpypi you will have to point `pip` to your locally hosted repository.
This section will show you how to do that. For the remainder of this section
I will assume that your index is hosted at `http://localhost:7890`

## General notes and Tips
- The `~/.pip/pip.conf` contains your *global* pip configuration
- The `PIP_CONFIG_FILE` environment variable can be set to an alternative configuration file
- You can use the `--extra-index-url` inside your `requirements.txt` file or on the commandline
- You can use the `--index-url` to specify the default index url

### Global installation
To do a global install, add the `extra-index-url` to the global section of
your pip configuration file (`~/.pip/pip.conf`).
```
[global]
; Extra index to private pypi dependencies
extra-index-url = http://localhost:7890/
```
### Less intrusive installation
To use your repository from a local virtualenv, or requirements.txt you can do one of the following
 - when installing from pip, do a `pip --extra-index-url http://localhost:7890/  <yourpackage-name-here>`
 - add the following line to the top of your `requirements.txt` file
    ```
    --extra-index-url http://localhost:7890/
    ```

# Examples
There are currently two examples you can execute:
- `python example.py`
- `python -m mpypi.extension.bitbucket` (requires that you install pybitbucket)
- [Base project for mpypi implementations](https://github.com/chriscz/mpypi-bitbucket)

# Resources
The following resources were investigated during the development of this project
- http://blog.xelnor.net/private-pypi/
- https://jasonstitt.com/pypi-index-install-from-get-repos
- https://gist.github.com/Jaza/fcea493dd0ba6ebf09d3


For the bitbucket example I made use of the [python-bitbucket project](https://bitbucket.org/atlassian/python-bitbucket).
