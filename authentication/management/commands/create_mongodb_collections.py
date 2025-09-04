"""
Django management command to create MongoDB collections and sample data.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from authentication.mongo_models import connect_to_mongodb, create_sample_data, disconnect_from_mongodb
from utils.mongodb import MongoDBManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create MongoDB collections and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample-data',
            action='store_true',
            help='Create sample data in collections',
        )
        parser.add_argument(
            '--collections-only',
            action='store_true',
            help='Create collections only without sample data',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting MongoDB collections setup...')
        )

        # Connect to MongoDB
        if not connect_to_mongodb():
            self.stdout.write(
                self.style.ERROR('Failed to connect to MongoDB. Please check your configuration.')
            )
            return

        manager = None
        try:
            # Create collections by creating indexes
            manager = MongoDBManager()
            
            if options['collections_only'] or not options['sample_data']:
                self.stdout.write('Creating MongoDB collections...')
                manager.create_indexes()
                self.stdout.write(
                    self.style.SUCCESS('✓ MongoDB collections created successfully')
                )
            
            if options['sample_data']:
                self.stdout.write('Creating sample data...')
                if create_sample_data():
                    self.stdout.write(
                        self.style.SUCCESS('✓ Sample data created successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Failed to create sample data')
                    )
            
            # Show collection stats
            self.stdout.write('\nCollection Statistics:')
            stats = manager.get_collection_stats('authentication_account')
            if stats:
                self.stdout.write(f'  authentication_account: {stats["count"]} documents')
            
            stats = manager.get_collection_stats('blog_post')
            if stats:
                self.stdout.write(f'  blog_post: {stats["count"]} documents')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during setup: {e}')
            )
            raise

        finally:
            if manager:
                manager.close()
            disconnect_from_mongodb()

        self.stdout.write(
            self.style.SUCCESS('MongoDB collections setup completed!')
        )
