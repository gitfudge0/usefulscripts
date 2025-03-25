import subprocess
import os
import json
import sys

def get_video_info(input_file):
    """Get video information using ffprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=bit_rate',
        '-show_entries', 'format=duration,size',
        '-of', 'json',
        input_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Try to get bitrate from stream info
        try:
            bitrate = int(info['streams'][0]['bit_rate'])
        except (KeyError, IndexError, ValueError):
            # If stream bitrate is not available, calculate from file size and duration
            try:
                size_in_bits = int(info['format']['size']) * 8
                duration = float(info['format']['duration'])
                bitrate = int(size_in_bits / duration)
            except (KeyError, ValueError):
                print("Could not determine video bitrate. Using default value.")
                bitrate = 2000000  # 2 Mbps as fallback
        
        return {'bitrate': bitrate}
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error analyzing video: {e}")
        print("Is ffprobe installed and in your PATH?")
        sys.exit(1)

def compress_video(input_file, output_file, target_reduction=0.8):
    """
    Compress video to reduce file size by approximately the specified percentage
    while maintaining good quality
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Get original video info
    video_info = get_video_info(input_file)
    original_bitrate = video_info['bitrate']
    
    # Calculate target bitrate (20% of original to achieve 80% reduction)
    target_bitrate = int(original_bitrate * (1 - target_reduction))
    
    # Ensure minimum bitrate to maintain quality
    min_bitrate = 500000  # 500 kbps
    if target_bitrate < min_bitrate:
        print(f"Warning: Calculated target bitrate is very low. Setting to minimum {min_bitrate//1000} kbps.")
        target_bitrate = min_bitrate
    
    print(f"Original bitrate: {original_bitrate // 1000} kbps")
    print(f"Target bitrate: {target_bitrate // 1000} kbps")
    
    try:
        # Two-pass encoding for better quality with target bitrate
        # First pass
        first_pass_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', input_file,
            '-c:v', 'libx264',
            '-b:v', f'{target_bitrate}',
            '-pass', '1',
            '-f', 'null',
            '-an',  # No audio in first pass
            '/dev/null'  # Output to nowhere
        ]
        
        # For Windows
        if os.name == 'nt':
            first_pass_cmd[-1] = 'NUL'
        
        print("Starting first pass encoding...")
        subprocess.run(first_pass_cmd, check=True)
        
        # Second pass
        second_pass_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', input_file,
            '-c:v', 'libx264',
            '-b:v', f'{target_bitrate}',
            '-pass', '2',
            '-preset', 'slow',  # Slower preset for better compression efficiency
            '-c:a', 'aac',  # Use AAC for audio
            '-b:a', '128k',  # Audio bitrate
            output_file
        ]
        
        print("Starting second pass encoding...")
        subprocess.run(second_pass_cmd, check=True)
        
        # Calculate actual reduction
        original_size = os.path.getsize(input_file)
        compressed_size = os.path.getsize(output_file)
        reduction = (original_size - compressed_size) / original_size * 100
        
        print(f"Compression complete!")
        print(f"Original size: {original_size/1024/1024:.2f} MB")
        print(f"Compressed size: {compressed_size/1024/1024:.2f} MB")
        print(f"Reduction: {reduction:.1f}%")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        print("Is ffmpeg installed and in your PATH?")
        sys.exit(1)
    finally:
        # Clean up temporary files
        for ext in ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']:
            if os.path.exists(ext):
                os.remove(ext)

def main():
    print("Video Compression Utility")
    print("-----------------------")
    
    # Get input file path
    input_file = input("Enter the path to the input video file: ")
    
    # Get output file path
    output_file = input("Enter the path for the output compressed video: ")
    
    # Get reduction percentage
    reduction_input = input("Enter target reduction percentage (0-100, default is 80): ")
    if reduction_input.strip():
        try:
            reduction = float(reduction_input) / 100  # Convert percentage to decimal
            if reduction < 0 or reduction > 1:
                print("Invalid reduction value. Using default 80%.")
                reduction = 0.8
        except ValueError:
            print("Invalid input. Using default 80% reduction.")
            reduction = 0.8
    else:
        reduction = 0.8
    
    # Confirm settings
    print("\nCompression Settings:")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Target reduction: {reduction*100:.1f}%")
    
    confirm = input("\nProceed with compression? (y/n): ")
    if confirm.lower() not in ['y', 'yes']:
        print("Compression cancelled.")
        return
    
    compress_video(input_file, output_file, reduction)

if __name__ == '__main__':
    main()

