#!/usr/bin/env python
# encoding: utf-8

"""
Functions to find and load vikinlp resource files, such as corpora,
grammars, and saved processing objects.  Resource files are identified
using URLs, such as ``vikinlp:corpora/abc/rural.txt`` or
``http://vikinlp.org/sample/toy.cfg``.  The following URL protocols are
supported:
  - ``file:path``: Specifies the file whose path is *path*.
    Both relative and absolute paths may be used.
  - ``http://host/path``: Specifies the file stored on the web
    server *host* at path *path*.
  - ``vikinlp:path``: Specifies the file stored in the vikinlp data
    package at *path*.  vikinlp will search for these files in the
    directories specified by ``vikinlp.data.path``.
If no protocol is specified, then the default protocol ``vikinlp:`` will
be used.
This module provides to functions that can be used to access a
resource file, given its URL: ``load()`` loads a given resource, and
adds it to a resource cache; and ``retrieve()`` copies a given resource
to a local file.
"""

import os
import re
import sys
import textwrap
from six.moves.urllib.request import url2pathname

from nltk.data import FileSystemPathPointer, ZipFilePathPointer, GzipFileSystemPathPointer
from vikinlp.util import PROJECT_DIR
from vikinlp.config import ConfigApps


vikinlp_path = os.path.join(PROJECT_DIR, 'data')

def split_resource_url(resource_url):
    """
    Splits a resource url into "<protocol>:<path>".
    >>> windows = sys.platform.startswith('win')
    >>> split_resource_url('vikinlp:home/vikinlp')
    ('vikinlp', 'home/vikinlp')
    >>> split_resource_url('vikinlp:/home/vikinlp')
    ('vikinlp', '/home/vikinlp')
    >>> split_resource_url('file:/home/vikinlp')
    ('file', '/home/vikinlp')
    >>> split_resource_url('file:///home/vikinlp')
    ('file', '/home/vikinlp')
    >>> split_resource_url('file:///C:/home/vikinlp')
    ('file', '/C:/home/vikinlp')
    """
    protocol, path_ = resource_url.split(':', 1)
    if protocol == 'vikinlp':
        pass
    elif protocol == 'file':
        if path_.startswith('/'):
            path_ = '/' + path_.lstrip('/')
    else:
        path_ = re.sub(r'^/{0,2}', '', path_)
    return protocol, path_


def normalize_resource_url(resource_url):
    r"""
    Normalizes a resource url
    >>> windows = sys.platform.startswith('win')
    >>> os.path.normpath(split_resource_url(normalize_resource_url('file:grammar.fcfg'))[1]) == \
    ... ('\\' if windows else '') + os.path.abspath(os.path.join(os.curdir, 'grammar.fcfg'))
    True
    >>> not windows or normalize_resource_url('file:C:/dir/file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('file:C:\\dir\\file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('file:C:\\dir/file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('file://C:/dir/file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('file:////C:/dir/file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('vikinlp:C:/dir/file') == 'file:///C:/dir/file'
    True
    >>> not windows or normalize_resource_url('vikinlp:C:\\dir\\file') == 'file:///C:/dir/file'
    True
    >>> windows or normalize_resource_url('file:/dir/file/toy.cfg') == 'file:///dir/file/toy.cfg'
    True
    >>> normalize_resource_url('vikinlp:home/vikinlp')
    'vikinlp:home/vikinlp'
    >>> windows or normalize_resource_url('vikinlp:/home/vikinlp') == 'file:///home/vikinlp'
    True
    >>> normalize_resource_url('http://example.com/dir/file')
    'http://example.com/dir/file'
    >>> normalize_resource_url('dir/file')
    'vikinlp:dir/file'
    """
    try:
        protocol, name = split_resource_url(resource_url)
    except ValueError:
        # the resource url has no protocol, use the vikinlp protocol by default
        protocol = 'vikinlp'
        name = resource_url
    # use file protocol if the path is an absolute path
    if protocol == 'vikinlp' and os.path.isabs(name):
        protocol = 'file://'
        name = normalize_resource_name(name, False, None)
    elif protocol == 'file':
        protocol = 'file://'
        # name is absolute
        name = normalize_resource_name(name, False, None)
    elif protocol == 'vikinlp':
        protocol = 'vikinlp:'
        name = normalize_resource_name(name, True)
    else:
        # handled by urllib
        protocol += '://'
    return ''.join([protocol, name])


