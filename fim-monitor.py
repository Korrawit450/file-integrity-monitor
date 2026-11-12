import sys
import os
import json
import hashlib
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

BASELINE_FILE = "baseline.json"
IGNORE_FILES = {BASELINE_FILE, ".DS_Store"}
IGNORE_DIRS = {".git", "__pycache__", "venv", ".venv"}

def calculate_sha256(file_path: str) -> str:
    """คำนวณค่าแฮช SHA-256"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def scan_target_directory(target_dir: str) -> dict:
    """สแกนไฟล์ทั้งหมดในโฟลเดอร์และเก็บค่า SHA-256"""
    file_hashes = {}
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file in IGNORE_FILES:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, target_dir)
            file_hash = calculate_sha256(full_path)
            if file_hash:
                file_hashes[rel_path] = file_hash
    return file_hashes

def create_baseline(target_dir: str):
    print(f"\n{Fore.CYAN}[*] Generating new SHA-256 baseline for: {target_dir}{Style.RESET_ALL}")
    hashes = scan_target_directory(target_dir)
    
    baseline_data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "target_directory": os.path.abspath(target_dir),
        "files": hashes
    }

    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=4)

    print(f"{Fore.GREEN}[+] Baseline created successfully ({len(hashes)} files indexed).")
    print(f"[+] Saved to: {BASELINE_FILE}\n")

def verify_integrity(target_dir: str):
    if not os.path.exists(BASELINE_FILE):
        print(f"{Fore.RED}[!] Baseline file '{BASELINE_FILE}' not found. Run 'init' mode first.")
        sys.exit(1)

    with open(BASELINE_FILE, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)

    stored_hashes = baseline_data.get("files", {})
    current_hashes = scan_target_directory(target_dir)

    print(f"\n{Fore.CYAN}=== File Integrity Audit Report ==={Style.RESET_ALL}")
    print(f"Target Directory : {os.path.abspath(target_dir)}")
    print(f"Baseline Created : {baseline_data.get('timestamp')}\n")

    modified = []
    added = []
    deleted = []

    for rel_path, current_hash in current_hashes.items():
        if rel_path not in stored_hashes:
            added.append(rel_path)
        elif stored_hashes[rel_path] != current_hash:
            modified.append(rel_path)

    for rel_path in stored_hashes:
        if rel_path not in current_hashes:
            deleted.append(rel_path)

    if not (modified or added or deleted):
        print(f"{Fore.GREEN}[+] STATUS: INTACT. No unauthorized file modifications detected.{Style.RESET_ALL}\n")
        return

    for f_path in modified:
        print(f"  {Fore.RED}[MODIFIED]{Style.RESET_ALL} {f_path}")
    for f_path in added:
        print(f"  {Fore.YELLOW}[NEW FILE]{Style.RESET_ALL} {f_path}")
    for f_path in deleted:
        print(f"  {Fore.MAGENTA}[DELETED] {Style.RESET_ALL} {f_path}")

    print("-" * 60)
    print(f"Summary: {Fore.RED}{len(modified)} Modified{Style.RESET_ALL}, "
          f"{Fore.YELLOW}{len(added)} Added{Style.RESET_ALL}, "
          f"{Fore.MAGENTA}{len(deleted)} Deleted{Style.RESET_ALL}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("init", "check"):
        print("Usage:")
        print("  python fim_monitor.py init <directory>   # Create cryptographic baseline")
        print("  python fim_monitor.py check <directory>  # Verify file integrity against baseline")
        sys.exit(1)

    mode = sys.argv[1]
    target = sys.argv[2]

    if not os.path.isdir(target):
        print(f"{Fore.RED}[!] Error: Directory '{target}' does not exist.")
        sys.exit(1)

    if mode == "init":
        create_baseline(target)
    elif mode == "check":
        verify_integrity(target)