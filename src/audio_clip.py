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
    logger.info(
        "Starting audio clip creation with clip_volume: %s, voice_volume: %s",
        clip_volume,
        voice_volume,
    )
    total_audio_clips_created = 0

    # Log all scene directories we're working with
    logger.info("Scene directories to process: %s", [str(d) for d in SCENES_DIR])

    for idx, scene_dir in enumerate(SCENES_DIR):
        logger.info("\n==== Processing scene %s at path: %s ====", idx + 1, scene_dir)
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

        logger.info(
            "Directories verified: clips_dir=%s, audios_dir=%s", clips_dir, audios_dir
        )

        if audio_clips_dir.exists():
            logger.info("Removing existing audio_clips directory: %s", audio_clips_dir)
            shutil.rmtree(audio_clips_dir)

        logger.info("Creating audio_clips directory: %s", audio_clips_dir)
        audio_clips_dir.mkdir(parents=True, exist_ok=True)

        # Check for audio files
        audio_files = list(audios_dir.glob("*.wav"))
        logger.info(
            "Found %s audio files in %s: %s",
            len(audio_files),
            audios_dir,
            [f.name for f in audio_files],
        )

        if not audio_files:
            logger.error("No audio files found in %s", audios_dir)
            continue

        # Log all clip files available
        all_clips = list(clips_dir.glob("*.mp4"))
        logger.info(
            "Found %s total clip files in %s: %s",
            len(all_clips),
            clips_dir,
            [f.name for f in all_clips],
        )

        scene_audio_clips = 0
        for audio_path in audio_files:
            audio_name = audio_path.stem
            logger.info("\n-- Processing audio: %s --", audio_name)

            try:
                logger.info("Loading audio file: %s", audio_path)
                audio = AudioFileClip(str(audio_path))
                logger.info(
                    "Audio loaded successfully - duration: %s seconds", audio.duration
                )

                # Check for matching clips
                matching_pattern = f"*{audio_name}.mp4"
                logger.info(
                    "Searching for matching clips with pattern: %s", matching_pattern
                )
                matching_clips = list(clips_dir.glob(matching_pattern))
                logger.info(
                    "Found %s matching clips for audio %s: %s",
                    len(matching_clips),
                    audio_name,
                    [f.name for f in matching_clips],
                )

                if not matching_clips:
                    logger.error("No matching clips found for audio: %s", audio_name)
                    continue

                for clip_path in matching_clips:
                    clip_name = clip_path.stem
                    logger.info("Processing clip: %s", clip_name)

                    try:
                        logger.info("Loading video clip: %s", clip_path)
                        clip = VideoFileClip(str(clip_path))
                        logger.info(
                            "Clip loaded successfully - duration: %s, size: %s",
                            clip.duration,
                            getattr(clip, "size", "Unknown"),
                        )

                        # Check if clip has audio
                        if clip.audio is None:
                            logger.error("Clip has no audio: %s", clip_path)
                            continue

                        logger.info("Creating composite audio")
                        mixed_audio = CompositeAudioClip(
                            [
                                clip.audio * clip_volume,
                                audio * voice_volume,
                            ]
                        )
                        logger.info("Composite audio created successfully")

                        output_path = f"{audio_clips_dir}/audio_clip_{clip_name}.mp4"
                        logger.info("Writing audio clip to: %s", output_path)

                        final_clip = clip.with_audio(mixed_audio)
                        logger.info("Audio attached to clip")

                        final_clip.write_videofile(
                            output_path,
                            verbose=False,
                            logger=None,
                        )

                        scene_audio_clips += 1
                        total_audio_clips_created += 1
                        logger.info("Successfully created audio clip: %s", output_path)
                    except Exception as e:
                        logger.error("Error processing clip %s: %s", clip_name, e)
                        import traceback

                        logger.error("Traceback: %s", traceback.format_exc())
            except Exception as e:
                logger.error("Error processing audio %s: %s", audio_name, e)
                import traceback

                logger.error("Traceback: %s", traceback.format_exc())

        logger.info(
            "\n==== Completed scene %s - Created %s audio clips ====",
            idx + 1,
            scene_audio_clips,
        )

    logger.info(
        "\n*** Audio clip creation complete. Total clips created: %s ***",
        total_audio_clips_created,
    )


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 6 audio clip creation #####\n")

get_audio_clips(
    configs["audio_clip"]["clip_volume"],
    configs["audio_clip"]["voice_volume"],
)
