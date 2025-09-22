from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
import uuid

from app.models.subscription import (
    SubscriptionRequest, 
    SubscriptionResponse, 
    AdminLoginRequest, 
    Token
)
from app.services.database import db_service
from app.services.email import email_service
from app.services.auth import authenticate_admin, create_access_token, get_current_admin
from app.core.config import settings
from app.core.logging import get_logger, log_request, log_subscription_event


router = APIRouter()
logger = get_logger(__name__)


@router.post("/subscriptions/", response_model=SubscriptionResponse)
async def create_subscription(subscription: SubscriptionRequest):
    """
    Handle subscription POST requests
    - Validates and stores subscription data in AuraDB
    - Checks for existing subscriptions
    - Generates unique request ID
    - Sends acknowledgment email
    """
    request_id = str(uuid.uuid4())
    
    # Log the request
    log_request(
        logger, 
        request_id, 
        "/subscriptions/", 
        "POST", 
        subscription.dict()
    )
    
    try:
        # Check for existing subscription
        existing = db_service.check_existing_subscription(subscription.email)
        if existing:
            log_subscription_event(
                logger,
                request_id,
                "duplicate_subscription_attempt",
                subscription.email,
                {"existing_request_id": existing.request_id}
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Subscription already exists for {subscription.email}"
            )
        
        # Create subscription in database
        subscription_data = subscription.dict()
        db_request_id = db_service.create_subscription(subscription_data)
        
        # Log subscription creation
        log_subscription_event(
            logger,
            db_request_id,
            "subscription_created",
            subscription.email,
            subscription_data
        )
        
        # Send acknowledgment email
        email_sent = await email_service.send_subscription_acknowledgment(
            subscription.email, 
            db_request_id, 
            subscription.name
        )
        
        if email_sent:
            log_subscription_event(
                logger,
                db_request_id,
                "acknowledgment_email_sent",
                subscription.email
            )
        else:
            log_subscription_event(
                logger,
                db_request_id,
                "acknowledgment_email_failed",
                subscription.email
            )
        
        # Send admin notification
        await email_service.send_admin_notification(subscription_data, db_request_id)
        
        return SubscriptionResponse(
            request_id=db_request_id,
            status="pending",
            message="Subscription request received and is pending approval"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing subscription: {str(e)}", extra={'request_id': request_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing subscription"
        )


@router.post("/admin/login", response_model=Token)
async def admin_login(login_data: AdminLoginRequest):
    """Admin login endpoint"""
    if not authenticate_admin(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": login_data.username}, 
        expires_delta=access_token_expires
    )
    
    logger.info(f"Admin login successful for user: {login_data.username}")
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }