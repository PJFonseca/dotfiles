import subprocess
import os

# Function to enable the required repositories
def enable_repositories():
    print("Enabling required repositories...")
    subprocess.run(["dnf", "config-manager", "--set-enabled", "epel", "--set-enabled", "remi-modular", "--set-enabled", "remi-safe"], check=True)
    print("All required repositories enabled.")

# Function to disable the repositories after the task is completed
def disable_repositories():
    print("Disabling repositories to restore system state...")
    subprocess.run(["dnf", "config-manager", "--set-disabled", "epel", "--set-disabled", "remi-modular", "--set-disabled", "remi-safe"], check=True)
    print("Repositories disabled.")

# Function to download the package and all its dependencies
def download_package_with_dependencies(package_name, download_dir):
    print(f"Downloading {package_name} and its dependencies...")
    
    # Ensure the download directory exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    try:
        # Use dnf to download the package and its dependencies, skipping broken packages
        subprocess.run([
            "dnf", "download", "--resolve", "--alldeps", "--skip-broken", "--destdir", str(download_dir), f"{package_name}*"
        ], check=True)
        print(f"Downloaded all {package_name} packages and dependencies to {download_dir}.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading packages: {e}")
        # Optionally log the error or handle it in a different way if needed

# Main function to run the process
def main():
    package_name = "php"  # Example: you can change this to any other package name (e.g., 'php-cli', 'php-fpm')
    download_dir = "/mnt/repo/rpms"  # Set your download directory (adjust the path as needed)
    
    # Enable required repositories
    enable_repositories()
    
    # Download the package and its dependencies
    download_package_with_dependencies(package_name, download_dir)
    
    # Disable repositories to restore system state
    disable_repositories()

# Run the script
if __name__ == "__main__":
    main()
