from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

from app.models.subscription import Subscription, SubscriptionStatus
from app.services.database import db_service
from app.services.auth import get_current_admin
from app.core.logging import get_logger


router = APIRouter()
logger = get_logger(__name__)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_admin: str = Depends(get_current_admin)):
    """Admin dashboard page"""
    try:
        # Get recent subscriptions for dashboard overview
        recent_subscriptions = db_service.get_all_subscriptions(limit=10)
        
        return templates.TemplateResponse(
            "admin_dashboard.html",
            {
                "request": request,
                "admin_user": current_admin,
                "recent_subscriptions": recent_subscriptions
            }
        )
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading dashboard"
        )


@router.get("/subscriptions/", response_model=List[Subscription])
async def get_all_subscriptions(
    limit: int = 100, 
    offset: int = 0,
    current_admin: str = Depends(get_current_admin)
):
    """Get all subscriptions for admin review"""
    try:
        subscriptions = db_service.get_all_subscriptions(limit=limit, offset=offset)
        logger.info(f"Admin {current_admin} accessed subscriptions list")
        return subscriptions
    except Exception as e:
        logger.error(f"Error retrieving subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving subscriptions"
        )


@router.get("/subscriptions/view/", response_class=HTMLResponse)
async def view_subscriptions(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_admin: str = Depends(get_current_admin)
):
    """View subscriptions in admin interface"""
    try:
        subscriptions = db_service.get_all_subscriptions(limit=limit, offset=offset)
        
        return templates.TemplateResponse(
            "subscriptions_list.html",
            {
                "request": request,
                "admin_user": current_admin,
                "subscriptions": subscriptions,
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        logger.error(f"Error loading subscriptions view: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading subscriptions view"
        )


@router.post("/subscriptions/{request_id}/approve")
async def approve_subscription(
    request_id: str,
    current_admin: str = Depends(get_current_admin)
):
    """Approve a subscription request"""
    try:
        success = db_service.update_subscription_status(
            request_id, 
            SubscriptionStatus.APPROVED
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        logger.info(f"Subscription {request_id} approved by admin {current_admin}")
        return {"message": "Subscription approved", "request_id": request_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving subscription {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error approving subscription"
        )


@router.post("/subscriptions/{request_id}/reject")
async def reject_subscription(
    request_id: str,
    current_admin: str = Depends(get_current_admin)
):
    """Reject a subscription request"""
    try:
        success = db_service.update_subscription_status(
            request_id, 
            SubscriptionStatus.REJECTED
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        logger.info(f"Subscription {request_id} rejected by admin {current_admin}")
        return {"message": "Subscription rejected", "request_id": request_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting subscription {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error rejecting subscription"
        )