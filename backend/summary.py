from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import google.generativeai as genai
import time
import os
import subprocess
import re
import json
from moviepy.editor import VideoFileClip
import datetime
import yt_dlp
import sys
import os
import gdown


def split_video(video_file, output_prefix, chunk_duration):
    """Splits a video into chunks of a specified duration."""
    try:
        video = VideoFileClip(video_file)
        duration = video.duration
        chunk_files = []
        for i in range(0, int(duration), chunk_duration):
            start = i
            end = min(i + chunk_duration, duration)
            output_file = f"{output_prefix}_part{int(start / chunk_duration)}.mp4"
            ffmpeg_extract_subclip(video_file, start, end, targetname=output_file)
            print(f"Created chunk: {output_file}")
            chunk_files.append((output_file, start))  # Store start time offset with the file
        
        video.close()
        return chunk_files
    except OSError as e:
        print(f"Error: {e}")
        return []


def get_video_description(video_path, base_time=0, api_key=None):
    """
    Uploads a video to Gemini and returns its description.
    Includes the base_time parameter to track the offset in the original video.
    """
    try:
        # Use provided API key or default
        if api_key is None:
            api_key = 'AIzaSyB4iKHoYawl0MLhnCgkQClro1dX0rGblq0'
            
        genai.configure(api_key=api_key)
        display_name = "temp_video_upload1"

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        print(f"Uploading file: {video_path}")
        video_file = genai.upload_file(path=video_path, display_name=display_name)
        print(f"File uploaded: {video_file.uri}")

        # Wait for processing to complete
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            video_file = genai.get_file(video_file.name)
        print("Upload processed")

        if video_file.state.name == "FAILED":
            raise ValueError(f"Video upload failed: {video_file.state.message}")

        # Generate content using the uploaded file
        prompt = "Write the activities of the cat in the ego centric video. Write only the key moments along with timesteps and duration. Do it for the full video. Don't assume unnecessary things. Just describe the video."
        model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
        print("Making LLM inference request...")
        response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
        print("LLM inference complete.")

        # Delete the uploaded file
        genai.delete_file(video_file.name)
        print("File deleted from Gemini.")
        
        # Return description along with the base time for this segment
        return {
            "description": response.text,
            "base_time": base_time
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"description": "", "base_time": base_time}


def summarize_description(description, api_key=None):
    """
    Summarizes the video description using Gemini.
    Returns a structured format with narrative and timestamps.
    """
    if api_key is None:
        api_key = 'AIzaSyA57VHXt2T1wXqHzEcpTe4YM66aIBgPEoU'
        
    genai.configure(api_key=api_key)
    prompt = """
    You are a model that summarizes video content of animals. Based on the text:
    1. Write how the day was spent focusing only on interesting and important moments
    2. Use simple and standard language without jargon
    3. Include timestamps of important and interesting moments
    4. Format your response as a JSON object with these fields:
       - "narrative": a cohesive story of the day's events (string)
       - "timestamps": a list of objects with:
           - "time": the timestamp in seconds or MM:SS format
           - "description": brief description of what happens at this timestamp
           - "importance": rate from 1-10 how important/interesting this moment is
    
    Here's the video description:
    """
    
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    print("Making LLM inference request for summary...")
    response = model.generate_content([prompt + description], request_options={"timeout": 600})
    print("LLM inference complete.")
    
    # Try to extract JSON
    try:
        # Look for JSON in the response
        match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # If no JSON code block, try to find any JSON-like structure
            json_str = response.text
            
        # Parse the JSON
        summary_data = json.loads(json_str)
        return summary_data
    except json.JSONDecodeError:
        print("Could not parse JSON from response. Using raw text.")
        return {
            "narrative": response.text,
            "timestamps": []
        }

