import os
import sys
from PIL import Image

def check_pillow():
    """Check if Pillow is installed"""
    try:
        import PIL
        return True
    except ImportError:
        return False

def compress_image(input_file_path, output_file_path, target_reduction=0.8):
    """
    Compress an image file to reduce size while maintaining maximum quality
    
    input_file_path: Path to the input image file
    output_file_path: Path to save the compressed image
    target_reduction: Target size reduction (0.0-1.0, default 0.8 for 80% reduction)
    """
    try:
        # Open the image
        img = Image.open(input_file_path)
        
        # Get the original format (jpg, png, etc)
        img_format = img.format
        
        # Calculate initial quality based on format
        if img_format == 'JPEG':
            quality = 95  # Start with high quality for JPEG
            output_format = 'JPEG'
        elif img_format == 'PNG':
            # For PNG, we'll try to convert to JPEG if it's not transparent
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # Image has transparency, keep as PNG with compression level 6
                quality = 85
                output_format = 'PNG'
            else:
                # No transparency, convert to JPEG
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                quality = 95
                output_format = 'JPEG'
                # Change extension to jpg if converting from PNG to JPEG
                if output_file_path.lower().endswith('.png'):
                    output_file_path = os.path.splitext(output_file_path)[0] + '.jpg'
                    print(f"Converting PNG to JPEG. New output file: {output_file_path}")
        else:
            # For other formats, try to maintain original format with high quality
            quality = 95
            output_format = img_format
        
        # Save with initial high quality to get baseline
        img.save(output_file_path, format=output_format, quality=quality, optimize=True)
        
        # Calculate current reduction
        original_size = os.path.getsize(input_file_path)
        current_size = os.path.getsize(output_file_path)
        current_reduction = (original_size - current_size) / original_size
        
        # Binary search to find optimal quality that meets target reduction
        min_quality = 5   # Minimum acceptable quality
        max_quality = 95  # Maximum quality
        
        # If we haven't reached target reduction, gradually reduce quality
        if current_reduction < target_reduction and output_format == 'JPEG':
            while max_quality - min_quality > 2 and current_reduction < target_reduction:
                # Try a quality in the middle
                quality = (min_quality + max_quality) // 2
                
                # Save with new quality
                img.save(output_file_path, format=output_format, quality=quality, optimize=True)
                
                # Check new reduction
                current_size = os.path.getsize(output_file_path)
                current_reduction = (original_size - current_size) / original_size
                
                # Adjust search range
                if current_reduction < target_reduction:
                    # Need more reduction, lower quality
                    max_quality = quality
                else:
                    # Reduction is good, try to increase quality
                    min_quality = quality
        
        # Return compression statistics
        return {
            'original_size': original_size,
            'compressed_size': os.path.getsize(output_file_path),
            'reduction_percent': current_reduction * 100,
            'final_quality': quality,
            'output_format': output_format,
            'output_path': output_file_path
        }
        
    except Exception as e:
        print(f"Error compressing image: {e}")
        return None

def get_input_file():
    """Get input file path interactively"""
    while True:
        file_path = input("Enter the path to the image file: ").strip()
        if file_path.lower() == "q":
            return None
        
        if os.path.exists(file_path):
            # Check if it's an image file
            img_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
            if any(file_path.lower().endswith(ext) for ext in img_extensions):
                return file_path
            else:
                print("File does not appear to be a supported image format.")
        else:
            print("File not found. Please try again or enter 'q' to quit.")

def get_output_file(input_file):
    """Generate output file path or get it interactively"""
    filename, ext = os.path.splitext(input_file)
    default_output = f"{filename}_compressed{ext}"
    
    print(f"\nDefault output file: {default_output}")
    choice = input("Use this file? (y/n) [y]: ").strip().lower()
    
    if choice == "" or choice == "y":
        return default_output
    else:
        output_path = input("Enter the output file path: ").strip()
        return output_path

def get_reduction_percentage():
    """Get target reduction percentage interactively"""
    print("\nSelect target file size reduction:")
    print("The default is 80% reduction (file will be ~20% of original size)")
    
    while True:
        choice = input("\nEnter target reduction percentage (1-99) [80]: ").strip()
        if choice == "":
            return 0.8
        
        try:
            percentage = float(choice)
            if 1 <= percentage <= 99:
                return percentage / 100
            else:
                print("Please enter a number between 1 and 99.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    print("Image Compression Tool")
    print("=====================")
    print("This tool will compress your images while trying to maintain maximum quality.")
    print("Enter 'q' at any prompt to quit.\n")
    
    # Check if Pillow is installed
    if not check_pillow():
        print("Error: Pillow library is not installed.")
        print("Please install it with: pip install Pillow")
        return
    
    # Get input file
    input_file = get_input_file()
    if input_file is None:
        print("Exiting program.")
        return
    
    # Get output file
    output_file = get_output_file(input_file)
    
    # Get target reduction percentage
    target_reduction = get_reduction_percentage()
    
    # Calculate original file size
    original_size = os.path.getsize(input_file) / 1024  # in KB
    print(f"\nOriginal size: {original_size:.2f} KB")
    print("Compressing image...")
    
    # Compress image
    result = compress_image(input_file, output_file, target_reduction)
    
    # Check results
    if result:
        compressed_size = result['compressed_size'] / 1024  # in KB
        reduction = result['reduction_percent']
        
        print(f"\nOriginal size: {original_size:.2f} KB")
        print(f"Compressed size: {compressed_size:.2f} KB")
        print(f"Reduction: {reduction:.1f}%")
        print(f"Output format: {result['output_format']}")
        
        if compressed_size > original_size:
            print("\nWarning: The compressed file is larger than the original.")
            print("This can happen with already optimized images or specific image types.")

if __name__ == "__main__":
    main()