from summary import *
from email_service import send_video_upload_notification,send_welcome_email
from models import User,Video
from sqlalchemy.orm import Session


from summary import *
from email_service import send_video_upload_notification, send_welcome_email
from models import User, Video, ProcessingStatus
from sqlalchemy.orm import Session

def process_video(input_video_link, output_video="highlight_summary.mp4", chunk_duration=900, max_clips=10, background_tasks=None, user_email=None, video_id=None, db: Session = None):
    """
    Process video by splitting it into chunks, analyzing each chunk, 
    then selecting only the most important moments for the final summary.
    
    Args:
        input_video_link: URL or path to the input video file.
        output_video: Path to the output video file.
        chunk_duration: Duration of each chunk in seconds.
        max_clips: Maximum number of clips to include in final video.
        background_tasks: BackgroundTasks object for scheduling background tasks.
        user_email: Email of the user processing the video.
        video_id: Unique identifier of the video being processed.
        db: SQLAlchemy database session.
    """
    # Start the timer
    start_time = time.time()
    start_datetime = datetime.datetime.now()
    print(f"Processing started at: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    # Handle video and user association
    if db and video_id:
        video = db.query(Video).filter(Video.unique_id == video_id).first()
        if not video:
            raise ValueError(f"Video with id {video_id} not found")
        
        user = None
        if video.user_id:
            user = db.query(User).filter(User.id == video.user_id).first()
        
        video.processing_status = ProcessingStatus.PROCESSING
        db.commit()
    else:
        video = None
        user = None

    
    if "youtube.com" in input_video_link or "youtu.be" in input_video_link:
        input_video = download_youtube_video_480p(input_video_link)
    elif "drive.google.com" in input_video_link:
        input_video = download_from_gdrive(input_video_link, "gdrive.mp4")
    else:
        input_video = input_video_link

    if not os.path.exists(input_video):
        raise ValueError(f"Input video file not found: {input_video}")

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
    current_key_index = 3
    
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
        print(f"{i+1}. [{format_time(moment['time'])}] {moment.get('description', '')}")
    
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
    
    result = {
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
    
    if db and video:
        video.summary_video_link = output_video
        video.summary_text = overall_summary
        video.processing_status = ProcessingStatus.COMPLETED
        db.commit()

    if background_tasks and user_email and video_id:
        background_tasks.add_task(
            send_video_upload_notification,
            user_email,
            video_id,
            output_video
        )
    
    return result

if __name__ == "__main__":
    # This part should be removed or modified to work with your actual database session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine('your_database_url_here')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    result = process_video(
        "https://www.youtube.com/watch?v=Nzw1JHe1HCo&ab_channel=CatswithGoPro",
        "cat_highlights_final.mp4",
        chunk_duration=900,
        max_clips=12,
        db=db,
        video_id="some_video_id_here"
    )
    
    # Save the processing results to a JSON file
    with open("processing_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Results saved to processing_results.json")