import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock, patch
from core.db_connector import DBConnector
from core.schema_parser import SchemaParser
from core.generator import DataGenerator, generate_row
from core.ai_agent import AIAgent

class TestDataForge(unittest.TestCase):
    def test_imports(self):
        self.assertTrue(True)

    def test_generate_row_fallback(self):
        """Test that generate_row falls back to Faker when AI is skipped or not present."""
        
        # Test 1: Integer fallback
        columns = [('id', 'integer', False)]
        row = generate_row(columns, ai_config=None)
        self.assertIsInstance(row[0], int)

        # Test 2: Varchar fallback (name)
        columns = [('full_name', 'varchar', False)]
        row = generate_row(columns, ai_config=None)
        self.assertIsInstance(row[0], str)
        self.assertTrue(len(row[0]) > 0)

        # Test 3: Date fallback
        columns = [('created_at', 'date', False)]
        row = generate_row(columns, ai_config=None)
        self.assertIsInstance(row[0], str) # It returns str(date)

    @patch('core.generator.AIAgent')
    def test_generate_row_with_ai_mock(self, MockAIAgent):
        """Test generation with AI mock returning None (should trigger fallback)."""
        # Setup Mock
        mock_agent = MockAIAgent.return_value
        mock_agent.generate_text.return_value = None # AI fails/returns None
        
        columns = [('description', 'text', True)]
        # We need a config that enables AI
        ai_config = {'enabled': True, 'api_url': 'http://localhost', 'model': 'test'}
        
        row = generate_row(columns, ai_config=ai_config)
        
        # Should fallback to Faker text
        self.assertIsInstance(row[0], str)
        self.assertNotEqual(row[0], "N/A")

if __name__ == '__main__':
    unittest.main()
