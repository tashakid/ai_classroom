import unittest
from ai_classroom_assistant.agents.foreman import ForemanAgent
from unittest.mock import MagicMock, patch
import os
import json

class TestForemanAgent(unittest.TestCase):
    def setUp(self):
        # Mock the Mistral model
        self.model = MagicMock()
        self.agent = ForemanAgent(model=self.model, model_name="o1-mini")
        
        # Initialize mock sub-agents
        self.agent.supervisor = MagicMock()
        self.agent.code_generator = MagicMock()
        self.agent.video_watcher = MagicMock()
        self.agent.confirmer = MagicMock()
        
        # Define paths
        self.video_structure_path = "ai_classroom_assistant/video_structure.json"
        self.instructions_path = "ai_classroom_assistant/video_instructions.json"
        
        # Sample valid visual instructions
        self.valid_instructions = {
            "instructions": [
                {
                    "timeframe": "0-5 seconds",
                    "visual_elements": ["Title slide", "Probability Curve"],
                    "animations": ["Fade in title", "Draw probability curve"],
                    "manim_configurations": {}
                }
            ]
        }

    def tearDown(self):
        # Clean up the JSON file after tests
        if os.path.exists(self.instructions_path):
            os.remove(self.instructions_path)

    def test_create_video_instruction_success(self):
        # Mock the supervisor to return a valid video structure
        video_structure = {"video_segments": []}
        self.agent.supervisor.design_video_structure.return_value = video_structure
        
        # Mock the language model to return valid visual instructions
        self.model.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(self.valid_instructions)))]
        )
        
        # Execute the create_video_instruction method
        with patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=json.dumps(video_structure)):
            success = self.agent.create_video_instruction(self.video_structure_path, self.instructions_path)
        
        # Assertions
        self.assertTrue(success)
        self.model.chat.complete.assert_called_once()
        self.assertTrue(os.path.exists(self.instructions_path))
        with open(self.instructions_path, 'r') as f:
            data = json.load(f)
            self.assertIn("instructions", data)
            self.assertEqual(data, self.valid_instructions)

    def test_create_video_instruction_load_failure(self):
        # Mock the supervisor to raise an exception when designing video structure
        self.agent.supervisor.design_video_structure.side_effect = Exception("Supervisor Error")
        
        # Execute the create_video_instruction method
        success = self.agent.create_video_instruction(self.video_structure_path, self.instructions_path)
        
        # Assertions
        self.assertFalse(success)
        self.model.chat.complete.assert_not_called()
        self.assertFalse(os.path.exists(self.instructions_path))

    def test_translate_to_visuals_validation_failure(self):
        # Mock the supervisor to return a video structure
        video_structure = {"video_segments": []}
        self.agent.supervisor.design_video_structure.return_value = video_structure
        
        # Mock the language model to return invalid visual instructions
        invalid_instructions = {"wrong_key": []}
        self.model.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps(invalid_instructions)))]
        )
        
        # Mock the refine_visuals_instructions to return valid instructions
        with patch.object(self.agent, 'refine_visuals_instructions', return_value=self.valid_instructions):
            success = self.agent.create_video_instruction(self.video_structure_path, self.instructions_path)
        
        # Assertions
        self.assertTrue(success)
        self.model.chat.complete.assert_called_twice()  # Initial call and refinement call
        self.assertTrue(os.path.exists(self.instructions_path))
        with open(self.instructions_path, 'r') as f:
            data = json.load(f)
            self.assertIn("instructions", data)
            self.assertEqual(data, self.valid_instructions)

    def test_translate_to_visuals_refinement_failure(self):
        # Mock the supervisor to return a video structure
        video_structure = {"video_segments": []}
        self.agent.supervisor.design_video_structure.return_value = video_structure
        
        # Mock the language model to return invalid visual instructions
        invalid_instructions = {"wrong_key": []}
        self.model.chat.complete.side_effect = [
            MagicMock(message=MagicMock(content=json.dumps(invalid_instructions))),  # Initial invalid response
            MagicMock(message=MagicMock(content=json.dumps(invalid_instructions)))   # Refined invalid response
        ]
        
        # Execute the create_video_instruction method
        success = self.agent.create_video_instruction(self.video_structure_path, self.instructions_path)
        
        # Assertions
        self.assertFalse(success)
        self.assertTrue(os.path.exists(self.instructions_path))
        with open(self.instructions_path, 'r') as f:
            data = json.load(f)
            # Since validation failed even after refinement, instructions might be invalid or not saved
            # Depending on implementation, this might be an empty dict or still invalid
            self.assertNotIn("instructions", data)

    def test_translate_to_visuals_json_decode_error(self):
        # Mock the supervisor to return a video structure
        video_structure = {"video_segments": []}
        self.agent.supervisor.design_video_structure.return_value = video_structure
        
        # Mock the language model to return invalid JSON
        self.model.chat.complete.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content='Invalid JSON'))]
        )
        
        # Mock the refine_visuals_instructions to return valid instructions
        self.agent.refine_visuals_instructions = MagicMock(return_value=self.valid_instructions)
        
        # Execute the create_video_instruction method
        with patch('builtins.open', new_callable=unittest.mock.mock_open):
            success = self.agent.create_video_instruction(self.video_structure_path, self.instructions_path)
        
        # Assertions
        self.assertTrue(success)
        self.model.chat.complete.assert_called_twice()  # Initial call and refinement call
        self.assertTrue(os.path.exists(self.instructions_path))
        with open(self.instructions_path, 'r') as f:
            data = json.load(f)
            self.assertIn("instructions", data)
            self.assertEqual(data, self.valid_instructions)

if __name__ == '__main__':
    unittest.main()