def meta_summarize(all_segment_summaries, max_clips=24, api_key=None):
    """
    Creates a meta-summary from all segment summaries to select only the most important moments.
    
    Args:
        all_segment_summaries: List of summary objects from each segment
        max_clips: Maximum number of clips to include in final video
        api_key: API key for Gemini
        
    Returns:
        Dictionary containing selected timestamps and an overall video summary
    """
    if api_key is None:
        api_key = 'AIzaSyDjAtD7FWAnb1m8F8iVnEostUPy5RuUaeg'
        
    genai.configure(api_key=api_key)
    
    # Create a combined narrative with all timestamps and their importance scores
    combined_data = {
        "segments": []
    }
    
    for segment in all_segment_summaries:
        base_time = segment.get("base_time", 0)
        
        # Add segment with adjusted timestamps
        segment_data = {
            "narrative": segment.get("narrative", ""),
            "timestamps": []
        }
        
        for ts in segment.get("timestamps", []):
            # Convert time to seconds if in MM:SS format
            if isinstance(ts["time"], str) and ":" in ts["time"]:
                parts = list(map(int, ts["time"].split(':')))
                if len(parts) == 3:  # HH:MM:SS
                    seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
                else:  # MM:SS
                    seconds = parts[0] * 60 + parts[1]
            else:
                try:
                    seconds = float(ts["time"])
                except:
                    seconds = 0
                
            # Adjust timestamp to global time
            global_time = base_time + seconds
            
            segment_data["timestamps"].append({
                "global_time": global_time,
                "local_time": seconds,
                "description": ts.get("description", ""),
                "importance": ts.get("importance", 5)
            })
        
        combined_data["segments"].append(segment_data)
    
    # Convert to JSON for the LLM
    combined_json = json.dumps(combined_data, indent=2)
    
    prompt = f"""
    You have summaries from different segments of a cat video. Your task is to:
    1. Select the {max_clips} most important and interesting moments from the entire video
    2. Create an overall summary of the entire video (250-300 words).
    3.Make the summary about how the day was spent by the pet in the video. Do not use jargons.Use simple and standard words.
    
    Guidelines for selecting moments:
    1. Select diverse moments that tell a coherent story of the pet's day
    2. Prioritize moments with higher importance scores
    3. Ensure moments are spread throughout the video, not just from one segment
    4. Select moments that showcase different activities and behaviors
    
    Guidelines for the overall summary:
    1. Create an engaging narrative that captures the essence of the entire video
    2. Donot use jargons.Use standard and simple words
    3. Make it cohesive and entertaining for viewers
    4. Highlight key themes or patterns observed throughout the video
    
    Return a JSON object with:
    1. "selected_moments": Array of selected moments, each with:
       - "time": the global_time in seconds (where in the full video this occurs)
       - "description": brief description of what happens
       - "duration": how long to clip (default 5 seconds)
    2. "overall_summary": A comprehensive summary of the entire video
    
    Here are all the segment summaries:
    {combined_json}
    """
    
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    print(f"Making meta-summarization request to select top {max_clips} moments and create overall summary...")
    response = model.generate_content(prompt, request_options={"timeout": 600})
    print(response.text)
    
    try:
        # Try to extract JSON
        match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = response.text
            
        result = json.loads(json_str)
        selected_moments = result['selected_moments']
        overall_summary = result['overall_summary']
        print(f"Selected {len(result['selected_moments'])} moments for the final video")
        print(f"Generated overall summary of {len(result['overall_summary'].split())} words")
        return selected_moments,overall_summary
    except Exception as e:
        print(f"Error parsing meta-summary response: {e}")
        return {"selected_moments": [], "overall_summary": ""}


