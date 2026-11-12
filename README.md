# File Integrity Monitor (FIM)

A host-based defensive security utility written in Python that detects unauthorized file tampering, deletions, and backdoor injections using SHA-256 cryptographic hashing.

## Key Features
- **Cryptographic Baseline Generation:** Computes and stores SHA-256 hashes for all files across target directories.
- **Tamper & Webshell Detection:** Alerts administrators when critical configuration files are altered, removed, or when unauthorized scripts are dropped into production directories.
- **Cross-Platform & Lightweight:** Built on Python's native `hashlib` module with zero heavy external dependencies.

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/Korrawit450/file-integrity-monitor.git](https://github.com/Korrawit450/file-integrity-monitor.git)
   cd file-integrity-monitor