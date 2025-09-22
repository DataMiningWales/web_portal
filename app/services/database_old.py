from neo4j import GraphDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from app.core.config import settings
from app.core.logging import get_logger
from app.models.subscription import Subscription, SubscriptionStatus


logger = get_logger(__name__)


class DatabaseService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
    
    def close(self):
        self.driver.close()
    
    def create_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Create a new subscription in the database"""
        request_id = str(uuid.uuid4())
        
        async with self.driver.session() as session:
            query = """
            CREATE (s:Subscription {
                request_id: $request_id,
                email: $email,
                name: $name,
                organization: $organization,
                interests: $interests,
                additional_data: $additional_data,
                status: $status,
                created_at: datetime(),
                updated_at: null
            })
            RETURN s.request_id as request_id
            """
            
            result = await session.run(
                query,
                request_id=request_id,
                email=subscription_data["email"],
                name=subscription_data.get("name"),
                organization=subscription_data.get("organization"),
                interests=subscription_data.get("interests"),
                additional_data=json.dumps(subscription_data.get("additional_data", {})),
                status=SubscriptionStatus.PENDING.value
            )
            
            record = await result.single()
            logger.info(f"Created subscription with ID: {request_id}")
            return record["request_id"]
    
    async def check_existing_subscription(self, email: str) -> Optional[Subscription]:
        """Check if a subscription already exists for the given email"""
        async with self.driver.session() as session:
            query = """
            MATCH (s:Subscription {email: $email})
            WHERE s.status IN ['pending', 'approved']
            RETURN s
            ORDER BY s.created_at DESC
            LIMIT 1
            """
            
            result = await session.run(query, email=email)
            record = await result.single()
            
            if record:
                subscription_data = record["s"]
                return Subscription(
                    request_id=subscription_data["request_id"],
                    email=subscription_data["email"],
                    name=subscription_data.get("name"),
                    organization=subscription_data.get("organization"),
                    interests=subscription_data.get("interests"),
                    additional_data=json.loads(subscription_data.get("additional_data", "{}")),
                    status=SubscriptionStatus(subscription_data["status"]),
                    created_at=subscription_data["created_at"],
                    updated_at=subscription_data.get("updated_at")
                )
            return None
    
    async def get_all_subscriptions(self, limit: int = 100, offset: int = 0) -> List[Subscription]:
        """Get all subscriptions for admin view"""
        async with self.driver.session() as session:
            query = """
            MATCH (s:Subscription)
            RETURN s
            ORDER BY s.created_at DESC
            SKIP $offset
            LIMIT $limit
            """
            
            result = await session.run(query, offset=offset, limit=limit)
            subscriptions = []
            
            async for record in result:
                subscription_data = record["s"]
                subscriptions.append(Subscription(
                    request_id=subscription_data["request_id"],
                    email=subscription_data["email"],
                    name=subscription_data.get("name"),
                    organization=subscription_data.get("organization"),
                    interests=subscription_data.get("interests"),
                    additional_data=json.loads(subscription_data.get("additional_data", "{}")),
                    status=SubscriptionStatus(subscription_data["status"]),
                    created_at=subscription_data["created_at"],
                    updated_at=subscription_data.get("updated_at")
                ))
            
            return subscriptions
    
    async def update_subscription_status(self, request_id: str, status: SubscriptionStatus) -> bool:
        """Update subscription status"""
        async with self.driver.session() as session:
            query = """
            MATCH (s:Subscription {request_id: $request_id})
            SET s.status = $status, s.updated_at = datetime()
            RETURN s.request_id as request_id
            """
            
            result = await session.run(
                query,
                request_id=request_id,
                status=status.value
            )
            
            record = await result.single()
            return record is not None


# Global database service instance
db_service = DatabaseService()