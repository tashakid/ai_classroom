import cv2
import os
import subprocess

def convert_anim_to_video(anim_path, video_path, fps=30):
    """
    Converts a Manim animation to a video file.

    :param anim_path: Path to the Manim animation script.
    :param video_path: Desired output video file path.
    :param fps: Frames per second for the video.
    """
    # This function calls Manim via subprocess to render the animation
    command = [
        "manim",
        anim_path,
        "-pql",  # -p for preview, -ql for low quality
        "--fps",
        str(fps),
        "-o",
        video_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Animation rendered and saved to {video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error rendering animation: {e}")

def get_video_properties(video_path):
    """
    Retrieves properties of a video file.

    :param video_path: Path to the video file.
    :return: Dictionary containing video properties.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {video_path}")
        return {}

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0

    cap.release()

    properties = {
        "frame_count": frame_count,
        "fps": fps,
        "resolution": f"{width}x{height}",
        "duration_seconds": duration
    }

    return properties