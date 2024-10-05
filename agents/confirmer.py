from mistralai import Mistral
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

class ConfirmerAgent:
    def __init__(self, model, confirmed_videos_dir):
        """
        Initializes the Confirmer Agent with a language model.

        :param model: The language model used for consolidation.
        :param confirmed_videos_dir: Directory to store confirmed video clips.
        """
        self.model = model
        self.confirmed_videos_dir = confirmed_videos_dir
        os.makedirs(self.confirmed_videos_dir, exist_ok=True)

    def consolidate_videos(self, video_paths, output_path):
        """
        Merges confirmed video clips into a final presentation.

        :param video_paths: List of paths to confirmed video clips.
        :param output_path: Path to save the consolidated video.
        :return: Path to the final video.
        """
        clips = []
        for path in video_paths:
            clip = VideoFileClip(path)
            clips.append(clip)

        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Close all clips to release resources
        for clip in clips:
            clip.close()
        final_clip.close()

        return output_path