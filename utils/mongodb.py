"""
MongoDB utilities for optimization and management.
"""
import logging
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB connection and optimization manager."""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            # Get MongoDB settings from Django settings
            mongodb_settings = getattr(settings, 'MONGODB_SETTINGS', {})
            
            if not mongodb_settings:
                raise ConnectionFailure("MongoDB settings not configured")
            
            # Extract connection parameters
            host = mongodb_settings.get('host', '')
            db_name = mongodb_settings.get('db', 'olaf_backend')
            
            # Create connection parameters
            connection_params = {
                'retryWrites': mongodb_settings.get('retryWrites', True),
                'w': mongodb_settings.get('w', 'majority'),
                'serverSelectionTimeoutMS': mongodb_settings.get('serverSelectionTimeoutMS', 30000),
                'connectTimeoutMS': mongodb_settings.get('connectTimeoutMS', 30000),
                'socketTimeoutMS': mongodb_settings.get('socketTimeoutMS', 30000),
                'maxPoolSize': mongodb_settings.get('maxPoolSize', 10),
                'minPoolSize': mongodb_settings.get('minPoolSize', 1),
                'maxIdleTimeMS': mongodb_settings.get('maxIdleTimeMS', 30000),
                'waitQueueTimeoutMS': mongodb_settings.get('waitQueueTimeoutMS', 5000),
            }
            
            # Only add SSL settings for Atlas connections
            if host.startswith('mongodb+srv://'):
                connection_params.update({
                    'ssl': mongodb_settings.get('ssl', True),
                    'ssl_cert_reqs': mongodb_settings.get('ssl_cert_reqs', 0),
                })
            
            # Add authentication if provided
            if mongodb_settings.get('username'):
                connection_params['username'] = mongodb_settings['username']
                connection_params['password'] = mongodb_settings.get('password', '')
                connection_params['authSource'] = mongodb_settings.get('authentication_source', 'admin')
                connection_params['authMechanism'] = mongodb_settings.get('authentication_mechanism', 'SCRAM-SHA-1')
            
            # Remove None values
            connection_params = {k: v for k, v in connection_params.items() if v is not None and v != ''}
            
            # Connect to MongoDB
            if host.startswith('mongodb+srv://'):
                # For Atlas, use the URI directly
                self.client = MongoClient(host, **connection_params)
            else:
                # For local MongoDB
                self.client = MongoClient(host, **connection_params)
            
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB Atlas: {e}")
            # If MongoDB connection fails, we can still allow the command to run
            # but with limited functionality
            logger.warning("MongoDB connection failed. Some features may not be available.")
            self.client = None
            self.db = None
    
    def create_indexes(self):
        """Create optimized indexes for collections."""
        if not self.client or not self.db:
            logger.warning("MongoDB not connected. Cannot create indexes.")
            return
            
        try:
            indexes = getattr(settings, 'MONGODB_INDEXES', {})
            
            for collection_name, index_list in indexes.items():
                collection = self.db[collection_name]
                
                for index_spec in index_list:
                    try:
                        # Create index with background=True for non-blocking operation
                        collection.create_index(
                            list(index_spec.items()),
                            background=True,
                            sparse=True
                        )
                        logger.info(f"Created index {index_spec} for collection {collection_name}")
                    except OperationFailure as e:
                        if "already exists" in str(e):
                            logger.info(f"Index {index_spec} already exists for collection {collection_name}")
                        else:
                            logger.error(f"Failed to create index {index_spec} for collection {collection_name}: {e}")
            
            logger.info("MongoDB indexes creation completed")
            
        except Exception as e:
            logger.error(f"Error creating MongoDB indexes: {e}")
            raise
    
    def get_collection_stats(self, collection_name):
        """Get statistics for a collection."""
        if not self.client or not self.db:
            logger.warning("MongoDB not connected. Cannot get collection stats.")
            return None
            
        try:
            collection = self.db[collection_name]
            stats = self.db.command("collStats", collection_name)
            return {
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avgObjSize': stats.get('avgObjSize', 0),
                'storageSize': stats.get('storageSize', 0),
                'indexes': stats.get('nindexes', 0),
                'totalIndexSize': stats.get('totalIndexSize', 0),
            }
        except Exception as e:
            logger.error(f"Error getting stats for collection {collection_name}: {e}")
            return None
    
    def optimize_collection(self, collection_name):
        """Optimize a collection by rebuilding indexes."""
        if not self.client or not self.db:
            logger.warning("MongoDB not connected. Cannot optimize collection.")
            return
            
        try:
            collection = self.db[collection_name]
            
            # Get current indexes
            indexes = list(collection.list_indexes())
            
            # Rebuild indexes
            for index in indexes:
                if index['name'] != '_id_':  # Skip default _id index
                    try:
                        collection.reindex()
                        logger.info(f"Rebuilt indexes for collection {collection_name}")
                        break  # reindex() rebuilds all indexes
                    except OperationFailure as e:
                        logger.error(f"Failed to rebuild indexes for {collection_name}: {e}")
            
        except Exception as e:
            logger.error(f"Error optimizing collection {collection_name}: {e}")
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def create_mongodb_indexes():
    """Django management command helper to create indexes."""
    manager = MongoDBManager()
    try:
        manager.create_indexes()
    finally:
        manager.close()


def get_mongodb_stats():
    """Get MongoDB database statistics."""
    manager = MongoDBManager()
    try:
        stats = {}
        collections = ['authentication_account', 'blog_post']
        
        for collection in collections:
            stats[collection] = manager.get_collection_stats(collection)
        
        return stats
    finally:
        manager.close()


def get_client():
    """Get MongoDB client instance."""
    manager = MongoDBManager()
    return manager.client


def get_database():
    """Get MongoDB database instance."""
    manager = MongoDBManager()
    return manager.db


# Connection pool for better performance
class MongoDBConnectionPool:
    """MongoDB connection pool for better performance."""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_client(self):
        """Get MongoDB client with connection pooling for Atlas."""
        if self._client is None:
            db_config = settings.DATABASES['default']
            client_config = db_config['CLIENT'].copy()
            options_config = db_config['OPTIONS'].copy()
            
            # Merge options into client config
            client_config.update(options_config)
            
            # Add Atlas-optimized connection pool settings
            client_config.update({
                'maxPoolSize': 10,  # Atlas limit
                'minPoolSize': 1,
                'maxIdleTimeMS': 30000,
                'waitQueueTimeoutMS': 5000,
                'serverSelectionTimeoutMS': 30000,  # Longer timeout for Atlas
                'connectTimeoutMS': 30000,
                'socketTimeoutMS': 30000,
            })
            
            # Remove None values
            client_config = {k: v for k, v in client_config.items() if v is not None and v != ''}
            
            # Handle Atlas URI format
            if 'host' in client_config and client_config['host'].startswith('mongodb+srv://'):
                # For Atlas, use the URI directly
                self._client = MongoClient(client_config['host'], **{k: v for k, v in client_config.items() if k != 'host'})
            else:
                # For local MongoDB
                self._client = MongoClient(**client_config)
        
        return self._client
    
    def get_database(self):
        """Get database instance."""
        client = self.get_client()
        db_config = settings.DATABASES['default']
        return client[db_config['NAME']]
