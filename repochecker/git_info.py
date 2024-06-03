import os
from pathlib import Path
import subprocess
import re

class DirectoryInfo:
    branches: list[tuple[str,str|None,int,int]] = list() # {branch, upstream, behind, ahead}
    current_branch: str|None = None
    has_no_uncommited_changes: bool = True
    has_no_unpushed_commits: bool = True
    has_no_stashed_changes: bool = True

    def has_issues(self):
        return not (self.has_no_uncommited_changes
                and self.has_no_unpushed_commits
                and self.has_no_stashed_changes)

def is_repository(directory: Path = Path()) -> bool:
    return directory.joinpath('.git').is_dir()

def get_branches(directory: Path = Path()) -> list[tuple[str,str|None,int,int]]:
    # Go into directory
    original = os.getcwd()
    os.chdir(directory)

    try:
        branch_result = subprocess.run(['git', 'branch', '-vv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if branch_result.returncode == 0:
            lines = [line.decode() for line in branch_result.stdout.splitlines()]
            branches: list[tuple[str,str|None,int,int]] = list()
            for line in lines:
                # Branch
                branch_match = re.search(r'^\*? +.+?(?= +[a-f\d]{7,} )', line)
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
            return branches
        else:
            raise Exception(f'Error {branch_result.returncode} in {os.getcwd()}: {branch_result.stderr}')
    finally:
        os.chdir(original)

def has_stash(directory: Path = Path()) -> bool:
    # Go into directory
    original = os.getcwd()
    os.chdir(directory)

    try:
        stash_result = subprocess.run(['git', 'stash', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if stash_result.returncode == 0:
            return True
        elif stash_result.returncode == 1:
            return False
        else:
            raise Exception(f'Error {stash_result.returncode} in {os.getcwd()}: {stash_result.stderr}')
    finally:
        os.chdir(original)

def get_info(directory: Path = Path()) -> DirectoryInfo:
    # Go into directory
    original = os.getcwd()
    os.chdir(directory)

    try:
        info = DirectoryInfo()

        # Check if git repo
        if not is_repository():
            raise Exception(f'{directory} is not a git repository')

        # Get branches
        info.branches = get_branches()
        # Check uncommited changes
        status_result = subprocess.run(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if status_result.returncode != 0:
            raise Exception(f'Error {status_result.returncode} in {os.getcwd()}: {status_result.stderr}')

        lines = status_result.stdout.splitlines()
        info.has_no_uncommited_changes = lines[-1].decode() == 'nothing to commit, working tree clean'
        # Check unpushed changes
        for branch, upstream, behind, ahead in info.branches:
            if ahead > 0:
                info.has_no_unpushed_commits = False
        # Check stashed changes
        info.has_no_stashed_changes = not has_stash()

        return info
    finally:
        os.chdir(original)