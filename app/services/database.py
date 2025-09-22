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
        # For now, we'll use a mock implementation since AuraDB connection isn't available
        self.driver = None
        self.mock_data = []
        logger.warning("Using mock database implementation - configure Neo4j/AuraDB for production")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def create_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Create a new subscription in the database"""
        request_id = str(uuid.uuid4())
        
        # Mock implementation for testing
        subscription = {
            "request_id": request_id,
            "email": subscription_data["email"],
            "name": subscription_data.get("name"),
            "organization": subscription_data.get("organization"),
            "interests": subscription_data.get("interests"),
            "additional_data": subscription_data.get("additional_data", {}),
            "status": SubscriptionStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        self.mock_data.append(subscription)
        logger.info(f"Created subscription with ID: {request_id}")
        return request_id
    
    def check_existing_subscription(self, email: str) -> Optional[Subscription]:
        """Check if a subscription already exists for the given email"""
        # Mock implementation
        for sub_data in self.mock_data:
            if (sub_data["email"] == email and 
                sub_data["status"] in [SubscriptionStatus.PENDING.value, SubscriptionStatus.APPROVED.value]):
                return Subscription(
                    request_id=sub_data["request_id"],
                    email=sub_data["email"],
                    name=sub_data.get("name"),
                    organization=sub_data.get("organization"),
                    interests=sub_data.get("interests"),
                    additional_data=sub_data.get("additional_data", {}),
                    status=SubscriptionStatus(sub_data["status"]),
                    created_at=sub_data["created_at"],
                    updated_at=sub_data.get("updated_at")
                )
        return None
    
    def get_all_subscriptions(self, limit: int = 100, offset: int = 0) -> List[Subscription]:
        """Get all subscriptions for admin view"""
        # Mock implementation
        sorted_data = sorted(self.mock_data, key=lambda x: x["created_at"], reverse=True)
        paginated_data = sorted_data[offset:offset + limit]
        
        subscriptions = []
        for sub_data in paginated_data:
            subscriptions.append(Subscription(
                request_id=sub_data["request_id"],
                email=sub_data["email"],
                name=sub_data.get("name"),
                organization=sub_data.get("organization"),
                interests=sub_data.get("interests"),
                additional_data=sub_data.get("additional_data", {}),
                status=SubscriptionStatus(sub_data["status"]),
                created_at=sub_data["created_at"],
                updated_at=sub_data.get("updated_at")
            ))
        
        return subscriptions
    
    def update_subscription_status(self, request_id: str, status: SubscriptionStatus) -> bool:
        """Update subscription status"""
        # Mock implementation
        for sub_data in self.mock_data:
            if sub_data["request_id"] == request_id:
                sub_data["status"] = status.value
                sub_data["updated_at"] = datetime.utcnow()
                logger.info(f"Updated subscription {request_id} status to {status.value}")
                return True
        return False


class Neo4jDatabaseService(DatabaseService):
    """Real Neo4j/AuraDB implementation - use when database is available"""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        logger.info("Connected to Neo4j/AuraDB")
    
    def create_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Create a new subscription in the database"""
        request_id = str(uuid.uuid4())
        
        with self.driver.session() as session:
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
            
            result = session.run(
                query,
                request_id=request_id,
                email=subscription_data["email"],
                name=subscription_data.get("name"),
                organization=subscription_data.get("organization"),
                interests=subscription_data.get("interests"),
                additional_data=json.dumps(subscription_data.get("additional_data", {})),
                status=SubscriptionStatus.PENDING.value
            )
            
            record = result.single()
            logger.info(f"Created subscription with ID: {request_id}")
            return record["request_id"]
    
    def check_existing_subscription(self, email: str) -> Optional[Subscription]:
        """Check if a subscription already exists for the given email"""
        with self.driver.session() as session:
            query = """
            MATCH (s:Subscription {email: $email})
            WHERE s.status IN ['pending', 'approved']
            RETURN s
            ORDER BY s.created_at DESC
            LIMIT 1
            """
            
            result = session.run(query, email=email)
            record = result.single()
            
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


# Use mock implementation by default, switch to Neo4jDatabaseService when database is available
db_service = DatabaseService()