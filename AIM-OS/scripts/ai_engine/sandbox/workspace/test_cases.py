"""
AIM-OS AI Engine — Improved Test Cases (Sandbox Auditor Proposal)

Focus areas:
- Shell argument limit robustness
- Agent registry persistence
- End-to-end pipeline mocking
"""

import unittest
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

# Import improved classes from the same workspace
from improved_code import PersistentAgentRegistry, RobustGeminiCLIProvider

class TestAiEngineImprovements(unittest.TestCase):

    def test_registry_persistence(self):
        """Verify that agent performance metrics persist across registry instances."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # First instance: update metrics
            reg1 = PersistentAgentRegistry(storage_path=tmp_path)
            reg1.update_performance('coder_v1', success=True, confidence=0.95)
            reg1.save()
            
            # Second instance: load and verify
            reg2 = PersistentAgentRegistry(storage_path=tmp_path)
            coder = reg2.get('coder_v1')
            self.assertEqual(coder.total_tasks, 1)
            self.assertAlmostEqual(coder.success_rate, 1.0)
            self.assertAlmostEqual(coder.avg_confidence, 0.95)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_robust_cli_vision_shell_limit(self):
        """Verify that vision prompts aren't limited by shell argument length."""
        provider = RobustGeminiCLIProvider(cli_path='gemini')
        
        # Create a massive prompt (10KB) that would exceed Windows shell limits
        huge_prompt = "Analyze this image: " + ("x" * 10000)
        
        # Mock subprocess.run to verify the command structure
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Create a dummy image file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as img:
                img_path = img.name
            
            try:
                provider.vision(image_path=img_path, prompt=huge_prompt)
                
                # Verify that subprocess.run was called with a shell pipe, not a direct -p flag
                args, kwargs = mock_run.call_args
                cmd_str = args[0]
                self.assertIn('|', cmd_str)
                self.assertNotIn(huge_prompt, cmd_str) # Prompt should be in file, not cmd string
            finally:
                if os.path.exists(img_path):
                    os.unlink(img_path)

if __name__ == '__main__':
    unittest.main()