def normalize_resource_name(resource_name, allow_relative=True, relative_path=None):
    """
    :type resource_name: str or unicode
    :param resource_name: The name of the resource to search for.
        Resource names are posix-style relative path names, such as
        ``corpora/brown``.  Directory names will automatically
        be converted to a platform-appropriate path separator.
        Directory trailing slashes are preserved
    >>> windows = sys.platform.startswith('win')
    >>> normalize_resource_name('.', True)
    './'
    >>> normalize_resource_name('./', True)
    './'
    >>> windows or normalize_resource_name('dir/file', False, '/') == '/dir/file'
    True
    >>> not windows or normalize_resource_name('C:/file', False, '/') == '/C:/file'
    True
    >>> windows or normalize_resource_name('/dir/file', False, '/') == '/dir/file'
    True
    >>> windows or normalize_resource_name('../dir/file', False, '/') == '/dir/file'
    True
    >>> not windows or normalize_resource_name('/dir/file', True, '/') == 'dir/file'
    True
    >>> windows or normalize_resource_name('/dir/file', True, '/') == '/dir/file'
    True
    """
    is_dir = bool(re.search(r'[\\/.]$', resource_name)) or resource_name.endswith(os.path.sep)
    if sys.platform.startswith('win'):
        resource_name = resource_name.lstrip('/')
    else:
        resource_name = re.sub(r'^/+', '/', resource_name)
    if allow_relative:
        resource_name = os.path.normpath(resource_name)
    else:
        if relative_path is None:
            relative_path = os.curdir
        resource_name = os.path.abspath(
            os.path.join(relative_path, resource_name))
    resource_name = resource_name.replace('\\', '/').replace(os.path.sep, '/')
    if sys.platform.startswith('win') and os.path.isabs(resource_name):
        resource_name = '/' + resource_name
    if is_dir and not resource_name.endswith('/'):
        resource_name += '/'
    return resource_name


def resource_url(resource_url):
    """
    """
    type_, url = split_resource_url(normalize_resource_url(resource_url))
    if type_ == 'vikinlp':
        url = os.path.join(ConfigApps.nlp_data_path, url)
    return url


######################################################################
# Search Path
######################################################################

path = []
"""A list of directories where the vikinlp data package might reside.
   These directories will be checked in order when looking for a
   resource in the data package.  Note that this allows users to
   substitute in their own versions of resources, if they have them
   (e.g., in their home directory under ~/vikinlp_data)."""

# User-specified locations:
_paths_from_env = os.environ.get('vikinlp_DATA', str('')).split(os.pathsep)
path += [d for d in _paths_from_env if d]
if 'APPENGINE_RUNTIME' not in os.environ and os.path.expanduser('~/') != '~/':
    path.append(os.path.expanduser(str('~/vikinlp_data')))

if sys.platform.startswith('win'):
    # Common locations on Windows:
    path += [
        str(r'C:\vikinlp_data'), str(r'D:\vikinlp_data'), str(r'E:\vikinlp_data'),
        os.path.join(sys.prefix, str('vikinlp_data')),
        os.path.join(sys.prefix, str('lib'), str('vikinlp_data')),
        os.path.join(
            os.environ.get(str('APPDATA'), str('C:\\')), str('vikinlp_data'))
    ]
else:
    # Common locations on UNIX & OS X:
    path += [
        ConfigApps.nlp_data_path,
        str('/usr/share/vikinlp_data'),
        str('/usr/local/share/vikinlp_data'),
        str('/usr/lib/vikinlp_data'),
        str('/usr/local/lib/vikinlp_data'),
        vikinlp_path,
    ]


