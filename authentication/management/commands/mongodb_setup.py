"""
Django management command for MongoDB setup and optimization.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from utils.mongodb import MongoDBManager, get_mongodb_stats
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Setup and optimize MongoDB for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-indexes',
            action='store_true',
            help='Create optimized indexes for collections',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show MongoDB database statistics',
        )
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Optimize collections by rebuilding indexes',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization tasks',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting MongoDB optimization...')
        )

        manager = MongoDBManager()
        
        try:
            if options['create_indexes'] or options['all']:
                self.stdout.write('Creating MongoDB indexes...')
                manager.create_indexes()
                self.stdout.write(
                    self.style.SUCCESS('✓ MongoDB indexes created successfully')
                )

            if options['stats'] or options['all']:
                self.stdout.write('Gathering MongoDB statistics...')
                stats = get_mongodb_stats()
                
                for collection, stat in stats.items():
                    if stat:
                        self.stdout.write(f'\nCollection: {collection}')
                        self.stdout.write(f'  Documents: {stat["count"]:,}')
                        self.stdout.write(f'  Size: {stat["size"]:,} bytes')
                        self.stdout.write(f'  Avg Object Size: {stat["avgObjSize"]:,} bytes')
                        self.stdout.write(f'  Storage Size: {stat["storageSize"]:,} bytes')
                        self.stdout.write(f'  Indexes: {stat["indexes"]}')
                        self.stdout.write(f'  Total Index Size: {stat["totalIndexSize"]:,} bytes')

            if options['optimize'] or options['all']:
                self.stdout.write('Optimizing collections...')
                collections = ['authentication_account', 'blog_post']
                
                for collection in collections:
                    self.stdout.write(f'Optimizing {collection}...')
                    manager.optimize_collection(collection)
                
                self.stdout.write(
                    self.style.SUCCESS('✓ Collections optimized successfully')
                )

            if not any([options['create_indexes'], options['stats'], options['optimize'], options['all']]):
                self.stdout.write(
                    self.style.WARNING('No action specified. Use --help to see available options.')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during MongoDB optimization: {e}')
            )
            raise

        finally:
            manager.close()

        self.stdout.write(
            self.style.SUCCESS('MongoDB optimization completed!')
        )
