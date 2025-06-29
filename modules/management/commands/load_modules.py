"""
Management command to load modules and register their models.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
from django.contrib import admin
from modules.manager import module_manager
from modules.base import module_registry


class Command(BaseCommand):
    help = 'Load modules and register their models with Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--install',
            action='store_true',
            help='Install modules after loading',
        )
        parser.add_argument(
            '--migrate',
            action='store_true',
            help='Run migrations for module models',
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Load specific module only',
        )

    def handle(self, *args, **options):
        self.stdout.write('Loading modules...')
        
        if options['module']:
            # Load specific module
            module_name = options['module']
            self.stdout.write(f'Loading module: {module_name}')
            
            module = module_manager.load_module(module_name)
            if module:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully loaded module: {module_name}')
                )
                
                if options['install']:
                    success = module_manager.install_module(module_name)
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully installed module: {module_name}')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to install module: {module_name}')
                        )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to load module: {module_name}')
                )
        else:
            # Load all modules
            loaded_modules = module_manager.load_all_modules()
            
            if loaded_modules:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully loaded {len(loaded_modules)} modules:')
                )
                for module_name, module in loaded_modules.items():
                    self.stdout.write(f'  - {module_name}: {module.name}')
            else:
                self.stdout.write(self.style.WARNING('No modules found to load.'))
            
            if options['install']:
                self.stdout.write('Installing modules...')
                for module_name in loaded_modules.keys():
                    success = module_manager.install_module(module_name)
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f'  - {module_name}: Installed successfully')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'  - {module_name}: Installation failed')
                        )
            
            if options['migrate']:
                self.stdout.write('Running migrations...')
                call_command('makemigrations')
                call_command('migrate')
        
        # Register models with admin
        self.stdout.write('Registering models with Django admin...')
        module_manager.register_module_models()
        
        self.stdout.write(
            self.style.SUCCESS('Module loading completed!')
        ) 