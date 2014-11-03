#! /usr/bin/env python
from __future__ import print_function, absolute_import
import sys
import os
import argparse
import subprocess
import logging
import shutil

try:
    raw_input
except NameError:
    raw_input = input

logger = logging.getLogger('conda_workspace')


def run_cmd(command):
    subprocess.check_call(command, shell=True)


WORKSPACE = '.conda.workspace'
ENV_CREATE = "conda create -p {envpath} {spec}"
ENV_LIST = "conda list -p {envpath}"


class ActionFailed(BaseException):
    pass


def find_root(path):
    """Find the root of a workspace

    Recursive traverse to the parent directory until we find a workspace folder
    """
    path = os.path.abspath(path)
    wspath = os.path.join(path, WORKSPACE)
    logger.info('is root? %s', path)
    if os.path.isdir(wspath):
        return wspath
    else:
        head, _ = os.path.split(path)
        if head == path:
            raise ActionFailed("Not in a conda workspace")
        return find_root(head)


def iter_spec(wspath):
    for p in os.listdir(wspath):
        p = os.path.join(wspath, p)
        if os.path.isdir(p):
            yield p


def project_install(wspath, name, spec):
    envpath = os.path.join(wspath, name)
    spec = ' '.join(spec)
    cmd = ENV_CREATE.format(envpath=envpath, spec=spec)
    if not os.path.exists(envpath):
        run_cmd(cmd)


def list_spec(wspath, show_details=False):
    for envpath in iter_spec(wspath):
        if show_details:
            print(os.path.relpath(envpath, wspath).center(80, '='))
            cmd = ENV_LIST.format(envpath=envpath)
            run_cmd(cmd)
        else:
            print(os.path.basename(envpath))


def trash(wspath):
    toremove = []
    for envpath in iter_spec(wspath):
        toremove.append(envpath)

    for p in toremove:
        print('will remove', p)

    question = "Are you sure you want to remove these? y/n (default n) > "
    prompt = raw_input(question)
    if prompt.startswith('y'):
        for p in toremove:
            print("removing", p)
            shutil.rmtree(p)
    else:
        print("cancelled")


def gui(wspath):
    import Tkinter as tk

    master = tk.Tk()

    l = tk.Label(master, text="Select a configuration")
    l.pack()

    var = tk.StringVar(master)
    var.set("")

    options = [os.path.relpath(p, wspath) for p in iter_spec(wspath)]
    option = tk.OptionMenu(master, var, *options)
    option.configure(width=max(map(len, options)))
    option.pack()

    def ok():
        master.quit()
        name = var.get()
        if not name:
            raise ActionFailed("Nothing was selected")
        print(os.path.join(wspath, name))

    button = tk.Button(master, text="OK", command=ok)
    button.pack()

    tk.mainloop()


def main():
    ap = argparse.ArgumentParser(description='conda workspace')
    ap.add_argument('-v', action='store_true', dest='verbose')
    ap.add_argument('--detail', action='store_true', dest='details')
    ap.add_argument('--root', action='store_true', dest='find_root')
    ap.add_argument('--install', action='store', dest='project_install',
                    nargs='+')
    ap.add_argument('--gui', action='store_true', dest='gui')
    ap.add_argument('--list', action='store_true', dest='list_spec')
    ap.add_argument('--trash', action='store_true', dest='trash')
    ap.add_argument('--activate', action='store', nargs=1, dest='activate')
    ns = ap.parse_args()
    # print(ns)
    if ns.verbose:
        logging.basicConfig(level=logging.INFO)

    try:
        if ns.find_root:
            print(find_root(os.curdir))

        elif ns.project_install:
            wspath = find_root(os.curdir)
            name, spec = ns.project_install[0], ns.project_install[1:]
            project_install(wspath, name, spec)

        elif ns.gui:
            wspath = find_root(os.curdir)
            gui(wspath)

        elif ns.list_spec:
            wspath = find_root(os.curdir)
            list_spec(wspath, show_details=ns.details)

        elif ns.trash:
            wspath = find_root(os.curdir)
            trash(wspath)

        elif ns.activate:
            wspath = find_root(os.curdir)
            print(os.path.join(wspath, ns.activate[0]))

        else:
            ap.print_help()

    except ActionFailed as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
