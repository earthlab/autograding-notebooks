"""
When you create a GitHub Classroom assignment, you can provide a link to a template repository that contains information you want to provide to the students. In our case, we want to that repo to include any notebooks in the nbgrader `release` directory. This script copies notebooks from nbgrader/release, adds a readme and .gitignore, initializes a repository and pushes the repo to an (already existing) github repo.

The first argument allows you to just create the local repo, just push to github, or both.

Sample call: `make-template-repo.py create nbgrader-bootcamp assignment1`

usage: make-template-repo.py [-h] [--org_name ORG_NAME]
                             [{create,push,both}] nbgrader_dir assignment

positional arguments:
  {create,push,both}   Whether to {create} local repo, {push} to github, or
                       both
  nbgrader_dir         path to nbgrader directory
  assignment           assignment name, e.g., "2019-01-31-stability" or
                       "ea-04-bootcamp-spatial-data"

optional arguments:
  -h, --help           show this help message and exit
  --org_name ORG_NAME  name of GitHub Classroom organization; default = earth-
                       analytics-edu

TODO: This script creates the repo in the same directory as the nbgrader repo.
that is not optimal as that means you have a git repo nested in another git repo
potentially. That could be a behavior but we likely want the user to specify a location or
it places is in the same dir as the nbgrader repo (that is likely ideal?)
That could actually be a config yaml setting. 

# note that


# Create template repo for github classroom from released notebooks
# for assignment in nbgrader directory; (fails if template dir already exists)

# Template repo with name assignment-template must already exist in
# GitHub organization
"""

import sys
import os
import fnmatch
import argparse
import subprocess
import shutil


def add_gitignore(repo_name):
    """add gitignore file to template github repos

    This function adds a .gitignore file to the specified repository. The file
    is populated with ``.DStore`` and ``.ipynb_checkpoints``

    TODO: if you wanted to add additional ignore files, ... that could be a parameter

    Assumes : ??? assumes the dir is in the same directory as ?? where and how does it look.
    Parameters
    ----------
    repo_name : string
        The name of the repository that should be added


    Returns
    -------
    Writes a .gitgnore file to specified repo
    """

    filename = os.path.join(repo_name, ".gitignore")
    with open(filename, "w") as f:
        f.write(".DStore\n")
        f.write(".ipynb_checkpoints\n")


def add_readme(repo_name, assignment):
    # create a stub of a readme file for the template repo
    print("Creating readme")
    filename = os.path.join(repo_name, "readme.md")
    with open(filename, "w") as f:
        f.write("# README\n")
        f.write(
            "\nThis repository contains the notebooks for assignment {}. Complete the homework in each .ipynb notebook, commit your work, and push the changes to github. Your instructor will pull the completed assignemnt after the deadline.\n".format(
                assignment
            )
        )
        f.write(
            "\nOnce grading is complete, your instructor will push the results to a file called `feedback.html`. You will need to pull the changes to your local copy and open this file in a browser to view (github will not render html files).\n"
        )


def get_notebooks(nbgrader_dir, assignment):
    # get the list of notebooks for this assignment
    # assumes assignemnts have been released (i.e. are in release dir)
    print("Getting notebooks")
    release_dir = os.path.join(nbgrader_dir, "release", assignment)
    notebooks = []
    for file in os.listdir(release_dir):
        if fnmatch.fnmatch(file, "*.ipynb"):
            print(file)
            notebooks.append(file)
    print("Found {} notebooks".format(len(notebooks)))
    return notebooks


# does all of the local git things but does not push to github
def do_local_git_things(repo_name):
    git = ["git", "-C", repo_name]
    try:
        if not os.path.exists(os.path.join(repo_name, ".git")):
            print("initializing git repo")
            subprocess.check_output(git + ["init"])
        for file in os.listdir(repo_name):
            if fnmatch.fnmatch(file, "*.ipynb"):
                subprocess.check_call(git + ["add", file])
        subprocess.check_output(git + ["commit", "-mInitial commit"])
    except subprocess.CalledProcessError as e:
        print(e.output)
        print("One or more git actions failed; exiting")


def push_to_github(org_name, repo_name):
    # push to the github classroom org:
    # git remote add origin git@github.com:earth-analytics-edu/repo_name.git
    # git push -u origin master

    repo_url = "git@github.com:{}/{}.git".format(org_name, repo_name)
    git = ["git", "-C", repo_name]

    try:
        print("pushing to github repo {}".format(repo_url))
        subprocess.check_output(git + ["remote", "add", "origin", repo_url])
        subprocess.check_output(git + ["push", "-u", "origin", "master"])
    except subprocess.CalledProcessError as e:
        print(e.output)
        print("Git push failed")


if __name__ == "__main__":
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        help="Whether to {create} local repo, {push} to github, or both",
        choices=["create", "push", "both"],
        default="both",
        nargs="?",
    )
    parser.add_argument("nbgrader_dir", help="path to nbgrader directory")
    parser.add_argument(
        "assignment",
        help='assignment name, e.g., "2019-01-31-stability" or "ea-04-bootcamp-spatial-data"',
    )
    parser.add_argument(
        "--org_name",
        help="name of GitHub Classroom organization; default = earth-analytics-edu",
        default="earth-analytics-edu",
    )
    args = parser.parse_args()

    # notebooks = get_notebooks(args.nbgrader_dir, args.assignment)
    # cp notebooks to new dir and initialize as git repo
    assignment = args.assignment
    repo_name = assignment + "-template"
    mode = args.mode

    # Create directory and populate with files
    if mode == "create" or mode == "both":
        try:
            os.mkdir(repo_name)
            print("Creating new directory at {}".format(repo_name))
        except FileExistsError as fee:
            print("directory {} already exists; exiting".format(repo_name))
            sys.exit(1)

        # copy notebooks to repo
        print("Getting notebooks")
        release_dir = os.path.join(args.nbgrader_dir, "release", assignment)
        nbooks = 0
        for file in os.listdir(release_dir):
            if fnmatch.fnmatch(file, "*.ipynb"):
                nb = os.path.join(release_dir, file)
                print("copying {} to {}".format(nb, repo_name))
                shutil.copy(nb, repo_name)
                nbooks += 1
        print("Copied {} notebooks".format(nbooks))

        add_readme(repo_name, assignment)
        add_gitignore(repo_name)
        do_local_git_things(repo_name)

    # Push to github
    if mode == "push" or mode == "both":
        push_to_github(args.org_name, repo_name)