######################################################################
# Access Functions
######################################################################

# Don't use a weak dictionary, because in the common case this
# causes a lot more reloading that necessary.


def find(resource_name, paths=None):
    """
    Find the given resource by searching through the directories and
    zip files in paths, where a None or empty string specifies an absolute path.
    Returns a corresponding path name.  If the given resource is not
    found, raise a ``LookupError``, whose message gives a pointer to
    the installation instructions for the vikinlp downloader.
    Zip File Handling:
      - If ``resource_name`` contains a component with a ``.zip``
        extension, then it is assumed to be a zipfile; and the
        remaining path components are used to look inside the zipfile.
      - If any element of ``vikinlp.data.path`` has a ``.zip`` extension,
        then it is assumed to be a zipfile.
      - If a given resource name that does not contain any zipfile
        component is not found initially, then ``find()`` will make a
        second attempt to find that resource, by replacing each
        component *p* in the path with *p.zip/p*.  For example, this
        allows ``find()`` to map the resource name
        ``corpora/chat80/cities.pl`` to a zip file path pointer to
        ``corpora/chat80.zip/chat80/cities.pl``.
      - When using ``find()`` to locate a directory contained in a
        zipfile, the resource name must end with the forward slash
        character.  Otherwise, ``find()`` will not locate the
        directory.
    :type resource_name: str or unicode
    :param resource_name: The name of the resource to search for.
        Resource names are posix-style relative path names, such as
        ``corpora/brown``.  Directory names will be
        automatically converted to a platform-appropriate path separator.
    :rtype: str
    """
    resource_name = normalize_resource_name(resource_name, True)

    # Resolve default paths at runtime in-case the user overrides
    # vikinlp.data.path
    if paths is None:
        paths = path

    # Check if the resource name includes a zipfile name
    m = re.match(r'(.*\.zip)/?(.*)$|', resource_name)
    zipfile, zipentry = m.groups()

    # Check each item in our path
    for path_ in paths:
        # Is the path item a zipfile?
        if path_ and (os.path.isfile(path_) and path_.endswith('.zip')):
            try:
                return ZipFilePathPointer(path_, resource_name)
            except IOError:
                # resource not in zipfile
                continue

        # Is the path item a directory or is resource_name an absolute path?
        elif not path_ or os.path.isdir(path_):
            if zipfile is None:
                p = os.path.join(path_, url2pathname(resource_name))
                if os.path.exists(p):
                    if p.endswith('.gz'):
                        return GzipFileSystemPathPointer(p)
                    else:
                        return FileSystemPathPointer(p)
            else:
                p = os.path.join(path_, url2pathname(zipfile))
                if os.path.exists(p):
                    try:
                        return ZipFilePathPointer(p, zipentry)
                    except IOError:
                        # resource not in zipfile
                        continue

    # Fallback: if the path doesn't include a zip file, then try
    # again, assuming that one of the path components is inside a
    # zipfile of the same name.
    if zipfile is None:
        pieces = resource_name.split('/')
        for i in range(len(pieces)):
            modified_name = '/'.join(pieces[:i] +
                                     [pieces[i] + '.zip'] + pieces[i:])
            try:
                return find(modified_name, paths)
            except LookupError:
                pass

    # Display a friendly error message if the resource wasn't found:
    msg = textwrap.fill(
        'Resource %r not found.  Please use the vikinlp Downloader to '
        'obtain the resource:  >>> vikinlp.download()' %
        (resource_name,), initial_indent='  ', subsequent_indent='  ',
        width=66)
    msg += '\n  Searched in:' + ''.join('\n    - %r' % d for d in paths)
    sep = '*' * 70
    resource_not_found = '\n%s\n%s\n%s' % (sep, msg, sep)
    raise LookupError(resource_not_found)



if __name__ == '__main__':
    print(normalize_resource_url("vikinlp:hello\ok"))
    print(resource_url("vikinlp:hello/ok"))
    print(resource_url("file:hello/ok"))
