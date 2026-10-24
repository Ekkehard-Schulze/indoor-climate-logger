"""CPython code. Intended to be run from the PC's CPython interpreter
Run this script in CircuitPython's base folder
"""

import os
import shutil
import sys
import time
from pathlib import Path

import serial
from serial.tools import list_ports

p_name = "indoor-climate-logger.py"

lib_folder_vs_prefix = "lib_cp-"  # e.g. "lib_cp-10.x"

VERBOSE = False


def merge_lib_cp(base_directory="."):
    """Reads the CircuitPython version from boot_out.txt and migrates
    the matching libraries from 'lib_cp-X.x' (e.g. lib_cp-9.x) into the
    'lib' folder. Deletes all lib_cp-* folders afterwards.
    """
    base_path = Path(base_directory)
    boot_file_path = base_path / "boot_out.txt"
    lib_target_dir = base_path / "lib"

    if not boot_file_path.exists():
        print("'boot_out.txt' not found.")
        print("Rerun this script in the base folder of your CircuitPython device. I abort.")
        sys.exit()
        return

    boot_content = boot_file_path.read_text(encoding="utf-8")

    version_keyword = "CircuitPython "
    if version_keyword not in boot_content:
        print("Aborted: CircuitPython Version token not found in 'boot_out.txt'.")
        sys.exit()
        return

    version_str = boot_content.split(version_keyword)[1].split()[0]
    major_version = version_str.split(".")[0]
    if VERBOSE:
        print(f"Identified CircuitPython Major Version: {major_version}")

    source_folder_name = f"{lib_folder_vs_prefix}{major_version}.x"
    source_folder_path = base_path / source_folder_name

    if not source_folder_path.exists():
        if VERBOSE:
            print(f"No folder '{source_folder_name}' found.")
            print("Assuming the lib/ folder is already complete. Continuing.")
        return

    # Create the 'lib' folder if it doesn't exist
    lib_target_dir.mkdir(exist_ok=True)

    print(f"Moving contents from '{source_folder_name}' to 'lib'...")

    # Iterate over all items in the source folder
    has_files = False
    for item in source_folder_path.iterdir():
        has_files = True
        target_item_path = lib_target_dir / item.name

        # If the target exists (file or folder), it is safely deleted first
        if target_item_path.exists():
            if target_item_path.is_dir():
                shutil.rmtree(target_item_path)
            else:
                target_item_path.unlink()

        # Move the file or the entire directory
        shutil.move(str(item), str(target_item_path))
        print(f" -> '{item.name}' migrated.")

    if not has_files:
        print("Notice: Source folder was already empty.")

    # Delete the now empty source folder
    try:
        shutil.rmtree(source_folder_path)
        print(f"Folder '{source_folder_name}' deleted successfully.")
    except OSError:
        print(f"Error: '{source_folder_name}' could not be deleted.")

    # Delete all remaining folders that start with the prefix
    print(f"Cleaning up alternative '{lib_folder_vs_prefix}*' folders...")
    for item in base_path.iterdir():
        if item.is_dir() and item.name.startswith(lib_folder_vs_prefix):
            shutil.rmtree(item)
            print(f" -> Removed unused folder '{item.name}'.")
    print("Library migration completed successfully!")


# ----------- main ----------------------------

err = False

merge_lib_cp()

if os.path.exists("boot.bak"):
    os.rename("boot.bak", "boot.py")
    print("\nboot.bak renamed to boot.py\n")
else:
    if VERBOSE:
        print("\nNo boot.bak found\n")
    err = True

try:
    shutil.copy(p_name, "code.py")
    print(f"{p_name} copied to code.py")
    x = input(f"\nDelete {p_name}?\nEnter 'yes' to delete: ")
    if x == "yes":
        os.remove(p_name)
except FileNotFoundError:
    if VERBOSE:
        print(f"\nNo local file '{p_name}' found to copy as code.py\n")
    # err = True


# ---------------- Hard Reset Section ---------------------------------------------------

# Target ports registration for execution

picoPorts = list(list_ports.grep("239A:80F4"))  # Adafruit Pico (CircuitPython)
picoWPorts = list(list_ports.grep("239A:8120"))  # Adafruit Pico W (CircuitPython)
pico2Ports = list(list_ports.grep("239A:8161"))  # Adafruit Pico 2 (CircuitPython)
pico2WPorts = list(list_ports.grep("239A:8162"))  # Adafruit Pico 2 W (CircuitPython)

picoPorts = picoPorts + picoWPorts + pico2Ports + pico2WPorts


pythonInject = r"""
import microcontroller
microcontroller.reset()
""".splitlines()[1:]


if not picoPorts:
    print("No compatible Raspberry Pi Pico found for resetting.")
else:
    # Fixed syntax: added missing [0] index lookup to fetch the port object details
    picoSerialPort = picoPorts[0].device
    with serial.Serial(picoSerialPort) as s:
        s.write(b"\x03")  # Interrupt the currently running script
        time.sleep(1.3)
        s.write(b"\x03")  # Send it twice to secure raw REPL state entry
        time.sleep(1.3)
        s.write(b"\x01")  # Switch over to raw REPL mode interface
        time.sleep(0.7)
        for code in pythonInject:
            s.write(bytes(code + "\r\n", "ascii"))
            time.sleep(0.05)
        time.sleep(0.25)
        s.write(b"\x04")  # Exit raw REPL interface targets and evaluate code execution

    print(f"\nRaspberry Pi Pico found and processed at {picoSerialPort}\n")
    if not err:
        print("\nboot.bak renamed to boot.py and microcontroller reset completed.\n")
    else:
        print("\nMicrocontroller hardware reset issued.\nWarning: NO boot.bak renamed to boot.py\n")
time.sleep(6)
