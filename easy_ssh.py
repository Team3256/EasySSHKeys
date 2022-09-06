import getpass
import os
import subprocess
import threading
import time
import webbrowser
from shutil import which


def clone_and_modify_git_config(repo_name: str, passwd: str) -> bool:
    """Clone a repo into ~/Documents/Github/<name> and modify the git config to include name and email."""
    # Clone the repo
    subprocess.Popen(
        [
            "git",
            "clone",
            f"git@github.com-{NAME_LOWER}:{repo_name}.git",
            (dr := f"{HOME_DIR}\\Documents\\Github\\{NAME}\\{repo_name.split('/')[1]}"),
        ]
    ).communicate(input=passwd.encode())
    # Update config
    print(f"{dr=}")
    p2 = subprocess.run(["git", "config", "user.name", NAME], cwd=f"{dr}")
    p3 = subprocess.run(["git", "config", "user.email", EMAIL], cwd=f"{dr}")
    return any([p2.returncode, p3.returncode])  # returncode == 0 is success


# Check if this script is running on windows
if os.name != "nt":
    print("This only works on windows")
    exit()

# Get user input
while True:
    NAME = input("Please enter your Github Username (e.g. StarDylan): ")
    REAL_NAME = input("Enter your real name on Github (e.g. Dylan Starink): ")
    NAME_LOWER = NAME.lower()
    EMAIL = input("Please enter your Github Email (e.g. dylan@starink.com): ")
    COMPUTER_NAME = "ThonkPad2"
    HOME_DIR = os.getenv("UserProfile")

    s = f"""\
    Name: {NAME}
    Lower Case Name: {NAME_LOWER}
    Real Name: {REAL_NAME}
    Email: {EMAIL}
    Computer Name: {COMPUTER_NAME}
Does this look Correct? (y/n): """

    if "y" in input(s).lower():
        break

print("\n")

# Check if the .ssh folder exists
if not os.path.isdir(f"{HOME_DIR}\\.ssh"):
    print("Making .ssh folder")
    os.mkdir(f"{HOME_DIR}\\.ssh")

# Check if ssh-keygen is installed
if which("ssh-keygen") is None:
    webbrowser.open("https://git-scm.com/download/win")  # Git comes with ssh-keygen
    exit()


# Create new ssh key, all input/output is handled by Popen
subprocess.Popen(
    [
        "ssh-keygen",
        "-C",
        f"{NAME}@{COMPUTER_NAME}",
        "-f",
        f"{HOME_DIR}\\.ssh\\id_rsa_{NAME_LOWER}",
    ]
).communicate()

# Start ssh-agent
# todo: uac set ssh-agent start type
# subprocess.Popen(["ssh-agent", "-s"]).communicate()
# Add ssh key to ssh-agent

subprocess.run(["ssh-add", f"{HOME_DIR}\\.ssh\\id_rsa_{NAME_LOWER}"])

# Copy public ssh key to clipboard
subprocess.run(
    f"type {HOME_DIR}\\.ssh\\id_rsa_{NAME_LOWER}.pub | clip",
    shell=True,
    stdout=subprocess.DEVNULL,
)
print("Public ssh key copied to clipboard\n")
time.sleep(2)

# Add new pub ssh key to github
if not webbrowser.open("https://github.com/settings/ssh/new"):
    print("Add ssh key to github: https://github.com/settings/ssh/new")
input("Press <Enter> to Continue")

# Edit ~/.ssh/config

# #<YOUR_NAME> Account
# Host github.com-<YOUR_NAME(Lowercase, One word>
#     HostName github.com
#     User git
#     IdentityFile ~/.ssh/id_rsa_<YOUR_NAME(lowercase,one word>

if os.path.isfile(f"{HOME_DIR}\\.ssh\\config"):  # Check if file exists
    with open(f"{HOME_DIR}\\.ssh\\config", "r") as f:
        ssh_config = f.read()
else:
    ssh_config = ""

if (
    f"# {NAME} Account" not in ssh_config
):  # Check if the account is already in the config
    with open(f"{HOME_DIR}\\.ssh\\config", "a") as f:
        f.write(
            f"""\
# {NAME} Account
Host github.com-{NAME_LOWER}
    Hostname github.com
    User git
    IdentityFile ~/.ssh/id_rsa_{NAME_LOWER}"""
        )

# Configure intellij
input(
    "Configure Intellij to forget your password\nFile > Settings > Appearance & Behavior > System Settings > Passwords\nSelect 'Do not save, forget passwords after restart', then click 'OK'"
)

# Multi-threaded git clones
passwd = getpass.getpass("Enter your Github ssh-key password: ")

threads = []
for repo in {
    "Team3256/FRC_Programming_2022",
    "Team3256/Alpine",
    "Team3256/T-ShirtShooter",
    "Team3256/FRC_Programming_2020",
}:
    t = threading.Thread(target=clone_and_modify_git_config, args=(repo, passwd))
    threads.append(t)
    t.start()

[t.join() for t in threads]

print(
    "\nRun: Get-Service -Name ssh-agent | Set-Service -StartupType Automatic && Start-Service ssh-agent' as a powershell admin to start ssh-agent"
)
