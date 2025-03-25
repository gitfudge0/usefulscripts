#!/usr/bin/env python3
import os
import sys
import platform
import subprocess

def get_os_type():
    """Detect the operating system type"""
    system = platform.system().lower()
    
    if system == "darwin":
        return "macos"
    elif system == "linux":
        # Check for different Linux distributions
        try:
            with open("/etc/os-release") as f:
                os_info = f.read()
                if "ubuntu" in os_info.lower() or "debian" in os_info.lower():
                    return "debian"
                elif "fedora" in os_info.lower() or "centos" in os_info.lower() or "rhel" in os_info.lower():
                    return "fedora"
                elif "arch" in os_info.lower() or "manjaro" in os_info.lower():
                    return "arch"
                else:
                    return "linux"
        except:
            return "linux"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

def run_command(command, description):
    """Run a shell command with proper error handling"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command output: {e.stderr}")
        return False

def install_python_packages(os_type):
    """Install required Python packages using pip"""
    packages = ["pillow"]
    
    # Check if pip is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("Error: pip is not installed or not working.")
        if os_type == "windows":
            print("For Windows:")
            print("  1. Download get-pip.py from https://bootstrap.pypa.io/get-pip.py")
            print("  2. Run: python get-pip.py")
        elif os_type == "debian":
            print("Run: sudo apt-get install python3-pip")
        elif os_type == "fedora":
            print("Run: sudo dnf install python3-pip")
        elif os_type == "arch":
            print("Run: sudo pacman -Sy python-pip")
        elif os_type == "macos":
            print("Run: brew install python3")
        print("Then try running this script again.")
        return False
    
    # Install packages
    for package in packages:
        # For Windows, avoid using system Python and prefer user installation
        if os_type == "windows":
            command = f"{sys.executable} -m pip install --user {package}"
        else:
            command = f"{sys.executable} -m pip install {package}"
        
        if not run_command(command, f"Installing {package}"):
            return False
    
    return True

def install_ghostscript(os_type):
    """Install Ghostscript based on OS type"""
    if os_type == "macos":
        # Check if Homebrew is installed
        brew_check = subprocess.run("which brew", shell=True, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if brew_check.returncode != 0:
            print("Homebrew is not installed. Installing Homebrew...")
            brew_install = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            if not run_command(brew_install, "Installing Homebrew"):
                print("Failed to install Homebrew. Please install it manually.")
                return False
        
        return run_command("brew install ghostscript", "Installing Ghostscript")
    
    elif os_type == "debian":
        return run_command("sudo apt-get update && sudo apt-get install -y ghostscript", 
                          "Installing Ghostscript")
    
    elif os_type == "fedora":
        return run_command("sudo dnf install -y ghostscript", "Installing Ghostscript")
    
    elif os_type == "arch":
        return run_command("sudo pacman -Sy --noconfirm ghostscript", "Installing Ghostscript")
    
    elif os_type == "windows":
        print("For Windows, please download and install Ghostscript from:")
        print("https://www.ghostscript.com/download/gsdnld.html")
        print("\nInstallation instructions:")
        print("1. Download the installer for the latest version")
        print("2. Run the installer and follow the prompts")
        print("3. Make sure to select 'Add Ghostscript to path for all users' during installation")
        print("4. After installation, restart your command prompt/terminal")
        return True
    
    else:
        print("Unsupported OS for automatic Ghostscript installation.")
        print("Please install Ghostscript manually for your system.")
        return False

def install_ffmpeg(os_type):
    """Install FFmpeg based on OS type"""
    if os_type == "macos":
        # Check if Homebrew is installed
        brew_check = subprocess.run("which brew", shell=True, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if brew_check.returncode != 0:
            print("Homebrew is not installed. Please install it first.")
            return False
        
        return run_command("brew install ffmpeg", "Installing FFmpeg")
    
    elif os_type == "debian":
        return run_command("sudo apt-get update && sudo apt-get install -y ffmpeg", 
                          "Installing FFmpeg")
    
    elif os_type == "fedora":
        return run_command("sudo dnf install -y ffmpeg", "Installing FFmpeg")
    
    elif os_type == "arch":
        return run_command("sudo pacman -Sy --noconfirm ffmpeg", "Installing FFmpeg")
    
    elif os_type == "windows":
        print("For Windows, please download and install FFmpeg:")
        print("\nMethod 1: Using Chocolatey (Recommended if you have Chocolatey):")
        print("  1. Open PowerShell as Administrator")
        print("  2. Run: choco install ffmpeg")
        print("\nMethod 2: Manual Installation:")
        print("  1. Download from: https://ffmpeg.org/download.html")
        print("  2. Extract the zip file to a permanent location (e.g., C:\\ffmpeg)")
        print("  3. Add to PATH:")
        print("     a. Right-click on 'This PC' or 'My Computer' and select 'Properties'")
        print("     b. Click on 'Advanced system settings'")
        print("     c. Click the 'Environment Variables' button")
        print("     d. Under 'System variables', find and select 'Path', then click 'Edit'")
        print("     e. Click 'New' and add the path to the bin folder (e.g., C:\\ffmpeg\\bin)")
        print("     f. Click OK on all dialogs")
        print("  4. Restart any open command prompts")
        return True
    
    else:
        print("Unsupported OS for automatic FFmpeg installation.")
        print("Please install FFmpeg manually for your system.")
        return False

def check_dependencies(os_type):
    """Check if dependencies are already installed"""
    dependencies = {
        "ghostscript": "gs --version",
        "ffmpeg": "ffmpeg -version",
    }
    
    results = {}
    for dep_name, check_cmd in dependencies.items():
        try:
            subprocess.run(check_cmd, shell=True, check=True, 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✓ {dep_name} is already installed")
            results[dep_name] = True
        except:
            print(f"✗ {dep_name} is not installed")
            results[dep_name] = False
    
    return results

def main():
    print("Compression Utilities - Dependency Installer")
    print("===========================================")
    
    # Detect OS
    os_type = get_os_type()
    print(f"Detected OS: {os_type}")
    
    if os_type == "unknown":
        print("Error: Unable to determine your operating system.")
        print("Please install dependencies manually.")
        return
    
    # Check existing dependencies
    print("\nChecking existing dependencies...")
    dep_status = check_dependencies(os_type)
    
    # Ask for confirmation
    print("\nThe following dependencies will be installed if missing:")
    print("1. Python packages: Pillow")
    if not dep_status.get("ghostscript", False):
        print("2. Ghostscript (for PDF compression)")
    if not dep_status.get("ffmpeg", False):
        print("3. FFmpeg (for video compression)")
    
    proceed = input("\nDo you want to proceed with installation? (y/n) [y]: ").strip().lower()
    if proceed not in ["", "y", "yes"]:
        print("Installation cancelled.")
        return
    
    # Install Python packages
    print("\nInstalling required Python packages...")
    if not install_python_packages(os_type):
        print("Failed to install some Python packages.")
    
    # Install Ghostscript if needed
    if not dep_status.get("ghostscript", False):
        print("\nInstalling Ghostscript...")
        if not install_ghostscript(os_type):
            print("Failed to install Ghostscript automatically.")
            if os_type != "windows":
                print("Please try to install it manually using your system's package manager.")
    
    # Install FFmpeg if needed
    if not dep_status.get("ffmpeg", False):
        print("\nInstalling FFmpeg...")
        if not install_ffmpeg(os_type):
            print("Failed to install FFmpeg automatically.")
            if os_type != "windows":
                print("Please try to install it manually using your system's package manager.")
    
    # Final check
    print("\nVerifying installations...")
    final_status = check_dependencies(os_type)
    
    # Check Python dependencies
    try:
        import PIL
        pillow_installed = True
    except ImportError:
        pillow_installed = False
    
    all_installed = all(final_status.values()) and pillow_installed
    
    if all_installed:
        print("\nAll dependencies have been successfully installed!")
        print("You can now use the following compression utilities:")
        print("- pdf_compress.py - For compressing PDF files")
        print("- image_compress.py - For compressing image files")
        print("- video_compress.py - For compressing video files")
    else:
        print("\nSome dependencies could not be installed automatically.")
        print("Please install the missing dependencies manually:")
        
        if not pillow_installed:
            print("- Pillow: pip install pillow")
        if not final_status.get("ghostscript", False):
            print("- Ghostscript: Required for PDF compression")
        if not final_status.get("ffmpeg", False):
            print("- FFmpeg: Required for video compression")

if __name__ == "__main__":
    main()