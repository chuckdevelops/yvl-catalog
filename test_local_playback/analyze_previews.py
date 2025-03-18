#!/usr/bin/env python3
"""
Utility script to analyze the actual audio content of preview files
to identify any duplications or encoding issues.
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Set up environment
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings

# Configuration
PREVIEW_DIR = os.path.join(settings.MEDIA_ROOT, 'previews')
OUTPUT_FILE = "preview_analysis.json"
AUDIO_SAMPLE_DIR = "audio_samples"

# Create output directory
os.makedirs(AUDIO_SAMPLE_DIR, exist_ok=True)

def extract_audio_sample(input_file, output_file, start_time=5, duration=3):
    """Extract a raw audio sample from the input file for content comparison"""
    try:
        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-ss', str(start_time),  # Start at specified time
            '-t', str(duration),     # Sample duration
            '-c:a', 'pcm_s16le',     # Use uncompressed PCM
            '-f', 'wav',             # Output as WAV
            output_file
        ]
        subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        return True
    except Exception as e:
        print(f"Error extracting audio sample from {input_file}: {str(e)}")
        return False

def calculate_audio_hash(file_path):
    """Calculate an MD5 hash of the file content"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {str(e)}")
        return None

def get_audio_properties(file_path):
    """Get audio properties using ffprobe"""
    try:
        # Get stream and format info in JSON format
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        output = subprocess.check_output(cmd, text=True)
        data = json.loads(output)
        
        # Extract the relevant audio properties
        properties = {}
        
        # Get stream properties (codec, sample rate, etc.)
        if 'streams' in data:
            for stream in data['streams']:
                if stream.get('codec_type') == 'audio':
                    properties['codec'] = stream.get('codec_name')
                    properties['sample_rate'] = int(stream.get('sample_rate', 0))
                    properties['channels'] = stream.get('channels')
                    properties['bitrate'] = int(stream.get('bit_rate', 0)) if stream.get('bit_rate') else None
                    break
        
        # Get format properties (duration, overall bitrate)
        if 'format' in data:
            properties['format'] = data['format'].get('format_name')
            properties['duration'] = float(data['format'].get('duration', 0))
            
            # Use format bitrate if stream bitrate is not available
            if not properties.get('bitrate') and data['format'].get('bit_rate'):
                properties['bitrate'] = int(data['format'].get('bit_rate'))
            
            # Get metadata
            if 'tags' in data['format']:
                properties['metadata'] = data['format'].get('tags', {})
                
        return properties
        
    except Exception as e:
        print(f"Error getting audio properties for {file_path}: {str(e)}")
        return None

