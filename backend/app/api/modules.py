"""
Modules API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.module import Module, ModuleStatus
from ..schemas.module import ModuleResponse, ModuleConfig
from ..core.auth import require_hub_master
from ..modules.loader import (
    activate_module_from_db,
    deactivate_module_from_db,
    update_module_config_in_db,
    get_module_from_registry
)


router = APIRouter()


@router.get("", response_model=List[ModuleResponse])
async def list_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    List all modules (Hub Master only).
    """
    modules = db.query(Module).all()
    return modules


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Get a specific module by ID (Hub Master only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    return module


@router.post("/{module_id}/activate", response_model=ModuleResponse)
async def activate_module(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Activate a module (Hub Master only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Use loader to activate the module in the registry
    success = activate_module_from_db(module_id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate module"
        )

    db.refresh(module)
    return module


@router.post("/{module_id}/deactivate", response_model=ModuleResponse)
async def deactivate_module(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Deactivate a module (Hub Master only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Use loader to deactivate the module in the registry
    success = deactivate_module_from_db(module_id, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate module"
        )

    db.refresh(module)
    return module


@router.patch("/{module_id}/config", response_model=ModuleResponse)
async def update_module_config(
    module_id: str,
    config_data: ModuleConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Update module configuration (Hub Master only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Use loader to update config in the registry
    success = update_module_config_in_db(module_id, config_data.config, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update module config"
        )

    db.refresh(module)
    return module


@router.get("/{module_id}/metrics")
async def get_module_metrics(
    module_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Get module metrics (Hub Master only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Try to get live metrics from registry
    try:
        live_module = get_module_from_registry(module.name)
        live_status = live_module.get_status()

        return {
            "module_id": module.id,
            "module_name": module.name,
            "metrics": live_module.get_metrics(),
            "last_run": module.last_run,
            "status": module.status,
            "live_status": live_status
        }
    except (ValueError, Exception):
        # Fallback to database metrics if module not in registry
        return {
            "module_id": module.id,
            "module_name": module.name,
            "metrics": module.metrics,
            "last_run": module.last_run,
            "status": module.status
        }
