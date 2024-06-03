# RepoChecker

Command line tool to summarize information git repositories in a directory

## Usage

```console
usage: RepoChecker [-h] [-i | -a] [-s | -r] [-d RECURSION_DEPTH] [-b] directory

Check git repository information and get a summary

positional arguments:
  directory

options:
  -h, --help            show this help message and exit
  -i, --invert
  -a, --all
  -s, --single
  -r, --recursive
  -d RECURSION_DEPTH, --recursion-depth RECURSION_DEPTH
  -b, --brief
```

## Example response

```console
C:\Users\oli\Workspaces>repochecker .

C:\Users\oli\Workspaces\Blockstates
 Is git repo: False


C:\Users\oli\Workspaces\RepoChecker
 Is git repo: True
 Current branch: None
 Branches: 
  * main -> origin/main
 No uncommited changes: False
 No unpushed commits: True
 No stashed changes: True


C:\Users\oli\Workspaces\XaeroMerge
 Is git repo: True
 Current branch: None
 Branches: 
  * main -> origin/main ahead 1
 No uncommited changes: False
 No unpushed commits: False
 No stashed changes: True
```
