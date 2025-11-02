"""
Module loader for The Hub.

Automatically discovers and registers available modules.
"""
from typing import Dict, Any
import logging
from sqlalchemy.orm import Session

from .base import registry, BaseModule
from .housekeeper import HousekeeperModule, SHOP_STEWARD_AVAILABLE
from .workflow_manager import WorkflowModule, WORKFLOW_AVAILABLE
from ..models.module import Module as ModuleModel, ModuleStatus
from ..database import SessionLocal

logger = logging.getLogger(__name__)


def load_modules(config: Dict[str, Any] = None) -> Dict[str, BaseModule]:
    """
    Load and register all available modules.

    Args:
        config: Optional configuration dictionary for modules

    Returns:
        dict: Dictionary of loaded modules
    """
    config = config or {}
    loaded_modules = {}

    # Load Housekeeper Module
    if SHOP_STEWARD_AVAILABLE:
        try:
            housekeeper_config = config.get("housekeeper", {
                "root_dir": "/data/shop",
                "hierarchical": True,
                "enforce_naming": True,
                "auto_rename": False
            })
            housekeeper = HousekeeperModule(config=housekeeper_config)
            if registry.register(housekeeper):
                loaded_modules["housekeeper"] = housekeeper
                logger.info("Loaded Housekeeper module")
        except Exception as e:
            logger.error(f"Failed to load Housekeeper module: {e}")
    else:
        logger.warning("Housekeeper module not available (shop_steward.py not found)")

    # Load Workflow Manager Module
    if WORKFLOW_AVAILABLE:
        try:
            workflow_config = config.get("workflow_manager", {
                "workflow_dir": "/data/workflow"
            })
            workflow = WorkflowModule(config=workflow_config)
            if registry.register(workflow):
                loaded_modules["workflow_manager"] = workflow
                logger.info("Loaded Workflow Manager module")
        except Exception as e:
            logger.error(f"Failed to load Workflow Manager module: {e}")
    else:
        logger.warning("Workflow Manager module not available (workflow.py not found)")

    # Future modules can be added here...
    # if MANUFACTURING_INTELLIGENCE_AVAILABLE:
    #     manufacturing_intelligence = ManufacturingIntelligenceModule(...)
    #     registry.register(manufacturing_intelligence)

    logger.info(f"Loaded {len(loaded_modules)} modules")
    return loaded_modules


def sync_modules_to_database():
    """
    Synchronize registered modules with the database.

    Creates or updates database records for all registered modules.
    """
    db = SessionLocal()
    try:
        for module_name in registry.list_modules():
            module = registry.get_module(module_name)

            # Check if module exists in database
            db_module = db.query(ModuleModel).filter(
                ModuleModel.name == module.name
            ).first()

            if db_module:
                # Update existing module
                db_module.display_name = module.display_name
                db_module.version = module.version
                db_module.description = module.__doc__ or ""
                db_module.status = (
                    ModuleStatus.ACTIVE if module.is_active else ModuleStatus.INACTIVE
                )
                db_module.config = module.config
                db_module.metrics = module.metrics
                db_module.last_run = module.last_run
                logger.info(f"Updated database record for module: {module.name}")
            else:
                # Create new module
                db_module = ModuleModel(
                    name=module.name,
                    display_name=module.display_name,
                    description=module.__doc__ or "",
                    version=module.version,
                    status=ModuleStatus.INACTIVE,
                    config=module.config,
                    metrics=module.metrics
                )
                db.add(db_module)
                logger.info(f"Created database record for module: {module.name}")

        db.commit()
        logger.info("Module database sync complete")

    except Exception as e:
        logger.error(f"Error syncing modules to database: {e}")
        db.rollback()
    finally:
        db.close()


def get_module_from_registry(module_name: str) -> BaseModule:
    """
    Get a module from the registry.

    Args:
        module_name: Name of the module

    Returns:
        Module instance

    Raises:
        ValueError: If module not found
    """
    module = registry.get_module(module_name)
    if not module:
        raise ValueError(f"Module {module_name} not found in registry")
    return module


def activate_module_from_db(module_id: str, db: Session) -> bool:
    """
    Activate a module and update database.

    Args:
        module_id: Database ID of the module
        db: Database session

    Returns:
        bool: True if successful
    """
    # Get module from database
    db_module = db.query(ModuleModel).filter(ModuleModel.id == module_id).first()
    if not db_module:
        logger.error(f"Module {module_id} not found in database")
        return False

    # Get module from registry
    try:
        module = get_module_from_registry(db_module.name)
    except ValueError as e:
        logger.error(str(e))
        return False

    # Activate module
    if registry.activate_module(module.name):
        db_module.status = ModuleStatus.ACTIVE
        db_module.config = module.config
        db.commit()
        logger.info(f"Activated module: {module.name}")
        return True
    else:
        db_module.status = ModuleStatus.ERROR
        db.commit()
        logger.error(f"Failed to activate module: {module.name}")
        return False


def deactivate_module_from_db(module_id: str, db: Session) -> bool:
    """
    Deactivate a module and update database.

    Args:
        module_id: Database ID of the module
        db: Database session

    Returns:
        bool: True if successful
    """
    # Get module from database
    db_module = db.query(ModuleModel).filter(ModuleModel.id == module_id).first()
    if not db_module:
        logger.error(f"Module {module_id} not found in database")
        return False

    # Get module from registry
    try:
        module = get_module_from_registry(db_module.name)
    except ValueError as e:
        logger.error(str(e))
        return False

    # Deactivate module
    if registry.deactivate_module(module.name):
        db_module.status = ModuleStatus.INACTIVE
        db_module.metrics = module.metrics
        db_module.last_run = module.last_run
        db.commit()
        logger.info(f"Deactivated module: {module.name}")
        return True
    else:
        logger.error(f"Failed to deactivate module: {module.name}")
        return False


def update_module_config_in_db(module_id: str, config: Dict[str, Any], db: Session) -> bool:
    """
    Update module configuration.

    Args:
        module_id: Database ID of the module
        config: New configuration
        db: Database session

    Returns:
        bool: True if successful
    """
    # Get module from database
    db_module = db.query(ModuleModel).filter(ModuleModel.id == module_id).first()
    if not db_module:
        logger.error(f"Module {module_id} not found in database")
        return False

    # Get module from registry
    try:
        module = get_module_from_registry(db_module.name)
    except ValueError as e:
        logger.error(str(e))
        return False

    # Update config
    module.update_config(config)
    db_module.config = module.config
    db.commit()
    logger.info(f"Updated config for module: {module.name}")
    return True
