#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import argparse
import os
import shutil
import errno

from fuse import FUSE, FuseOSError, Operations
from logtrace import Trace

__author__ = "Markus M<E4>sker"
__email__ = "maesker@gmx.net"
__version__ = "1.0"
__status__ = "Development"


class TraceGenerator(Operations):

    def __init__(self, root, flush=False, clear=False):
        self.base = root
        self.virtual_root = os.path.join(root, "root")
        if clear:
            shutil.rmtree(self.virtual_root)
        if not os.path.isdir(self.virtual_root):
            os.makedirs(self.virtual_root)
        self.trace = Trace(
            os.path.join(self.base, 'trace'), flush=flush, clear=clear)
        self._log = self.trace.log

    def virtual_root_path(self, path):
        if path.startswith("/"):
            return os.path.join(self.virtual_root, path[1:])
        return os.path.join(self.virtual_root, path)

    # File System API:

    def access(self, path, mode):
        self._log("ACCESS", "path=%s; mode=%s" % (path, mode))
        if not os.access(self.virtual_root_path(path), mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        self._log("CHMOD", "path=%s; mode=%s" % (path, mode))
        return os.chmod(self.virtual_root_path(path), mode)

    def chown(self, path, uid, gid):
        self._log("CHOWN", "path=%s; uid=%s; gid=%s" % (path, uid, gid))
        return os.chown(self.virtual_root_path(path), uid, gid)

    def create(self, path, mode, fi=None):
        self._log("CREATE", "path=%s; mode=%s; fi=%s" % (path, mode, fi))
        return os.open(self.virtual_root_path(path),
                       os.O_WRONLY | os.O_CREAT,
                       mode)

    def flush(self, path, fh):
        self._log("FLUSH", "path=%s" % path)
        return os.fsync(fh)

    def fsync(self, path, fdatasync, fh):
        self._log("FSYNC", "path=%s" % path)
        return self.flush(path, fh)

    def getattr(self, path, fh=None):
        self._log("GETATTR", "path=%s" % (path))
        return dict((key, getattr(os.lstat(self.virtual_root_path(path)), key))
                    for key in ('st_atime', 'st_ctime', 'st_gid',
                                'st_mode', 'st_mtime', 'st_nlink',
                                'st_size', 'st_uid'))

    def link(self, target, name):
        self._log("LINK", "target=%s; name=%s" % (target, name))
        return os.link(self.virtual_root_path(name),
                       self.virtual_root_path(target))

    def mkdir(self, path, mode):
        self._log("MKDIR", "path=%s; mode=%s" % (path, mode))
        return os.mkdir(self.virtual_root_path(path), mode)

    def mknod(self, path, mode, dev):
        self._log("MKNOD", "path=%s; mode=%s; dev=%s" % (path, mode, dev))
        return os.mknod(self.virtual_root_path(path), mode, dev)

    def open(self, path, flags):
        self._log("OPEN", "path=%s; flags=%s" % (path, flags))
        return os.open(self.virtual_root_path(path), flags)

    def read(self, path, length, offset, fh):
        self._log("READ", "path=%s; length=%s; offset=%i" %
                  (path, length, offset))
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def readdir(self, path, fh):
        self._log("READDIR", "path=%s" % (path))
        dirents = ['.', '..']
        if os.path.isdir(self.virtual_root_path(path)):
            dirents.extend(os.listdir(self.virtual_root_path(path)))
        for r in dirents:
            yield r

    def readlink(self, path):
        self._log("READLINK", "path=%s" % (path))
        pathname = os.readlink(self.virtual_root_path(path))
        if pathname.startswith("/"):
            return os.path.relpath(pathname, self.virtual_root)
        return pathname

    def release(self, path, fh):
        self._log("RELEASE", "path=%s" % path)
        return os.close(fh)

    def rename(self, old, new):
        self._log("RENAME", "old=%s; new=%s" % (old, new))
        return os.rename(self.virtual_root_path(old),
                         self.virtual_root_path(new))

    def rmdir(self, path):
        self._log("RMDIR", "path=%s" % (path))
        return os.rmdir(self.virtual_root_path(path))

    def statfs(self, path):
        self._log("STATFS", "path=%s" % (path))
        stv = os.statvfs(self.virtual_root_path(path))
        return dict((key, getattr(stv, key))
                    for key in ('f_bavail', 'f_bfree', 'f_blocks', 'f_bsize',
                                'f_favail', 'f_ffree', 'f_files', 'f_flag',
                                'f_frsize', 'f_namemax'))

    def symlink(self, name, target):
        self._log("SYMLINK", "name=%s; target=%s" % (name, target))
        return os.symlink(target, self.virtual_root_path(name))

    def truncate(self, path, length, fh=None):
        self._log("TRUNC", "path=%s; length=%i" % (path, length))
        with open(self.virtual_root_path(path), 'r+') as f:
            f.truncate(length)

    def unlink(self, path):
        self._log("UNLINK", "path=%s" % (path))
        return os.unlink(self.virtual_root_path(path))

    def utimens(self, path, times=None):
        self._log("UTIMES", "path=%s; times:%s" % (path, times))
        return os.utime(self.virtual_root_path(path), times)

    def write(self, path, buf, offset, fh):
        self._log("WRITE", "path=%s; offset=%i; length_buf=%i" %
                  (path, offset, len(buf)))
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Collect IO events')
    parser.add_argument(
        '-m', '--mountpoint', required=True,
        help='Directory to use as mountpoint')
    parser.add_argument(
        '-b', '--backend', required=True,
        help='File system backend to pass requests to')
    parser.add_argument(
        '-f', '--flush', default=False, action="store_true",
        help='Flush log messages immediately')
    parser.add_argument(
        '-c', '--clear', default=False, action="store_true",
        help='Clear backend before mounting, removes previous traces as well.')

    args = parser.parse_args()

    if not os.path.isdir(args.mountpoint):
        os.mkdir(args.mountpoint)
    FUSE(TraceGenerator(args.backend, flush=args.flush, clear=args.clear),
         args.mountpoint, nothreads=True, foreground=True)
