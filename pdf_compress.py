import os
import subprocess


def compress_pdf_ghostscript(input_file_path, output_file_path, power=3):
    """
    Compress PDF using Ghostscript.
    power: compression level (0-4), higher means more compression but potentially lower quality
    """
    quality = {0: "/default", 1: "/prepress", 2: "/printer", 3: "/ebook", 4: "/screen"}

    # Ensure the power value is valid
    if power not in quality:
        power = 3

    # Command for Ghostscript compression
    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={quality[power]}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_file_path}",
        input_file_path,
    ]

    try:
        subprocess.call(cmd)
        print(f"Compressed PDF saved to {output_file_path}")
        return True
    except Exception as e:
        print(f"Error compressing PDF with Ghostscript: {e}")
        return False


def check_ghostscript():
    """Check if Ghostscript is installed"""
    try:
        subprocess.run(
            ["gs", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except FileNotFoundError:
        return False


def get_input_file():
    """Get input file path interactively"""
    while True:
        file_path = input("Enter the path to the PDF file: ").strip()
        if file_path.lower() == "q":
            return None

        if os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
            return file_path
        else:
            print("File not found or not a PDF. Please try again or enter 'q' to quit.")


def get_output_file(input_file):
    """Generate output file path or get it interactively"""
    filename, ext = os.path.splitext(input_file)
    default_output = f"{filename}_compressed{ext}"

    print(f"\nDefault output file: {default_output}")
    choice = input("Use this file? (y/n) [y]: ").strip().lower()

    if choice == "" or choice == "y":
        return default_output
    else:
        while True:
            output_path = input("Enter the output file path: ").strip()
            if output_path.lower().endswith(".pdf"):
                return output_path
            else:
                print("Please enter a valid PDF file path.")


def get_compression_level():
    """Get compression level interactively"""
    print("\nSelect compression level:")
    print("0: Default (lowest compression, highest quality)")
    print("1: Prepress (high quality, less compression)")
    print("2: Printer (medium quality, medium compression)")
    print("3: Ebook (medium-low quality, better compression)")
    print("4: Screen (lowest quality, highest compression)")

    while True:
        choice = input("\nEnter your choice (0-4) [3]: ").strip()
        if choice == "":
            return 3

        try:
            level = int(choice)
            if 0 <= level <= 4:
                return level
            else:
                print("Please enter a number between 0 and 4.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    print("PDF Compression Tool")
    print("====================")
    print(
        "This tool will help you reduce the size of your PDF files using Ghostscript."
    )
    print("Enter 'q' at any prompt to quit.\n")

    # Check if Ghostscript is installed
    if not check_ghostscript():
        print("Error: Ghostscript is not installed or not found in PATH.")
        print("Please install Ghostscript and try again.")
        return

    # Get input file
    input_file = get_input_file()
    if input_file is None:
        print("Exiting program.")
        return

    # Get output file
    output_file = get_output_file(input_file)

    # Get compression level
    power = get_compression_level()

    # Calculate original file size
    original_size = os.path.getsize(input_file) / 1024 / 1024  # in MB
    print(f"\nOriginal size: {original_size:.2f} MB")
    print("Compressing PDF...")

    # Compress PDF
    success = compress_pdf_ghostscript(input_file, output_file, power)

    # Check results
    if success and os.path.exists(output_file):
        compressed_size = os.path.getsize(output_file) / 1024 / 1024  # in MB
        reduction = (1 - compressed_size / original_size) * 100

        print(f"Original size: {original_size:.2f} MB")
        print(f"Compressed size: {compressed_size:.2f} MB")
        print(f"Reduction: {reduction:.1f}%")

        if compressed_size > original_size:
            print("\nWarning: The compressed file is larger than the original.")
            print("This can happen with already optimized PDFs.")


if __name__ == "__main__":
    main()