def format_time(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_duration(seconds):
    """Convert seconds to a human-readable duration"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if hours > 0:
        parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{int(seconds)} second{'s' if seconds != 1 else ''}")
    return " and ".join(parts)

def parse_time_to_seconds(time_str):
    """Convert time string (HH:MM:SS or MM:SS or seconds) to seconds"""
    if isinstance(time_str, (int, float)):
        return time_str
    
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + float(parts[1])
    else:  # Seconds
        return float(time_str)

def extract_clips_and_create_video(selected_moments, input_video, output_video):
    """ Extracts clips for the selected moments and combines them into a final video.
    Args:
        selected_moments: List of moments with time, description, and duration
        input_video: Path to the original full video
        output_video: Path for the output summary video
    """
    if not selected_moments:
        print("No moments selected. Cannot create summary video.")
        return False

    if not os.path.exists(input_video):
        print(f"Input video not found: {input_video}")
        return False

    # Get video duration using moviepy
    try:
        full_video = VideoFileClip(input_video)
        video_duration = full_video.duration
        full_video.close()
        print(f"Video duration: {format_time(video_duration)}")
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return False

    # Create temp directory for clips
    temp_dir = os.path.abspath("temp_clips")
    os.makedirs(temp_dir, exist_ok=True)

    # Extract each clip
    clips = []
    valid_moments = []
    for i, moment in enumerate(selected_moments):
        # Parse the time if needed
        start_time = parse_time_to_seconds(moment.get("time", 0))
        duration = 5
        end_time = start_time + duration
        description = moment.get("description", f"Moment {i+1}")

        # Skip if timestamp is beyond video duration
        if start_time >= video_duration:
            print(f"Skipping clip {i+1}/{len(selected_moments)}: {description} ({format_time(start_time)}) - Timestamp exceeds video duration")
            continue

        # Adjust end time if it exceeds video duration
        if end_time > video_duration:
            print(f"Adjusting end time for clip {i+1} from {format_time(end_time)} to {format_time(video_duration)}")
            end_time = video_duration
            duration = end_time - start_time

        # Store valid moment
        valid_moments.append({
            "time": start_time,
            "duration": duration,
            "description": description
        })

        clip_path = os.path.join(temp_dir, f"highlight_{i}.mp4")
        try:
            print(f"Extracting clip {i+1}/{len(selected_moments)}: {description} ({format_time(start_time)})")
            ffmpeg_extract_subclip(input_video, start_time, end_time, targetname=clip_path)
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 0:
                clips.append(clip_path)
                print(f"Extracted clip: {clip_path}")
            else:
                print(f"Failed to create clip at {start_time}s")
        except Exception as e:
            print(f"Error extracting clip at {start_time}s: {e}")

    if not clips:
        print("No clips extracted. Cannot create summary video.")
        return False
    concat_file = os.path.join(temp_dir, "concat_list.txt")

    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")  # Use absolute path
    
    print(f"Concat file created at: {concat_file}")
    output_dir = os.path.dirname(os.path.abspath(output_video))
    os.makedirs(output_dir, exist_ok=True)
    
    # Ensure we have the correct ffmpeg path or use default
    ffmpeg_path = r"C:/ffmpeg/bin/ffmpeg.exe"  # Default path
    
    # Check if ffmpeg exists at the specified path
    if not os.path.exists(ffmpeg_path):
        print(f"WARNING: FFmpeg not found at {ffmpeg_path}")
        print("Trying to use system FFmpeg...")
        ffmpeg_path = "ffmpeg"  # Try using system PATH
    
    # Clean up any existing output file to avoid conflicts
    if os.path.exists(output_video):
        try:
            os.remove(output_video)
            print(f"Removed existing output file: {output_video}")
        except Exception as e:
            print(f"Warning: Could not remove existing output file: {e}")
    
    # Use a more robust command with progress output
    final_command = [
        ffmpeg_path, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file, "-c:v", "libx264", "-preset", "fast",
        "-crf", "23", "-c:a", "aac", "-b:a", "192k",
        output_video
    ]
    
    print("Executing FFmpeg command:")
    print(" ".join(final_command))

    # Combine all clips using MoviePy
    try:
        result = subprocess.run(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"Combined video saved at: {output_video}")
            # Verify the output file exists and has content
            if os.path.exists(output_video) and os.path.getsize(output_video) > 0:
                print(f"Success! Output file verified: {output_video} ({os.path.getsize(output_video)} bytes)")
                return True
            else:
                print(f"ERROR: Output file does not exist or is empty: {output_video}")
                return False
        else:
            print(f"FFmpeg error (code {result.returncode}):")
            print(f"STDERR: {result.stderr}")
            return False
    except Exception as e:
        print(f"Failed to run FFmpeg: {e}")
        return False

def get_next_api_key(api_keys, current_index=None):
    """Returns the next API key in the rotation."""
    if current_index is None or current_index >= len(api_keys) - 1:
        next_index = 0
    else:
        next_index = current_index + 1
        
    return api_keys[next_index], next_index


def process_video(input_video, output_video="highlight_summary.mp4", chunk_duration=900, max_clips=10):
    """
    Process video by splitting it into chunks, analyzing each chunk, 
    then selecting only the most important moments for the final summary.
    
    Args:
        input_video: Path to the input video file.
        output_video: Path to the output video file.
        chunk_duration: Duration of each chunk in seconds.
        max_clips: Maximum number of clips to include in final video.
    """
    # Start the timer
    start_time = time.time()
    start_datetime = datetime.datetime.now()
    print(f"Processing started at: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all API keys
    api_keys = [
        'AIzaSyC-JOfG2Oc3CppcZVC3FxwbEXzSm9y1Zgs',
        'AIzaSyB4iKHoYawl0MLhnCgkQClro1dX0rGblq0',
        'AIzaSyDjAtD7FWAnb1m8F8iVnEostUPy5RuUaeg',
        'AIzaSyA57VHXt2T1wXqHzEcpTe4YM66aIBgPEoU',
        'AIzaSyDhc59vWrJSVgTG-6MbFWuh8lQf2HmaJdc',
        'AIzaSyBqDIdg5xpgLG3Fv6vawtLuMD5Y_Un6ZNY',
        'AIzaSyDZ02pS-CjVTCXeCbQD8ALjpduUBDS2CrE',
    ]
    
    print(f"Processing video: {input_video}")
    
    # Split the video into chunks
    output_prefix = os.path.splitext(input_video)[0]
    chunk_files = split_video(input_video, output_prefix, chunk_duration)
    
    segment_summaries = []
    current_key_index = 4
    
    # Process each chunk with rotating API keys
    for i, (chunk_file, base_time) in enumerate(chunk_files):
        print(f"\nProcessing chunk {i+1}/{len(chunk_files)}: {chunk_file}")
        chunk_start_time = time.time()
        
        # Get description for this chunk
        description_api_key, current_key_index = get_next_api_key(api_keys, current_key_index)
        print(f"Using API key for description: {description_api_key[:10]}...")
        
        chunk_data = get_video_description(chunk_file, base_time, description_api_key)
        
        # Get summary for this chunk
        summary_api_key, current_key_index = get_next_api_key(api_keys, current_key_index)
        print(f"Using API key for summary: {summary_api_key[:10]}...")
        
        chunk_summary = summarize_description(chunk_data["description"], summary_api_key)
        chunk_summary["base_time"] = chunk_data["base_time"]  # Add base time to the summary
        
        segment_summaries.append(chunk_summary)
        
        chunk_duration = time.time() - chunk_start_time
        print(f"Chunk {i+1} processing time: {format_duration(chunk_duration)}")
    
    # Meta-summarize to select the most important moments across all segments
    meta_start_time = time.time()
    meta_api_key, current_key_index = get_next_api_key(api_keys, current_key_index)
    selected_moments, overall_summary = meta_summarize(segment_summaries, max_clips, meta_api_key)
    meta_duration = time.time() - meta_start_time
    print(f"Meta-summarization time: {format_duration(meta_duration)}")
    
    # Create a comprehensive narrative
    all_narratives = "\n\n".join([f"Segment {i+1} ({format_time(s['base_time'])}):\n{s.get('narrative', '')}" 
                                  for i, s in enumerate(segment_summaries)])
    print("\nComplete Video Narrative:")
    print(all_narratives)

    print("\nOverall Summary")
    print(overall_summary)
    
    # Create a text description of selected moments
    print("\nSelected Highlight Moments:")
    for i, moment in enumerate(selected_moments):
        print(f"{i+1}. [{format_time(int(moment['time']))}] {moment.get('description', '')}")
    
    # Create the highlight video from the original file
    video_creation_start = time.time()
    print("\nCreating highlight video...")
    extract_clips_and_create_video(selected_moments, input_video, output_video)
    video_creation_duration = time.time() - video_creation_start
    print(f"Video creation time: {format_duration(video_creation_duration)}")
    
    # Calculate and print total elapsed time
    end_time = time.time()
    end_datetime = datetime.datetime.now()
    total_duration = end_time - start_time
    
    print("\n" + "="*50)
    print(f"Processing completed at: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total processing time: {format_duration(total_duration)}")
    print(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    return {
        "full_narrative": all_narratives,
        "selected_moments": selected_moments,
        "overall_summary": overall_summary,
        "output_video": output_video,
        "processing_time": {
            "total_seconds": total_duration,
            "formatted": format_duration(total_duration),
            "start_time": start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "end_time": end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }
    }


def download_from_gdrive(drive_url, output_path):
    """
    Download a file from Google Drive using gdown (better for large files)
    
    Parameters:
    drive_url (str): Public Google Drive URL
    output_path (str): Path to save the file
    
    Returns:
    str: Path to the downloaded file
    """
    gdown.download(url = drive_url,output= output_path, quiet=False, fuzzy = True)
    return output_path

def download_youtube_video_480p(video_url):
    """
    Download a YouTube video in 480p quality
    
    Parameters:
    video_url (str): URL of the YouTube video
    """
    # Format options to target 480p
    # 244+140: 480p video + audio for newer videos
    # 135+140: 480p video + audio (alternative format)
    # 18: 360p-480p combined video+audio (fallback)
    format_options = "244+140/135+140/18"
    
    # Output template for the filename
    output_template = "%(title)s.%(ext)s"
    
    print(f"Downloading: {video_url}")
    print("Target quality: 480p")
    
    ydl_opts = {
        'format': format_options,
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'progress': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"Download completed: {filename}")
            return filename
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Example usage
if __name__ == "__main__":
    result = process_video("backend/cat.mp4", "backend/newhighlights.mp4", chunk_duration=900, max_clips=12)
    
    # Save the processing results to a JSON file
    with open("processing_results.json", "w") as f:
        # Convert datetime objects to strings
        json_result = {
            "full_narrative": result["full_narrative"],
            "selected_moments": result["selected_moments"],
            "overall_summary": result["overall_summary"],
            "output_video": result["output_video"],
            "processing_time": result["processing_time"]
        }
        json.dump(json_result, f, indent=2)
    
    print(f"Results saved to processing_results.json")