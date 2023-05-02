import json as jsonlib
import os
import shutil


def add_dry_run_arg(parser):
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Do not perform the action, but show what would be done.')


def add_batch_proccessor_args(parser, report: bool = True):
    parser.add_argument('-w', '--wait-between-items', default=2.0, type=float,
                        help="number of seconds to wait between processing items",
                        dest='wait')
    parser.add_argument('-f', '--fail-fast', dest='fail_fast', action='store_true', help='fail on first error ')
    if report:
        parser.add_argument('-r', '--report-file', default='-', help="the report file, or - for stdout",
                            dest='report_file')


def print_dry_run_message(method, url, params=None, headers=None, data=None, json=None):
    print("DRY-RUN: only printing command, not sending it...")
    print(f"{method} {url}")
    print(f"headers: {headers}") if headers else None
    print(f"params: {params}") if params else None
    print(f"data: {data}") if data else None
    print(f"json: {jsonlib.dumps(json)}") if json else None
    print()


def is_sub_path_of(child, parent):
    """
    Returns True if child is a descendant directory of parent, or if child is a file in a descendant directory
    of parent. Returns False otherwise. If one of the paths does not exist, returns False. The paths are first
    converted to absolute paths."""
    if not os.path.exists(child) or not os.path.exists(parent):
        return False
    absolute_parent = os.path.abspath(parent)
    absolute_dir = os.path.abspath(child)
    return absolute_dir.startswith(absolute_parent)


def has_file_pred(file, pred):
    return pred(file)


def has_dirtree_pred(path, pred):
    """
    Returns True if all files and directories in the directory tree rooted at path satisfy the predicate pred.
    """
    for root, dirs, files in os.walk(path):
        return pred(root) \
            and all(pred(os.path.join(root, d)) for d in dirs) \
            and all(pred(os.path.join(root, f)) for f in files)


def set_permissions(path, dir_mode, file_mode, group):
    """
    Sets the permissions of all files and directories in the directory tree rooted at path to dir_mode and file_mode,
    respectively. The group of all files and directories is set to group.
    """
    for root, dirs, files in os.walk(path):
        shutil.chown(root, group=group)
        for d in [root] + dirs:
            p = os.path.join(root, d)
            os.chmod(p, dir_mode)
            shutil.chown(p, group=group)
        for f in files:
            p = os.path.join(root, f)
            os.chmod(p, file_mode)
            shutil.chown(p, group=group)


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            # skip if it is symbolic link
            if not os.path.islink(os.path.join(dirpath, f)):
                total_size += os.path.getsize(os.path.join(dirpath, f))
    return total_size


# Return size in human-readable format
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)