"""
Housekeeper Module - File Organization and Management

Integrates the shop_steward.py functionality into The Hub as a module.
"""
from typing import Dict, Any
from pathlib import Path
import sys
from datetime import datetime

# Add root directory to path to import shop_steward
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .base import BaseModule

# Import the ShopSteward class from the CLI tool
try:
    from shop_steward import ShopSteward
    SHOP_STEWARD_AVAILABLE = True
except ImportError:
    SHOP_STEWARD_AVAILABLE = False
    ShopSteward = None


class HousekeeperModule(BaseModule):
    """
    Housekeeper module for automated file organization.

    This module integrates the Shop Steward file organization system
    into The Hub, providing:
    - Automated file categorization
    - Hierarchical folder structure management
    - Real-time monitoring of directories
    - Naming convention enforcement
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="housekeeper",
            display_name="Housekeeper",
            version="1.0.0",
            config=config or {}
        )
        self.shop_steward: Optional[ShopSteward] = None
        self.monitor_path: Optional[str] = None
        self.is_monitoring = False

    def activate(self) -> bool:
        """Activate the Housekeeper module."""
        if not SHOP_STEWARD_AVAILABLE:
            self.log_activity("ShopSteward not available", "error")
            return False

        try:
            # Get configuration
            root_dir = self.get_config("root_dir", "/data/shop")
            hierarchical = self.get_config("hierarchical", False)
            enforce_naming = self.get_config("enforce_naming", False)
            auto_rename = self.get_config("auto_rename", False)

            # Initialize ShopSteward
            self.shop_steward = ShopSteward(
                root_dir=Path(root_dir),
                hierarchical=hierarchical,
                enforce_naming=enforce_naming,
                auto_rename=auto_rename
            )

            # Initialize folder structure
            self.shop_steward.init_folders()

            self.log_activity(f"Housekeeper activated with root: {root_dir}")
            self.update_metrics("activations", 1)

            # Start monitoring if configured
            monitor_path = self.get_config("monitor_path")
            if monitor_path:
                self.start_monitoring(monitor_path)

            return True

        except Exception as e:
            self.log_activity(f"Failed to activate: {e}", "error")
            return False

    def deactivate(self) -> bool:
        """Deactivate the Housekeeper module."""
        try:
            # Stop monitoring if active
            if self.is_monitoring:
                self.stop_monitoring()

            self.shop_steward = None
            self.log_activity("Housekeeper deactivated")
            return True

        except Exception as e:
            self.log_activity(f"Failed to deactivate: {e}", "error")
            return False

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process files with the Housekeeper.

        Args:
            data: Dictionary with:
                - action: 'organize', 'archive', 'init'
                - path: Path to process
                - dry_run: Whether to do a dry run (optional)
                - customer: Customer name for hierarchical mode (optional)

        Returns:
            dict: Result with stats and any errors
        """
        if not self.shop_steward:
            return {
                "success": False,
                "error": "Housekeeper not activated"
            }

        action = data.get("action")
        path = data.get("path")
        dry_run = data.get("dry_run", False)

        try:
            if action == "organize":
                if not path:
                    return {"success": False, "error": "Path required for organize action"}

                customer = data.get("customer")
                stats = self.shop_steward.organize_directory(
                    Path(path),
                    customer=customer,
                    dry_run=dry_run
                )

                self.increment_metric("files_processed", stats.get("total_files", 0))
                self.last_run = datetime.utcnow()

                return {
                    "success": True,
                    "stats": stats,
                    "dry_run": dry_run
                }

            elif action == "archive":
                if not path:
                    return {"success": False, "error": "Path required for archive action"}

                self.shop_steward.archive_folder(Path(path), dry_run=dry_run)

                self.increment_metric("folders_archived")
                self.last_run = datetime.utcnow()

                return {
                    "success": True,
                    "message": f"Archived {path}",
                    "dry_run": dry_run
                }

            elif action == "init":
                self.shop_steward.init_folders()

                return {
                    "success": True,
                    "message": "Folder structure initialized"
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            self.log_activity(f"Error processing {action}: {e}", "error")
            self.increment_metric("errors")
            return {
                "success": False,
                "error": str(e)
            }

    def get_status(self) -> Dict[str, Any]:
        """Get current Housekeeper status."""
        return {
            "healthy": self.shop_steward is not None,
            "active": self.is_active,
            "monitoring": self.is_monitoring,
            "monitor_path": self.monitor_path,
            "config": {
                "root_dir": self.get_config("root_dir"),
                "hierarchical": self.get_config("hierarchical"),
                "enforce_naming": self.get_config("enforce_naming"),
                "auto_rename": self.get_config("auto_rename"),
            },
            "metrics": self.get_metrics(),
            "last_run": self.last_run.isoformat() if self.last_run else None
        }

    def start_monitoring(self, path: str) -> bool:
        """
        Start real-time monitoring of a directory.

        Args:
            path: Directory path to monitor

        Returns:
            bool: True if monitoring started successfully
        """
        if not self.shop_steward:
            return False

        try:
            # Note: Actual monitoring would require watchdog integration
            # For now, just mark as monitoring enabled
            self.monitor_path = path
            self.is_monitoring = True
            self.log_activity(f"Started monitoring: {path}")
            return True
        except Exception as e:
            self.log_activity(f"Failed to start monitoring: {e}", "error")
            return False

    def stop_monitoring(self) -> bool:
        """
        Stop real-time monitoring.

        Returns:
            bool: True if monitoring stopped successfully
        """
        try:
            self.monitor_path = None
            self.is_monitoring = False
            self.log_activity("Stopped monitoring")
            return True
        except Exception as e:
            self.log_activity(f"Failed to stop monitoring: {e}", "error")
            return False

    def organize_path(self, path: str, customer: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """
        Convenience method to organize a specific path.

        Args:
            path: Path to organize
            customer: Customer name for hierarchical mode
            dry_run: Whether to do a dry run

        Returns:
            dict: Results of organization
        """
        return self.process({
            "action": "organize",
            "path": path,
            "customer": customer,
            "dry_run": dry_run
        })

    def archive_path(self, path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Convenience method to archive a path.

        Args:
            path: Path to archive
            dry_run: Whether to do a dry run

        Returns:
            dict: Results of archiving
        """
        return self.process({
            "action": "archive",
            "path": path,
            "dry_run": dry_run
        })
