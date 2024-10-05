from mistralai import Mistral
import json
import cv2

class VideoWatcherAgent:
    def __init__(self, model, objective):
        """
        Initializes the Video Watcher Agent with a language model and objective.

        :param model: The language model used for evaluation.
        :param objective: The educational objective to evaluate against.
        """
        self.model = model
        self.objective = objective

    def evaluate_video(self, video_path):
        """
        Evaluates the generated video to determine if it meets the educational objective.

        :param video_path: Path to the generated video file.
        :return: Evaluation result as a dictionary.
        """
        # Basic video property analysis using OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video file {video_path}")
            return {"status": "failure", "reason": "Cannot open video file."}

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps else 0

        cap.release()

        evaluation = {
            "duration_seconds": duration,
            "frame_count": frame_count,
            "fps": fps,
            "status": "success",
            "objective_met": self.check_objective(duration)
        }

        return evaluation

    def check_objective(self, duration):
        """
        Checks if the video meets the educational objective.

        :param duration: Duration of the video in seconds.
        :return: Boolean indicating if the objective is met.
        """
        required_duration = 90  # seconds
        return duration >= required_duration

    def suggest_improvements(self, evaluation):
        """
        Suggests improvements based on the evaluation.

        :param evaluation: The evaluation result dictionary.
        :return: Suggestions as a string.
        """
        if evaluation["status"] != "success":
            return "Video file could not be processed. Please check the file format and integrity."

        if not evaluation["objective_met"]:
            return "The video duration is too short to cover the educational objective adequately. Consider extending the content."

        return "No improvements needed. The video meets the educational objective."