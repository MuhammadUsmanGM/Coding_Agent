# src/git_ops.py

from git import Repo, InvalidGitRepositoryError

class GitOps:
    def __init__(self, repo_path="."):
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.repo = Repo.init(repo_path)

    def stage_files(self, files):
        if isinstance(files, str):
            files = [files]
        self.repo.index.add(files)

    def commit(self, message):
        return self.repo.index.commit(message)

    def status(self):
        return self.repo.git.status()

    def diff(self):
        return self.repo.git.diff()

    def create_branch(self, branch_name):
        branch = self.repo.create_head(branch_name)
        branch.checkout()
        return branch
