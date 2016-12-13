import os

from subprocess import Popen, PIPE
from contextlib import contextmanager
from collections import namedtuple

RunResult = namedtuple('RunResult', ['returncode', 'stdout', 'stderr'])

@contextmanager
def cd(directory):
    """
    Context manager that changes the working directory in the given context.

    Example
    -------

    with cd('/home/'):
        # do some stuff
    """
    old = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old)

def run(*args, **kwargs):
    """
    Runs a command on the underlying system. 

    Optional Keyword Arguments
    --------------------------
    input: string
        passed to the Popen.communicate call as input

    timeout: millisecond float
        specifies how long to wait before terminating the given command  
    """
    _patch_popen(Popen)
    assert len(args) > 0

    arguments = []

    input = kwargs.pop('input', None)

    if len(args) == 1:
        if isinstance(args[0], basestring):
            arguments = args[0].split()
    else:
        for i in args:
            if isinstance(i, (list, tuple)):
                for j in i:
                    arguments.append(j)
            else:
                arguments.append(i)

    def set_default_kwarg(key, default):    
        kwargs[key] = kwargs.get(key, default)

    set_default_kwarg('stdin', PIPE)
    set_default_kwarg('stdout', PIPE)
    set_default_kwarg('stderr', PIPE)


    proc = Popen(arguments, **kwargs)
    stdout, stderr = proc.communicate(input)

    return RunResult(proc.returncode, stdout, stderr)

def _patch_popen(Popen):
    """
    Patches Popen.communicate to take a timeout option that allows a process to
    be timed out. The timeput is a millisecond float
    """
    if hasattr(Popen.communicate, 'patched'):
        return

    from threading import Timer
    _communicate = Popen.communicate

    def communicate(self, *args, **kwargs):
        timeout = kwargs.pop('timeout', None)

        if timeout is not None:
            timeout /= 1000.0
            timer = Timer(timeout, self.kill)
            try:
                timer.start()
                return _communicate(self, *args, **kwargs)
            finally:
                timer.cancel()
        else:
            return _communicate(self, *args, **kwargs)

    Popen.communicate = communicate
    communicate.patched = True
