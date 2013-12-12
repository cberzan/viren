#!/usr/bin/env python

import os
import random
import subprocess
import sys
import tempfile


class VirenError(RuntimeError):
    pass


def verify_rename_list(old_names, new_names):
    """
    Sanity check a rename proposal.

    If there is a problem (new names not provided, or they collide among
    themselves, etc), raises VirenError.
    """
    if len(old_names) != len(new_names):
        raise VirenError("Edited list has {} names, expected {}".format(
            len(new_names), len(old_names)))
    seen_names = set()
    for lineno, name in enumerate(new_names, 1):
        if not name:
            raise VirenError("Line {}: empty filename".format(lineno))
        if '/' in name:
            raise VirenError("Line {}: slash in filename".format(lineno))
        if name in ('.', '..'):
            raise VirenError("Line {}: filename is . or ..".format(lineno))
        if name in seen_names:
            raise VirenError("Line {}: duplicate filename".format(lineno))
        seen_names.add(name)


def mk_temp_subdir(forbidden_names):
    """
    Make a temp subdir in pwd and return its name.

    The directory name is assigned randomly, and checked not to collide with
    `forbidden_names`.
    """
    for attempt in xrange(10):
        fname = 'viren-' + hex(random.randint(1e9, 1e10))[2:]
        if fname in forbidden_names or os.path.exists(fname):
            continue
        os.mkdir(fname)
        return fname
    raise VirenError("Failed to create temp dir")


if __name__ == "__main__":
    # Get sorted list of files in pwd.
    old_names = os.listdir('.')
    old_names.sort()
    index_to_old_name = dict(enumerate(old_names))

    # Write that list to a temp file.
    _, temp_path = tempfile.mkstemp(prefix='viren')
    temp = open(temp_path, 'w')
    temp.write('\n'.join(old_names))
    temp.close()

    try:
        # Let the user edit that file in her favorite editor.
        ret = subprocess.call(['editor', temp_path])
        if ret != 0:
            raise VirenError('editor failed with return code {}'.format(ret))

        # Get the edited list back from the temp file, and sanity check it.
        temp = open(temp_path)
        new_names = [line.strip() for line in temp.xreadlines()]
        temp.close()
        verify_rename_list(old_names, new_names)

        # Move the old files to a temp subdir. We do this to avoid accidental
        # overwrites, in case old_names and new_names overlap.
        temp_dirname = mk_temp_subdir(old_names + new_names)
        for name in old_names:
            ret = subprocess.call(['mv', name, temp_dirname + os.path.sep])
            if ret != 0:
                raise VirenError('mv failed with return code {}'.format(ret))

        # Now move the files back with their new names.
        for i in xrange(len(old_names)):
            ret = subprocess.call(
                ['mv', os.path.join(temp_dirname, old_names[i]), new_names[i]])
            if ret != 0:
                raise VirenError('mv failed with return code {}'.format(ret))

        # Clean up.
        os.rmdir(temp_dirname)
        os.remove(temp_path)
        print "Done."

    except VirenError as err:
        print >>sys.stderr, "Something went wrong:"
        print >>sys.stderr, err.message
        print >>sys.stderr, "File list saved to {}".format(temp_path)
        sys.exit(1)
