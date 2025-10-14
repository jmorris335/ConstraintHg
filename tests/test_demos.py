import pytest
import subprocess
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).parent.parent / "demos"

class TestDemos():
    def run_demo(self, filename):
        result = subprocess.run(
            [sys.executable, str(DEMO_DIR / filename)],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def test_basic(self):
        """Tests the demo_basic.py demonstration."""
        stdout = self.run_demo('demo_basic.py')
        assert "└●─E" in stdout
        assert "C=10" in stdout
        assert "└──F=-10" in stdout
        assert "├──A=3" in stdout

    def test_linear_motion(self):
        """Tests the linear motion demo."""
        stdout = self.run_demo('demo_linear_motion.py')
        assert "├◯─x[CYCLE]" in stdout
        assert "└──x_n=6, index=5" in stdout
        assert "└──x=6, index=5" in stdout

    def test_elevator(self):
        """Tests the elevator demonstration."""
        stdout = self.run_demo('demo_elevator.py')
        assert "height=5.695" in stdout
    
    def test_pendulum(self):
        """Tests the pendulum demonstration."""
        stdout = self.run_demo('demo_pendulum.py')
        assert "theta=0.4445, index=100," in stdout

