"""
Configuration Manager for Stage Validator - v1.2.12

統一設定管理とプロファイル機能を提供する。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import asdict, replace

from .models import ValidationConfig, LogDetailLevel, VisionCheckTiming, PatrolAdvancementRule


class ConfigManager:
    """設定管理とプロファイル機能"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir or ".stage_validator_config")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.profiles_dir = self.config_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)

        self.current_config: Optional[ValidationConfig] = None
        self.current_profile: str = "default"

    def load_config(self, profile_name: str = "default") -> ValidationConfig:
        """設定ファイルから設定をロード"""
        try:
            if profile_name == "default":
                config_path = self.config_file
            else:
                config_path = self.profiles_dir / f"{profile_name}.json"

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                # Enum値の復元
                config_data = self._restore_enum_values(config_data)
                self.current_config = ValidationConfig(**config_data)
                self.current_profile = profile_name

                print(f"✅ Loaded profile '{profile_name}' from {config_path}")
                return self.current_config
            else:
                print(f"⚠️  Profile '{profile_name}' not found, using default config")
                self.current_config = ValidationConfig()
                self.current_profile = "default"
                return self.current_config

        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("Using default configuration")
            self.current_config = ValidationConfig()
            self.current_profile = "default"
            return self.current_config

    def save_config(self, config: ValidationConfig, profile_name: str = "default") -> bool:
        """設定をファイルに保存"""
        try:
            if profile_name == "default":
                config_path = self.config_file
            else:
                config_path = self.profiles_dir / f"{profile_name}.json"

            config_data = asdict(config)
            # Enum値を文字列に変換
            config_data = self._serialize_enum_values(config_data)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.current_config = config
            self.current_profile = profile_name
            print(f"✅ Saved profile '{profile_name}' to {config_path}")
            return True

        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False

    def list_profiles(self) -> List[str]:
        """利用可能なプロファイルをリスト"""
        profiles = ["default"]
        if self.profiles_dir.exists():
            for profile_file in self.profiles_dir.glob("*.json"):
                profiles.append(profile_file.stem)
        return sorted(profiles)

    def create_profile_from_template(self, profile_name: str, template: str) -> ValidationConfig:
        """テンプレートからプロファイルを作成"""
        templates = {
            "performance": self._create_performance_config(),
            "debug": self._create_debug_config(),
            "minimal": self._create_minimal_config(),
            "strict": self._create_strict_config()
        }

        if template not in templates:
            raise ValueError(f"Unknown template: {template}. Available: {list(templates.keys())}")

        config = templates[template]
        self.save_config(config, profile_name)
        return config

    def get_current_config(self) -> ValidationConfig:
        """現在の設定を取得"""
        if self.current_config is None:
            return self.load_config()
        return self.current_config

    def update_config(self, **kwargs) -> ValidationConfig:
        """現在の設定を更新"""
        if self.current_config is None:
            self.current_config = ValidationConfig()

        updated_config = replace(self.current_config, **kwargs)
        self.current_config = updated_config
        return updated_config

    def reset_to_defaults(self) -> ValidationConfig:
        """デフォルト設定にリセット"""
        self.current_config = ValidationConfig()
        return self.current_config

    def export_config(self, output_path: str) -> bool:
        """設定を外部ファイルにエクスポート"""
        try:
            if self.current_config is None:
                self.current_config = ValidationConfig()

            export_data = {
                "profile_name": self.current_profile,
                "export_timestamp": str(Path().resolve()),
                "config": asdict(self.current_config)
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Configuration exported to {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error exporting config: {e}")
            return False

    def import_config(self, input_path: str, profile_name: Optional[str] = None) -> ValidationConfig:
        """外部ファイルから設定をインポート"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            if "config" in import_data:
                config_data = import_data["config"]
            else:
                config_data = import_data

            config_data = self._restore_enum_values(config_data)
            config = ValidationConfig(**config_data)

            save_name = profile_name or import_data.get("profile_name", "imported")
            self.save_config(config, save_name)

            print(f"✅ Configuration imported as profile '{save_name}'")
            return config

        except Exception as e:
            print(f"❌ Error importing config: {e}")
            raise

    def _create_performance_config(self) -> ValidationConfig:
        """パフォーマンス重視設定"""
        return ValidationConfig(
            log_detail_level=LogDetailLevel.MINIMAL,
            max_solution_steps=500,
            comparison_timeout_seconds=30.0,
            memory_optimization_enabled=True,
            enable_debug_file_logging=False,
            enemy_rotation_delay=1,
            alert_cooldown_turns=3,
            chase_timeout_turns=5
        )

    def _create_debug_config(self) -> ValidationConfig:
        """デバッグ重視設定"""
        return ValidationConfig(
            log_detail_level=LogDetailLevel.DEBUG,
            max_solution_steps=2000,
            comparison_timeout_seconds=300.0,
            memory_optimization_enabled=False,
            enable_debug_file_logging=True,
            enemy_rotation_delay=2,
            alert_cooldown_turns=10,
            chase_timeout_turns=15,
            enable_visual_mode=True
        )

    def _create_minimal_config(self) -> ValidationConfig:
        """最小設定"""
        return ValidationConfig(
            log_detail_level=LogDetailLevel.MINIMAL,
            max_solution_steps=200,
            comparison_timeout_seconds=10.0,
            memory_optimization_enabled=True,
            enable_debug_file_logging=False,
            position_tolerance=0.1
        )

    def _create_strict_config(self) -> ValidationConfig:
        """厳密検証設定"""
        return ValidationConfig(
            log_detail_level=LogDetailLevel.DETAILED,
            max_solution_steps=1000,
            comparison_timeout_seconds=120.0,
            position_tolerance=0.0,
            enemy_rotation_delay=3,
            vision_check_timing=VisionCheckTiming.BEFORE_ACTION,
            patrol_advancement_rule=PatrolAdvancementRule.DELAYED
        )

    def _serialize_enum_values(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enum値を文字列にシリアライズ"""
        serialized = config_data.copy()

        enum_fields = {
            'log_detail_level': LogDetailLevel,
            'vision_check_timing': VisionCheckTiming,
            'patrol_advancement_rule': PatrolAdvancementRule
        }

        for field_name, enum_class in enum_fields.items():
            if field_name in serialized and hasattr(serialized[field_name], 'value'):
                serialized[field_name] = serialized[field_name].value

        return serialized

    def _restore_enum_values(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """文字列からEnum値を復元"""
        restored = config_data.copy()

        enum_fields = {
            'log_detail_level': LogDetailLevel,
            'vision_check_timing': VisionCheckTiming,
            'patrol_advancement_rule': PatrolAdvancementRule
        }

        for field_name, enum_class in enum_fields.items():
            if field_name in restored and isinstance(restored[field_name], str):
                try:
                    restored[field_name] = enum_class(restored[field_name])
                except ValueError:
                    print(f"⚠️  Invalid {field_name} value: {restored[field_name]}, using default")
                    # デフォルト値を使用
                    restored[field_name] = getattr(ValidationConfig(), field_name)

        return restored

    def get_config_summary(self) -> str:
        """設定サマリーを取得"""
        if self.current_config is None:
            return "No configuration loaded"

        config = self.current_config
        summary = []
        summary.append(f"📋 Configuration Profile: {self.current_profile}")
        summary.append(f"🔍 Log Level: {config.log_detail_level.value}")
        summary.append(f"🎯 Max Solution Steps: {config.max_solution_steps}")
        summary.append(f"⏱️  Timeout: {config.comparison_timeout_seconds}s")
        summary.append(f"🎛️  Enemy Rotation Delay: {config.enemy_rotation_delay}")
        summary.append(f"👁️  Vision Timing: {config.vision_check_timing.value}")
        summary.append(f"🚶 Patrol Rule: {config.patrol_advancement_rule.value}")
        summary.append(f"🔧 Memory Optimization: {'✅' if config.memory_optimization_enabled else '❌'}")
        summary.append(f"📁 Debug Logging: {'✅' if config.enable_debug_file_logging else '❌'}")

        return "\n".join(summary)


# ファクトリー関数とグローバル管理
_global_config_manager: Optional[ConfigManager] = None


def get_global_config_manager() -> ConfigManager:
    """グローバル設定マネージャーを取得"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager


def create_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """設定マネージャー作成"""
    return ConfigManager(config_dir)