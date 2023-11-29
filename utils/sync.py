import atexit
import concurrent.futures
import json
import logging
import shutil
import signal
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Handle tmp directories cleanup
tmp_dirs = []


def cleanup_tmp_dirs():
    for tmp_dir in tmp_dirs:
        if tmp_dir.exists():
            shutil.rmtree(str(tmp_dir))
    logger.info("Cleaned up all temporary directories")


# Register atexit handler for cleanup on exit
atexit.register(cleanup_tmp_dirs)

# Register signal handlers for cleanup on exit
for sig in ("TERM", "HUP", "INT"):
    signal.signal(getattr(signal, "SIG" + sig), cleanup_tmp_dirs)

# Define output directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "zsh"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_latest_release(repo):
    program_name = repo.split("/")[-1]
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_dirs.append(tmp_dir)
    logger.debug("Created temporary directory for %s", repo)
    response = urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases/latest")
    tag = json.load(response)["tag_name"]

    special_cases = {
        "charmbracelet/glow": f"{program_name}_Linux_x86_64.tar.gz",
        "watchexec/watchexec": f'{program_name}-{tag.lstrip("v")}-x86_64-unknown-linux-musl.tar.xz',
        "ajeetdsouza/zoxide": f'{program_name}-{tag.lstrip("v")}-x86_64-unknown-linux-musl.tar.gz',
    }

    archive_name = special_cases.get(repo, f"{program_name}-{tag}-x86_64-unknown-linux-musl.tar.gz")
    archive_url = f"https://github.com/{repo}/releases/download/{tag}/{archive_name}"
    urllib.request.urlretrieve(archive_url, str(tmp_dir / archive_name))
    logger.debug("Downloaded %s", archive_url)
    return tmp_dir / archive_name


def extract_completion_files(archive_path):
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_dirs.append(tmp_dir)
    logger.debug("Created temporary directory for %s", archive_path)
    with tarfile.open(str(archive_path), "r:*") as tar:
        tar.extractall(path=str(tmp_dir))
    completion_files = []
    for path in tmp_dir.rglob("*"):
        if path.name == "zsh":
            new_completion_file = tmp_dir / "_watchexec"
            path.rename(new_completion_file)
            completion_files.append(new_completion_file)
            continue
        if path.suffix == ".ps1":
            continue
        if path.suffix == ".zsh":
            new_completion_file = tmp_dir / f'_{path.name.replace(".zsh", "")}'
            path.rename(new_completion_file)
            completion_files.append(new_completion_file)
        elif "/_" in str(path):
            completion_files.append(path)
    return completion_files


def get_completion_from_release(repo):
    logger.info("Starting task: get_completion_from_release for %s", repo)
    archive_path = download_latest_release(repo)
    completion_files = extract_completion_files(archive_path)
    for completion_file in completion_files:
        shutil.copy(str(completion_file), str(OUTPUT_DIR))
    logger.info("Completed task: get_completion_from_release for %s", repo)


def download_raw(raw_url, completion_file):
    logger.info("Starting task: download_raw for %s", raw_url)
    urllib.request.urlretrieve(raw_url, str(OUTPUT_DIR / completion_file))
    logger.info("Completed task: download_raw for %s", raw_url)


tasks = {
    "get_completion_from_release": [
        "sharkdp/bat",
        "sharkdp/fd",
        "charmbracelet/glow",
        "sharkdp/hyperfine",
        "lsd-rs/lsd",
        "BurntSushi/ripgrep",
        "watchexec/watchexec",
        "ducaale/xh",
        "ajeetdsouza/zoxide",
    ],
    "download_raw": [],
    "just": ["just", "--completions", "zsh"],
    "zellij": ["zellij", "setup", "--generate-completion", "zsh"],
}

with concurrent.futures.ThreadPoolExecutor() as executor:
    for repo_name in tasks["get_completion_from_release"]:
        executor.submit(get_completion_from_release, repo_name)
    for url, filename in tasks["download_raw"]:
        executor.submit(download_raw, url, filename)
    logger.info("Starting task: Running %s", " ".join(tasks["just"]))
    executor.submit(subprocess.run, tasks["just"], stdout=(OUTPUT_DIR / "_just").open("w"))
    logger.info("Completed task: Running %s", " ".join(tasks["just"]))
    logger.info("Starting task: Running %s", " ".join(tasks["zellij"]))
    executor.submit(subprocess.run, tasks["zellij"], stdout=(OUTPUT_DIR / "_zellij").open("w"))
    logger.info("Completed task: Running %s", " ".join(tasks["zellij"]))

logger.info("Sync success!")
