import os
import subprocess
from pathlib import Path

# Configuration
REPO_DIR = "/mnt/repo"
RPM_DIR = Path(REPO_DIR) / "rpms"
REPO_ARCHIVE = "/mnt/repo.tar.gz"
REPO_LIST = ["remi-modular", "epel"]
OPTIONAL_REPOS = []

# Function to check if a command exists
def command_exists(cmd):
    return subprocess.run(["which", cmd], capture_output=True, text=True).returncode == 0

# Function to check if a repository is enabled
def is_repo_enabled(repo_name):
    result = subprocess.run(["dnf", "repolist", "--enabled"], capture_output=True, text=True)
    return repo_name in result.stdout

# Function to enable repositories if they are missing
def enable_repositories():
    print("Enabling required repositories...")

    # Enable EPEL manually for Fedora
    epel_repo_content = """
[epel]
name=Extra Packages for Enterprise Linux 9 - $basearch
baseurl=https://dl.fedoraproject.org/pub/epel/9/Everything/$basearch/
enabled=1
gpgcheck=0
"""
    with open("/etc/yum.repos.d/epel.repo", "w") as f:
        f.write(epel_repo_content)

    # Manually configure Remi repository for Fedora
    remi_repo_content = """
[remi]
name=Remi Repository for RHEL/CentOS/Fedora
baseurl=https://rpms.remirepo.net/enterprise/remi/9.5/fedora/$basearch/
enabled=1
gpgcheck=0
"""
    with open("/etc/yum.repos.d/remi.repo", "w") as f:
        f.write(remi_repo_content)

    print("All required repositories enabled.")

# Function to disable repositories after execution
def disable_repositories():
    print("Disabling repositories to restore system state...")

    subprocess.run(["dnf", "config-manager", "--set-disabled", "epel"], check=True)
    subprocess.run(["dnf", "config-manager", "--set-disabled", "remi"], check=True)

    print("Repositories disabled.")

# Function to sync repositories
def sync_repositories(repo_list, repo_dir):
    for repo in repo_list:
        repo_path = Path(repo_dir) / repo
        repo_path.mkdir(parents=True, exist_ok=True)

        print(f"Syncing repository: {repo}")
        subprocess.run([
            "dnf", "reposync", "--repo", repo, "--download-metadata", "--download-path", str(repo_path)
        ], check=True)

    print("Repositories synced successfully.")

# Function to create a local repository
def create_local_repo(repo_dir):
    subprocess.run(["dnf", "install", "-y", "createrepo"], check=True)
    subprocess.run(["createrepo", str(repo_dir)], check=True)

    repo_file_content = f"""
[my_local_repo]
name=My Local Repo
baseurl=file://{repo_dir}
enabled=1
gpgcheck=0
"""
    with open(Path(repo_dir) / "my_local_repo.repo", "w") as f:
        f.write(repo_file_content)

    print("Local repo created.")

# Function to package the repo for transfer
def package_repo(repo_dir, archive_path):
    subprocess.run(["tar", "-czf", archive_path, "-C", str(Path(repo_dir).parent), str(Path(repo_dir).name)], check=True)
    print(f"Repository archived to {archive_path}")

# Main execution
def main():
    enable_repositories()  # Enable repositories before syncing

    try:
        sync_repositories(REPO_LIST, RPM_DIR)  # Sync the entire repository
        create_local_repo(RPM_DIR)  # Create a local repository for offline use
        package_repo(REPO_DIR, REPO_ARCHIVE)  # Package repo for transfer
        print(f"Repo is ready at {REPO_ARCHIVE}. Transfer it to the offline machine.")

    finally:
        disable_repositories()  # Disable repositories after execution

if __name__ == "__main__":
    main()
