import logging
import shutil

from moviepy import AudioFileClip, CompositeAudioClip, VideoFileClip

from src.common import SCENES_DIR, configs


def get_audio_clips(clip_volume: float, voice_volume: float) -> None:
    """Add generated voice to each clip.

    Args:
        clip_volume (float): Volume of the original clip used for the audio clip
        voice_volume (float): Volume of the generated voice used for the audio clip
    """
    total_audio_clips_created = 0
    
    for idx, scene_dir in enumerate(SCENES_DIR):
        logger.info("Generating audio clips for scene %s", idx+1)
        clips_dir = scene_dir / "clips"
        audios_dir = scene_dir / "audios"
        audio_clips_dir = scene_dir / "audio_clips"

        # Check if directories exist
        if not clips_dir.exists():
            logger.error("Clips directory not found: %s", clips_dir)
            continue
            
        if not audios_dir.exists():
            logger.error("Audios directory not found: %s", audios_dir)
            continue

        if audio_clips_dir.exists():
            shutil.rmtree(audio_clips_dir)

        audio_clips_dir.mkdir(parents=True, exist_ok=True)
        
        # Check for audio files
        audio_files = list(audios_dir.glob("*.wav"))
        logger.info("Found %s audio files in %s", len(audio_files), audios_dir)
        
        if not audio_files:
            logger.error("No audio files found in %s", audios_dir)
            continue

        scene_audio_clips = 0
        for audio_path in audio_files:
            audio_name = audio_path.stem
            logger.info("Processing audio: %s", audio_name)
            
            try:
                audio = AudioFileClip(str(audio_path))
                
                # Check for matching clips
                matching_clips = list(clips_dir.glob(f"*{audio_name}.mp4"))
                logger.info("Found %s matching clips for audio %s", len(matching_clips), audio_name)
                
                if not matching_clips:
                    logger.error("No matching clips found for audio: %s", audio_name)
                    continue
                
                for clip_path in matching_clips:
                    clip_name = clip_path.stem
                    logger.info("Processing clip: %s", clip_name)
                    
                    try:
                        clip = VideoFileClip(str(clip_path))
                        
                        # Check if clip has audio
                        if clip.audio is None:
                            logger.error("Clip has no audio: %s", clip_path)
                            continue
                        
                        mixed_audio = CompositeAudioClip(
                            [
                                clip.audio * clip_volume,
                                audio * voice_volume,
                            ]
                        )
                        
                        output_path = f"{audio_clips_dir}/audio_clip_{clip_name}.mp4"
                        logger.info("Creating audio clip: %s", output_path)
                        
                        clip.with_audio(mixed_audio).write_videofile(
                            output_path,
                            verbose=False,
                            logger=None,
                        )
                        
                        scene_audio_clips += 1
                        total_audio_clips_created += 1
                        logger.info("Successfully created audio clip: %s", output_path)
                    except Exception as e:
                        logger.error("Error processing clip %s: %s", clip_name, e)
            except Exception as e:
                logger.error("Error processing audio %s: %s", audio_name, e)
                
        logger.info("Created %s audio clips for scene %s", scene_audio_clips, idx+1)
    
    logger.info("Total audio clips created: %s", total_audio_clips_created)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 6 audio clip creation #####\n")

get_audio_clips(
    configs["audio_clip"]["clip_volume"],
    configs["audio_clip"]["voice_volume"],
)