def analyze_previews():
    """Analyze all preview files in the media directory"""
    print(f"Analyzing preview files in {PREVIEW_DIR}")
    
    # Check if directory exists
    if not os.path.exists(PREVIEW_DIR):
        print(f"Preview directory not found: {PREVIEW_DIR}")
        return
    
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(PREVIEW_DIR) if f.endswith('.mp3')]
    print(f"Found {len(mp3_files)} MP3 files")
    
    # Analysis results
    analysis = {
        'total_files': len(mp3_files),
        'sample_hashes': {},
        'file_hashes': {},
        'properties': {},
        'duplicates': {},
        'bitrate_counts': {},
        'sample_rate_counts': {},
        'metadata_issues': []
    }
    
    # Process each file
    for filename in mp3_files:
        file_path = os.path.join(PREVIEW_DIR, filename)
        print(f"Processing {filename}")
        
        # Get basic file information
        file_size = os.path.getsize(file_path)
        file_hash = calculate_audio_hash(file_path)
        
        # Store file hash
        if file_hash:
            if file_hash in analysis['file_hashes']:
                analysis['file_hashes'][file_hash].append(filename)
            else:
                analysis['file_hashes'][file_hash] = [filename]
        
        # Extract audio properties
        properties = get_audio_properties(file_path)
        if properties:
            analysis['properties'][filename] = properties
            
            # Track bitrate distribution
            bitrate = properties.get('bitrate', 0)
            if bitrate:
                bitrate_key = f"{int(bitrate/1000)}kbps"
                analysis['bitrate_counts'][bitrate_key] = analysis['bitrate_counts'].get(bitrate_key, 0) + 1
            
            # Track sample rate distribution
            sample_rate = properties.get('sample_rate', 0)
            if sample_rate:
                sample_rate_key = f"{sample_rate}Hz"
                analysis['sample_rate_counts'][sample_rate_key] = analysis['sample_rate_counts'].get(sample_rate_key, 0) + 1
            
            # Check for metadata issues
            metadata = properties.get('metadata', {})
            if not metadata or len(metadata) < 2:
                analysis['metadata_issues'].append(filename)
        
        # Extract audio sample for content comparison
        sample_file = os.path.join(AUDIO_SAMPLE_DIR, f"sample_{filename}.wav")
        if extract_audio_sample(file_path, sample_file):
            sample_hash = calculate_audio_hash(sample_file)
            
            if sample_hash:
                # Track sample hash
                if sample_hash in analysis['sample_hashes']:
                    analysis['sample_hashes'][sample_hash].append(filename)
                else:
                    analysis['sample_hashes'][sample_hash] = [filename]
    
    # Find duplicates (files with identical audio content)
    for hash_value, filenames in analysis['sample_hashes'].items():
        if len(filenames) > 1:
            analysis['duplicates'][hash_value] = filenames
    
    # Save analysis results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"Total files analyzed: {analysis['total_files']}")
    print(f"Unique audio content: {len(analysis['sample_hashes'])}")
    print(f"Duplicate groups: {len(analysis['duplicates'])}")
    print(f"Files with metadata issues: {len(analysis['metadata_issues'])}")
    
    # Print bitrate distribution
    print("\nBitrate Distribution:")
    for bitrate, count in sorted(analysis['bitrate_counts'].items()):
        print(f"  {bitrate}: {count} files")
    
    # Print sample rate distribution
    print("\nSample Rate Distribution:")
    for rate, count in sorted(analysis['sample_rate_counts'].items()):
        print(f"  {rate}: {count} files")
    
    # Print duplicate groups
    if analysis['duplicates']:
        print("\nDuplicate Files Detected:")
        for hash_value, filenames in analysis['duplicates'].items():
            print(f"  Group with {len(filenames)} identical files:")
            for filename in filenames:
                print(f"    - {filename}")
    
    return analysis

def create_visualization(analysis):
    """Create visualization of audio analysis results"""
    try:
        # Create figures directory
        os.makedirs("figures", exist_ok=True)
        
        # Bitrate distribution
        if analysis['bitrate_counts']:
            plt.figure(figsize=(10, 6))
            bitrates = sorted(analysis['bitrate_counts'].keys())
            counts = [analysis['bitrate_counts'][bitrate] for bitrate in bitrates]
            plt.bar(bitrates, counts)
            plt.title('Bitrate Distribution')
            plt.xlabel('Bitrate')
            plt.ylabel('Number of Files')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('figures/bitrate_distribution.png')
        
        # Sample rate distribution
        if analysis['sample_rate_counts']:
            plt.figure(figsize=(10, 6))
            sample_rates = sorted(analysis['sample_rate_counts'].keys())
            counts = [analysis['sample_rate_counts'][rate] for rate in sample_rates]
            plt.bar(sample_rates, counts)
            plt.title('Sample Rate Distribution')
            plt.xlabel('Sample Rate')
            plt.ylabel('Number of Files')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('figures/sample_rate_distribution.png')
        
        # Duplicate analysis
        if analysis['duplicates']:
            plt.figure(figsize=(10, 6))
            unique_files = analysis['total_files'] - sum(len(files) - 1 for files in analysis['duplicates'].values())
            duplicate_files = analysis['total_files'] - unique_files
            plt.pie([unique_files, duplicate_files], 
                   labels=['Unique Content', 'Duplicate Content'],
                   autopct='%1.1f%%',
                   startangle=90,
                   colors=['#4CAF50', '#F44336'])
            plt.axis('equal')
            plt.title('Audio Content Uniqueness')
            plt.tight_layout()
            plt.savefig('figures/content_uniqueness.png')
            
        print("Visualizations saved to 'figures' directory")
        
    except Exception as e:
        print(f"Error creating visualizations: {str(e)}")

if __name__ == "__main__":
    # Run the analysis
    analysis = analyze_previews()
    
    # Create visualizations
    if analysis:
        try:
            create_visualization(analysis)
        except ImportError:
            print("Matplotlib not installed, skipping visualizations")