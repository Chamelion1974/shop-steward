"""
Base module class and registry for The Hub plugin system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseModule(ABC):
    """
    Base class for all Hub modules.

    All modules must inherit from this class and implement the required methods.
    Modules are plugins that extend The Hub with specialized functionality.
    """

    def __init__(self, name: str, display_name: str, version: str, config: Dict[str, Any] = None):
        """
        Initialize the module.

        Args:
            name: Unique module identifier (snake_case)
            display_name: Human-readable module name
            version: Module version (semver format)
            config: Module configuration dictionary
        """
        self.name = name
        self.display_name = display_name
        self.version = version
        self.config = config or {}
        self.is_active = False
        self.metrics: Dict[str, Any] = {}
        self.last_run: Optional[datetime] = None
        self.logger = logging.getLogger(f"module.{name}")

    @abstractmethod
    def activate(self) -> bool:
        """
        Activate the module.

        This method is called when the module is activated from The Hub.
        Use this to start background processes, initialize resources, etc.

        Returns:
            bool: True if activation was successful, False otherwise
        """
        pass

    @abstractmethod
    def deactivate(self) -> bool:
        """
        Deactivate the module.

        This method is called when the module is deactivated from The Hub.
        Use this to stop background processes, clean up resources, etc.

        Returns:
            bool: True if deactivation was successful, False otherwise
        """
        pass

    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data with this module.

        This is the main entry point for module functionality.
        Called when the module needs to process something.

        Args:
            data: Input data dictionary

        Returns:
            dict: Result dictionary with processing outcome
        """
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current module status.

        Returns:
            dict: Status information including health, metrics, etc.
        """
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get module performance metrics.

        Returns:
            dict: Metrics dictionary
        """
        return self.metrics

    def update_metrics(self, metric_name: str, value: Any):
        """
        Update a metric value.

        Args:
            metric_name: Name of the metric
            value: New value
        """
        self.metrics[metric_name] = value

    def increment_metric(self, metric_name: str, amount: int = 1):
        """
        Increment a metric counter.

        Args:
            metric_name: Name of the metric
            amount: Amount to increment by
        """
        current = self.metrics.get(metric_name, 0)
        self.metrics[metric_name] = current + amount

    def health_check(self) -> bool:
        """
        Perform a health check on the module.

        Returns:
            bool: True if module is healthy, False otherwise
        """
        try:
            status = self.get_status()
            return status.get("healthy", True)
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def update_config(self, config: Dict[str, Any]):
        """
        Update module configuration.

        Args:
            config: New configuration dictionary
        """
        self.config.update(config)

    def log_activity(self, message: str, level: str = "info"):
        """
        Log module activity.

        Args:
            message: Log message
            level: Log level (debug, info, warning, error)
        """
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(message)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} v{self.version}>"


class ModuleRegistry:
    """
    Registry for managing Hub modules.

    This class keeps track of all available modules and provides
    methods to register, activate, and manage them.
    """

    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.logger = logging.getLogger("module.registry")

    def register(self, module: BaseModule) -> bool:
        """
        Register a module with the registry.

        Args:
            module: Module instance to register

        Returns:
            bool: True if registration was successful
        """
        if module.name in self.modules:
            self.logger.warning(f"Module {module.name} already registered")
            return False

        self.modules[module.name] = module
        self.logger.info(f"Registered module: {module.name} v{module.version}")
        return True

    def unregister(self, module_name: str) -> bool:
        """
        Unregister a module from the registry.

        Args:
            module_name: Name of the module to unregister

        Returns:
            bool: True if unregistration was successful
        """
        if module_name not in self.modules:
            self.logger.warning(f"Module {module_name} not found")
            return False

        module = self.modules[module_name]
        if module.is_active:
            module.deactivate()

        del self.modules[module_name]
        self.logger.info(f"Unregistered module: {module_name}")
        return True

    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Get a module by name.

        Args:
            module_name: Name of the module

        Returns:
            Module instance or None if not found
        """
        return self.modules.get(module_name)

    def list_modules(self) -> List[str]:
        """
        Get list of all registered module names.

        Returns:
            List of module names
        """
        return list(self.modules.keys())

    def list_active_modules(self) -> List[str]:
        """
        Get list of active module names.

        Returns:
            List of active module names
        """
        return [name for name, module in self.modules.items() if module.is_active]

    def activate_module(self, module_name: str) -> bool:
        """
        Activate a module.

        Args:
            module_name: Name of the module to activate

        Returns:
            bool: True if activation was successful
        """
        module = self.get_module(module_name)
        if not module:
            self.logger.error(f"Module {module_name} not found")
            return False

        if module.is_active:
            self.logger.warning(f"Module {module_name} already active")
            return True

        try:
            if module.activate():
                module.is_active = True
                self.logger.info(f"Activated module: {module_name}")
                return True
            else:
                self.logger.error(f"Failed to activate module: {module_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error activating module {module_name}: {e}")
            return False

    def deactivate_module(self, module_name: str) -> bool:
        """
        Deactivate a module.

        Args:
            module_name: Name of the module to deactivate

        Returns:
            bool: True if deactivation was successful
        """
        module = self.get_module(module_name)
        if not module:
            self.logger.error(f"Module {module_name} not found")
            return False

        if not module.is_active:
            self.logger.warning(f"Module {module_name} already inactive")
            return True

        try:
            if module.deactivate():
                module.is_active = False
                self.logger.info(f"Deactivated module: {module_name}")
                return True
            else:
                self.logger.error(f"Failed to deactivate module: {module_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error deactivating module {module_name}: {e}")
            return False

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all modules.

        Returns:
            dict: Dictionary mapping module names to their status
        """
        return {
            name: module.get_status()
            for name, module in self.modules.items()
        }


# Global module registry instance
registry = ModuleRegistry()
