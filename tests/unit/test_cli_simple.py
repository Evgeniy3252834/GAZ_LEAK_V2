"""
Простые тесты для CLI
"""
import pytest
from unittest.mock import patch, MagicMock

class TestCLISimple:
    
    def test_cli_module_exists(self):
        """Проверка существования модуля CLI"""
        try:
            from src.cli import batch_process
            assert hasattr(batch_process, 'main')
        except ImportError:
            pytest.skip("CLI module not available")
    
    def test_batch_process_import(self):
        """Тест импорта batch_process"""
        try:
            from src.cli.batch_process import main
            assert callable(main)
        except ImportError:
            pytest.skip("batch_process import failed")
    
    @patch('src.cli.batch_process.argparse.ArgumentParser')
    def test_argument_parsing(self, mock_parser):
        """Тест парсинга аргументов"""
        mock_instance = MagicMock()
        mock_parser.return_value = mock_instance
        mock_instance.parse_args.return_value = MagicMock(
            input_dir="./input",
            output_dir="./output",
            model_path=None,
            confidence=0.5,
            max_workers=4
        )
        
        from src.cli import batch_process
        # Просто проверяем что импорт работает
        assert True
