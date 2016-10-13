# traverse.py
# various functions for traversing directories, meanwhile it returns destination directory with different
# parent node
# author: xiao yang <xiaoyang0117@gmail.com>    
# date: 2016.Mar.01

import os
import re
import sys

# @param: dst_dir could be an empty string when 'dst_file' is not needed
# @param: fn is a function which accepts two argments - src_file, dst_file
# @param: target filters files found
# @param: kwargs are passed to fn
# the function also could be used in this way:
# src_file, _ = traverse_with_kwargs("path/to/target", "", shutil.move, "txt", date="2016/09/01")
def traverse_with_kwargs(src_dir, dst_dir, fn, target='.wav', err=sys.stderr, **kwargs):
    t = traverser(src_dir, dst_dir, target, err)
    for src_file, dst_file in t:
        fn(src_file, dst_file, **kwargs)


# no arguments provided version for traversing
def traverse(src_dir, dst_dir, fn, target='.wav', err=sys.stderr):
    traverse_with_kwargs(src_dir, dst_dir, fn, target, err)


# generator version of traversing
def traverser(src_dir, dst_dir, target='.wav', err=sys.stderr):
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.endswith(target):
                try:
                    src_file = os.path.join(dirpath, filename)
                    src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
                    dst_file = os.path.join(dst_dir, src_file[src_dir_len:])    # should not use replace
                    yield src_file, dst_file
                except Exception as e:
                    err.write("unable to process {filename} for {reason}\n".format(filename=src_file, reason=e))
    

# traverse directories given by a text file which lists all pathes
def traverse_by_reference(reference, coding='utf-8'):
    with open(reference) as f:
        for path in f:
            path = path.decode(coding).strip()
            if os.path.isdir(path):
                yield path
            else:
                print "directory {0} does not exist".format(path)
