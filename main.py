import os
from pathlib import Path
import subprocess
import argparse
import re
import colorama

class DirectoryInfo:
    is_git_repo: bool = True
    branches: list[tuple[str,str|None,int,int]] = list() # {branch, upstream, behind, ahead}
    current_branch: str|None = None
    has_no_uncommited_changes: bool = True
    has_no_unpushed_commits: bool = True
    has_no_stashed_changes: bool = True

    def has_issues(self):
        return not (self.is_git_repo
                and self.has_no_uncommited_changes
                and self.has_no_unpushed_commits
                and self.has_no_stashed_changes)

def color_bool(b: bool) -> str:
    if b:
        return colorama.Fore.GREEN + str(b) + colorama.Fore.RESET
    else:
        return colorama.Fore.RED + str(b) + colorama.Fore.RESET

def format_branch(branch: str, upstream: str|None, behind: int, ahead: int):
    return (
        branch +
        (' -> ' + upstream if upstream != None else '') +
        (f' ahead {ahead}' if ahead != 0 else '') +
        (f' behind {behind}' if behind != 0 else '')
    )

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        prog='RepoChecker',
        description='Check git repository information and get a summary',
    )
    parser.add_argument('directory', type=Path)
    select_group = parser.add_mutually_exclusive_group()
    select_group.add_argument('-i', '--invert', action='store_true')
    select_group.add_argument('-a', '--all', action='store_true')

    args = parser.parse_args()

    abspath = args.directory.absolute()
    os.chdir(abspath)

    for dir_name in os.listdir():
        os.chdir(abspath)
        # Go into directory
        if not os.path.isdir(dir_name):
            continue
        os.chdir(dir_name)

        info = DirectoryInfo()

        # Check if git repo
        status_result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if status_result.returncode == 128:
            info.is_git_repo = False
        elif status_result.returncode != 0:
            print(colorama.Fore.RED + f'Error {status_result.returncode} in {os.getcwd()}: {status_result.stderr}' + colorama.Fore.RESET)
            continue
        else:
            # Get branches
            branch_result = subprocess.run(['git', 'branch', '-vv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if branch_result.returncode == 0:
                lines = [line.decode() for line in branch_result.stdout.splitlines()]
                branches: list[tuple[str,str|None,int,int]] = list()
                for line in lines:
                    # Branch
                    branch_match = re.search(r'(?<=^.{2}).+?(?= +[a-f\d]{7,} )', line)
                    if branch_match == None:
                        raise Exception("Undefined branch")
                    branch: str = branch_match[0]
                    # Upstream
                    upstream_match = re.search(r'(?<=\[).+?(?=(\]|:))', line)
                    upstream: str|None
                    if upstream_match == None:
                        upstream = None
                    else:
                        upstream = upstream_match[0]
                    # Behind
                    behind_match = re.search(r'(?<=behind )\d+', line)
                    behind: int
                    if behind_match == None:
                        behind = 0
                    else: 
                        behind = int(behind_match[0])
                    # Ahead
                    ahead_match = re.search(r'(?<=ahead )\d+', line)
                    ahead: int
                    if ahead_match == None:
                        ahead = 0
                    else: 
                        ahead = int(ahead_match[0])

                    # Save
                    branches.append((branch, upstream, behind, ahead))
                    if line.startswith('*'):
                        info.current_branch = branch
                info.branches = branches
            else:
                print(colorama.Fore.RED + f'Error {branch_result.returncode} in {os.getcwd()}: {branch_result.stderr}' + colorama.Fore.RESET)
                continue
            # Check uncommited changes
            lines = status_result.stdout.splitlines()
            info.has_no_uncommited_changes = lines[-1].decode() == 'nothing to commit, working tree clean'
            # Check unpushed changes
            for branch, upstream, behind, ahead in info.branches:
                if ahead > 0:
                    info.has_no_unpushed_commits = False
            # Check stashed changes
            stash_result = subprocess.run(['git', 'stash', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if stash_result.returncode == 0:
                info.has_no_stashed_changes = False
            elif stash_result.returncode == 1:
                info.has_no_stashed_changes = True
            else:
                print(colorama.Fore.RED + f'Error {stash_result.returncode} in {os.getcwd()}: {stash_result.stderr}' + colorama.Fore.RESET)
                continue

        if not args.all and (not info.has_issues() ^ args.invert):
            continue

        print()
        print(os.getcwd())
        print(colorama.Fore.LIGHTBLACK_EX + f' Is git repo: {color_bool(info.is_git_repo)}')
        if (info.is_git_repo):
            print(colorama.Fore.LIGHTBLACK_EX + ' Current branch: ' + (colorama.Fore.CYAN + info.current_branch if info.current_branch != None else colorama.Fore.RED + 'None') + colorama.Fore.RESET)
            print(colorama.Fore.LIGHTBLACK_EX + ' Branches: ' + colorama.Fore.WHITE + ''.join([f'\n  {format_branch(*branch)}' for branch in info.branches]) + colorama.Fore.RESET)
            print(colorama.Fore.LIGHTBLACK_EX + f' No uncommited changes: {color_bool(info.has_no_uncommited_changes)}')
            print(colorama.Fore.LIGHTBLACK_EX + f' No unpushed commits: {color_bool(info.has_no_unpushed_commits)}')
            print(colorama.Fore.LIGHTBLACK_EX + f' No stashed changes: {color_bool(info.has_no_stashed_changes)}')
        print()

if __name__ == '__main__':
    main()