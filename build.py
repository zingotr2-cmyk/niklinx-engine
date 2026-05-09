#!/usr/bin/env python3
"""
DRO Build System — Source code protection & packaging.

This script uses PyArmor to obfuscate the Python source code,
creating a tamper-resistant, redistributable package.

Usage:
    python build.py          # Full build (obfuscate + package)
    python build.py obfuscate  # Obfuscate only
    python build.py package    # Package only
    python build.py clean      # Clean build artifacts
"""

import sys
import shutil
import subprocess
from pathlib import Path


# Configuration
PROJECT_NAME = "dro"
VERSION = "2.0.0"
BUILD_DIR = Path("dist")
OBFUSCATE_DIR = BUILD_DIR / "obfuscated"
PACKAGE_DIR = BUILD_DIR / PROJECT_NAME
ENTRY_POINTS = ["main.py", "config.py", "licensing.py"]
MODULES = ["app", "data"]
EXCLUDES = ["__pycache__", "*.pyc", ".env", "node_modules", "dist"]


def banner(text: str):
    width = 60
    print(f"\n{'=' * width}")
    print(f"  {text}")
    print(f"{'=' * width}\n")


def check_dependencies():
    """Ensure required build tools are installed."""
    missing = []
    try:
        import pyarmor
        print("  ✓ PyArmor found")
    except ImportError:
        missing.append("pyarmor")
    
    try:
        import PyInstaller
        print("  ✓ PyInstaller found")
    except ImportError:
        missing.append("pyinstaller")
    
    if missing:
        print(f"\n  Installing missing dependencies: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("  ✓ Dependencies installed")


def clean():
    """Remove build artifacts."""
    banner("Cleaning Build Artifacts")
    
    paths = [
        BUILD_DIR,
        Path("__pycache__"),
        *Path(".").glob("**/__pycache__"),
        *Path(".").glob("**/*.pyc"),
        *Path(".").glob("**/*.pyo"),
    ]
    
    for p in paths:
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink()
            print(f"  ✗ Removed: {p}")
    
    print("  ✓ Clean complete")


def obfuscate():
    """Obfuscate Python source code with PyArmor."""
    banner("Obfuscating Source Code with PyArmor")
    
    OBFUSCATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Collect all Python files to obfuscate
    files = []
    for pattern in ENTRY_POINTS:
        p = Path(pattern)
        if p.exists():
            files.append(str(p))
    
    for module in MODULES:
        p = Path(module)
        if p.exists() and p.is_dir():
            for py_file in p.rglob("*.py"):
                if not any(ex in str(py_file) for ex in EXCLUDES):
                    files.append(str(py_file))
    
    print(f"  Found {len(files)} files to obfuscate")
    
    # Run PyArmor
    cmd = [
        sys.executable, "-m", "pyarmor", "obfuscate",
        "--output", str(OBFUSCATE_DIR),
        "--recursive",
        "--exclude", *[f"*/{e}" for e in EXCLUDES],
        *files,
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Obfuscation complete → {OBFUSCATE_DIR}")
        else:
            print(f"  ✗ Obfuscation failed: {result.stderr[:200]}")
            # Fall back to copying source files
            fallback_obfuscate()
    except Exception as e:
        print(f"  ✗ Error: {e}")
        fallback_obfuscate()


def fallback_obfuscate():
    """Fallback: copy source files if PyArmor fails."""
    print("  → Using fallback: copying source files")
    
    for pattern in ENTRY_POINTS:
        p = Path(pattern)
        if p.exists():
            dest = OBFUSCATE_DIR / p
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            print(f"  ✓ {p} → {dest}")
    
    for module in MODULES:
        p = Path(module)
        if p.exists() and p.is_dir():
            dest = OBFUSCATE_DIR / module
            shutil.copytree(p, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"  ✓ {module}/ → {dest}/")
    
    print("  ✓ Fallback complete")


def package():
    """Package obfuscated code into distributable."""
    banner("Packaging Distribution")
    
    if not OBFUSCATE_DIR.exists():
        print("  ✗ No obfuscated code found. Run 'build.py obfuscate' first.")
        return
    
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy obfuscated code
    for item in OBFUSCATE_DIR.iterdir():
        dest = PACKAGE_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)
    
    # Copy static files
    for item in Path("static").rglob("*"):
        if item.is_file():
            dest = PACKAGE_DIR / "static" / item.relative_to("static")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    
    # Copy data
    for item in Path("data").rglob("*"):
        if item.is_file():
            dest = PACKAGE_DIR / "data" / item.relative_to("data")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    
    # Copy config files
    for item in [".env.example", "requirements.txt", "README.md"]:
        p = Path(item)
        if p.exists():
            shutil.copy2(p, PACKAGE_DIR / p.name)
    
    # Create launcher scripts
    _create_launcher()
    
    print(f"\n  ✓ Package created at: {PACKAGE_DIR}")
    print(f"  ✓ Size: {sum(f.stat().st_size for f in PACKAGE_DIR.rglob('*') if f.is_file()) / 1024:.1f} KB")


def _create_launcher():
    """Create platform-specific launchers."""
    # Windows launcher
    bat_content = """@echo off
title DRO - Agentic Commerce Engine
python main.py %*
pause
"""
    (PACKAGE_DIR / "run.bat").write_text(bat_content)
    
    # PowerShell launcher
    ps_content = """#!/usr/bin/env pwsh
Write-Host "🚀 DRO - Agentic Commerce Engine v{VERSION}" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  python main.py server     - Start API server"
Write-Host "  python main.py dashboard  - Start Streamlit dashboard"
Write-Host "  python main.py doctor     - Run diagnostics"
Write-Host ""
$cmd = Read-Host "Enter command (or 'server')"
if (-not $cmd) { $cmd = "server" }
python main.py $cmd
""".format(VERSION=VERSION)
    (PACKAGE_DIR / "run.ps1").write_text(ps_content)


def print_tree(path: Path, prefix: str = ""):
    """Print directory tree."""
    items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        if item.is_dir():
            print(f"{prefix}{connector}{item.name}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(item, next_prefix)
        else:
            print(f"{prefix}{connector}{item.name} ({item.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if command == "clean":
        clean()
    elif command == "obfuscate":
        check_dependencies()
        obfuscate()
    elif command == "package":
        package()
        print(f"\n  📦 Package structure:")
        print_tree(PACKAGE_DIR)
    else:  # full build
        clean()
        check_dependencies()
        obfuscate()
        package()
        
        print(f"\n  {'=' * 60}")
        print(f"  ✅ Build Complete: {PROJECT_NAME} v{VERSION}")
        print(f"  {'=' * 60}")
        print(f"\n  📦 Output: {PACKAGE_DIR}/")
        print(f"\n  To distribute:")
        print(f"    1. Zip the '{PACKAGE_DIR}' directory")
        print(f"    2. Include .env.example (rename to .env)")
        print(f"    3. Share with your customers!")
        print(f"\n  {'=' * 60}\n")
