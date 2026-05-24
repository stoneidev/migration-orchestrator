import subprocess
from pathlib import Path


class WorktreeManager:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.worktrees_dir = repo_root / ".worktrees"
        self.worktrees_dir.mkdir(exist_ok=True)

    def get_branch_name(self, page_id: str, worker_type: str) -> str:
        return f"wt/{worker_type}/{page_id}"

    def _get_worktree_path(self, page_id: str, worker_type: str) -> Path:
        safe_id = page_id.replace(".", "_")
        return self.worktrees_dir / f"{worker_type}-{safe_id}"

    def create(self, page_id: str, worker_type: str) -> Path:
        wt_path = self._get_worktree_path(page_id, worker_type)
        branch = self.get_branch_name(page_id, worker_type)

        if wt_path.exists():
            self.remove(page_id, worker_type)

        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(wt_path)],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            check=True,
        )

        return wt_path

    def remove(self, page_id: str, worker_type: str) -> None:
        wt_path = self._get_worktree_path(page_id, worker_type)

        if wt_path.exists():
            subprocess.run(
                ["git", "worktree", "remove", str(wt_path), "--force"],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
            )

        branch = self.get_branch_name(page_id, worker_type)
        subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )
