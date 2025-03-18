import wave
import numpy as np
import sys
import os

def get_audio_data(filename):
    """Extract raw audio data as a numpy array from a WAV file"""
    with wave.open(filename, 'rb') as wav_file:
        # Get basic info
        n_channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        # Read all frames
        frames = wav_file.readframes(n_frames)
        
        # Convert to numpy array
        if sampwidth == 2:  # 16-bit
            dtype = np.int16
        elif sampwidth == 4:  # 32-bit
            dtype = np.int32
        else:
            dtype = np.uint8
            
        # Reshape based on number of channels
        audio_data = np.frombuffer(frames, dtype=dtype)
        
        if n_channels > 1:
            audio_data = audio_data.reshape(-1, n_channels)
            
        return {
            'data': audio_data,
            'channels': n_channels,
            'sample_width': sampwidth,
            'framerate': framerate,
            'n_frames': n_frames
        }

def compare_audio_files(file1, file2):
    """Compare two audio files and report differences"""
    audio1 = get_audio_data(file1)
    audio2 = get_audio_data(file2)
    
    # Check if audio parameters match
    if audio1['channels'] != audio2['channels']:
        return f"Channel count mismatch: {audio1['channels']} vs {audio2['channels']}"
        
    if audio1['sample_width'] != audio2['sample_width']:
        return f"Sample width mismatch: {audio1['sample_width']} vs {audio2['sample_width']}"
        
    if audio1['framerate'] != audio2['framerate']:
        return f"Sample rate mismatch: {audio1['framerate']} vs {audio2['framerate']}"
    
    # Check if data length matches
    data1 = audio1['data']
    data2 = audio2['data']
    
    if len(data1) != len(data2):
        return f"Audio length mismatch: {len(data1)} vs {len(data2)} samples"
    
    # Compare data
    if np.array_equal(data1, data2):
        return "Audio data is IDENTICAL"
    
    # Calculate differences
    # For multi-channel, use mean difference across channels
    if len(data1.shape) > 1 and data1.shape[1] > 1:
        diff = np.abs(data1 - data2).mean(axis=1)
    else:
        diff = np.abs(data1 - data2)
    
    # Calculate statistics
    max_diff = np.max(diff)
    mean_diff = np.mean(diff)
    nonzero = np.count_nonzero(diff)
    percent_diff = (nonzero / len(diff)) * 100
    
    # Sample some differences for display
    diff_indices = np.where(diff > 0)[0]
    sample_indices = diff_indices[:5] if len(diff_indices) >= 5 else diff_indices
    
    sample_diffs = []
    for idx in sample_indices:
        if len(data1.shape) > 1 and data1.shape[1] > 1:
            val1 = data1[idx]
            val2 = data2[idx]
            sample_diffs.append(f"Sample {idx}: {val1} vs {val2}")
        else:
            val1 = data1[idx]
            val2 = data2[idx]
            sample_diffs.append(f"Sample {idx}: {val1} vs {val2}")
    
    return f"Audio data DIFFERS:\n" + \
           f"- {percent_diff:.2f}% of samples are different\n" + \
           f"- Max difference: {max_diff}\n" + \
           f"- Mean difference: {mean_diff:.2f}\n" + \
           f"- Sample differences:\n  " + "\n  ".join(sample_diffs)

if __name__ == "__main__":
    # Compare all three files
    file1 = "sample1.wav"
    file2 = "sample2.wav"
    file3 = "sample3.wav"
    
    print(f"Comparing {file1} vs {file2}:")
    print(compare_audio_files(file1, file2))
    print("\n" + "="*50 + "\n")
    
    print(f"Comparing {file1} vs {file3}:")
    print(compare_audio_files(file1, file3))
    print("\n" + "="*50 + "\n")
    
    print(f"Comparing {file2} vs {file3}:")
    print(compare_audio_files(file2, file3))