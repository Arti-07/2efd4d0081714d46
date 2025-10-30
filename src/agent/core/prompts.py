import os
from datetime import datetime
from functools import cache

from src.agent.settings import get_config

config = get_config()


class PromptLoader:
    @classmethod
    @cache
    def _load_prompt_file(cls, filename: str) -> str:
        user_file_path = os.path.join(config.prompts_dir, filename)
        lib_file_path = os.path.join(os.path.dirname(__file__), "..", config.prompts_dir, filename)

        for file_path in [user_file_path, lib_file_path]:
            if os.path.exists(file_path):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        return f.read().strip()
                except IOError as e:
                    raise IOError(f"Error reading prompt file {file_path}: {e}") from e

        raise FileNotFoundError(f"Prompt file not found: {user_file_path} or {lib_file_path}")

    @classmethod
    def get_system_prompt(cls) -> str:
        """Load the default system prompt (for backward compatibility)"""
        template = cls._load_prompt_file(config.system_prompt_file)
        try:
            return template.format(
                current_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                date_format="d-m-Y HH:MM:SS",
            )
        except KeyError as e:
            raise KeyError(f"Missing placeholder in system prompt template: {e}") from e
    
    @classmethod
    def get_prompt(cls, filename: str) -> str:
        """Load any prompt file with current date substitution"""
        template = cls._load_prompt_file(filename)
        try:
            return template.format(
                current_date=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                date_format="d-m-Y HH:MM:SS",
            )
        except KeyError as e:
            # If template doesn't have placeholders, return as is
            return template