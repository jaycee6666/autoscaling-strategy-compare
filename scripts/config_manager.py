#!/usr/bin/env python3
"""
Phase 0: Configuration Manager
Centralized configuration management for cross-platform compatibility.
Handles environment variables, config files, and AWS settings.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv, dotenv_values
import yaml


class ConfigManager:
    """Centralized configuration management."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.env_file = self.config_dir / ".env"
        self.config_file = self.config_dir / "config.yaml"
        self.aws_config_file = self.config_dir / "aws_config.json"

        # Load environment variables
        load_dotenv(self.env_file)
        self._load_configs()

    def _load_configs(self):
        """Load all configuration files."""
        self.env_vars = dotenv_values(self.env_file) if self.env_file.exists() else {}
        self.yaml_config = self._load_yaml() if self.config_file.exists() else {}
        self.aws_config = (
            self._load_aws_config() if self.aws_config_file.exists() else {}
        )

    def _load_yaml(self) -> Dict[str, Any]:
        """Load YAML configuration."""
        try:
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Failed to load YAML config: {e}")
            return {}

    def _load_aws_config(self) -> Dict[str, Any]:
        """Load AWS configuration."""
        try:
            with open(self.aws_config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load AWS config: {e}")
            return {}

    def get(self, key: str, default: Any = None, section: str = "env") -> Any:
        """
        Get configuration value from specified section.

        Args:
            key: Configuration key
            default: Default value if not found
            section: Configuration section ('env', 'yaml', or 'aws')

        Returns:
            Configuration value or default
        """
        if section == "env":
            return self.env_vars.get(key, os.environ.get(key, default))
        elif section == "yaml":
            return self._get_nested_value(self.yaml_config, key, default)
        elif section == "aws":
            return self.aws_config.get(key, default)
        return default

    def get_aws_setting(self, key: str, default: Any = None) -> Any:
        """Get AWS-specific setting."""
        # Check environment variables first (higher priority)
        env_key = f"AWS_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value

        # Check AWS config
        return self.aws_config.get(key, default)

    def _get_nested_value(self, config: Dict, key: str, default: Any) -> Any:
        """Get nested value from config using dot notation."""
        keys = key.split(".")
        value = config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any, section: str = "env"):
        """Set configuration value."""
        if section == "env":
            self.env_vars[key] = str(value)
            os.environ[key] = str(value)
        elif section == "yaml":
            self._set_nested_value(self.yaml_config, key, value)
        elif section == "aws":
            self.aws_config[key] = value

    def _set_nested_value(self, config: Dict, key: str, value: Any):
        """Set nested value using dot notation."""
        keys = key.split(".")
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value

    def save(self, section: str = "all"):
        """Save configuration to files."""
        if section in ["env", "all"]:
            self._save_env()
        if section in ["yaml", "all"]:
            self._save_yaml()
        if section in ["aws", "all"]:
            self._save_aws_config()

    def _save_env(self):
        """Save environment variables to .env file."""
        try:
            lines = []
            for key, value in self.env_vars.items():
                # Skip AWS keys that shouldn't be committed
                if key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]:
                    continue
                lines.append(f"{key}={value}")

            with open(self.env_file, "w") as f:
                f.write("\n".join(lines))
            print(f"✓ Saved environment config to {self.env_file}")
        except Exception as e:
            print(f"✗ Failed to save .env: {e}")

    def _save_yaml(self):
        """Save YAML configuration."""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self.yaml_config, f, default_flow_style=False)
            print(f"✓ Saved YAML config to {self.config_file}")
        except Exception as e:
            print(f"✗ Failed to save YAML config: {e}")

    def _save_aws_config(self):
        """Save AWS configuration."""
        try:
            with open(self.aws_config_file, "w") as f:
                json.dump(self.aws_config, f, indent=2)
            print(f"✓ Saved AWS config to {self.aws_config_file}")
        except Exception as e:
            print(f"✗ Failed to save AWS config: {e}")

    def validate_aws_credentials(self) -> bool:
        """Validate AWS credentials are configured."""
        access_key = self.get_aws_setting("access_key_id")
        secret_key = self.get_aws_setting("secret_access_key")

        if not access_key or not secret_key:
            print("✗ AWS credentials not configured")
            print(
                "  Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            )
            return False

        print("✓ AWS credentials found")
        return True

    def validate_aws_region(self) -> bool:
        """Validate AWS region is configured."""
        region = self.get_aws_setting(
            "default_region", os.environ.get("AWS_DEFAULT_REGION")
        )

        if not region:
            print("✗ AWS region not configured")
            print("  Set AWS_DEFAULT_REGION environment variable")
            return False

        print(f"✓ AWS region configured: {region}")
        return True

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values (sanitized)."""
        config = {
            "env": {
                k: v
                for k, v in self.env_vars.items()
                if k not in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
            },
            "yaml": self.yaml_config,
            "aws": {
                k: v
                for k, v in self.aws_config.items()
                if k not in ["access_key_id", "secret_access_key"]
            },
        }
        return config

    def print_summary(self):
        """Print configuration summary."""
        print("\n" + "=" * 60)
        print("CONFIGURATION SUMMARY")
        print("=" * 60)

        all_config = self.get_all()

        print("\n📋 Environment Variables:")
        for k, v in all_config["env"].items():
            print(f"  {k}: {v}")

        print("\n⚙️  YAML Configuration:")
        print(
            yaml.dump(all_config["yaml"], default_flow_style=False)
            if all_config["yaml"]
            else "  (empty)"
        )

        print("\n☁️  AWS Configuration:")
        for k, v in all_config["aws"].items():
            print(f"  {k}: {v}")

        print("=" * 60 + "\n")


# Helper functions for direct access
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None, section: str = "env") -> Any:
    """Get configuration value."""
    return get_config_manager().get(key, default, section)


def set_config(key: str, value: Any, section: str = "env"):
    """Set configuration value."""
    return get_config_manager().set(key, value, section)


def save_config(section: str = "all"):
    """Save configuration."""
    return get_config_manager().save(section)


if __name__ == "__main__":
    # Test the config manager
    config = ConfigManager()
    config.print_summary()
