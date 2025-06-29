.PHONY: help install build watch dev clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies for SCSS compilation
	. venv/bin/activate && pip install libsass

build: ## Build CSS from SCSS (compressed)
	. venv/bin/activate && python -m sass static/scss/style.scss:static/css/style.css --style compressed

watch: ## Watch SCSS files and compile on changes (compressed)
	. venv/bin/activate && python -m sass --watch static/scss/style.scss:static/css/style.css --style compressed

dev: ## Watch SCSS files and compile on changes (expanded for debugging)
	. venv/bin/activate && python -m sass --watch static/scss/style.scss:static/css/style.css --style expanded

clean: ## Clean compiled CSS files
	rm -f static/css/style.css
	rm -f static/css/style.css.map

setup: install build ## Setup the project (install dependencies and build CSS)

# Django commands
runserver: ## Run Django development server
	. venv/bin/activate && python manage.py runserver

migrate: ## Run Django migrations
	. venv/bin/activate && python manage.py migrate

makemigrations: ## Make Django migrations
	. venv/bin/activate && python manage.py makemigrations

collectstatic: ## Collect static files
	. venv/bin/activate && python manage.py collectstatic --noinput

# Module management
load-modules: ## Load and install modules
	. venv/bin/activate && python manage.py load_modules

# Development workflow
dev-setup: setup ## Complete development setup
	@echo "Development setup complete!"
	@echo "Run 'make dev' to start SCSS watching"
	@echo "Run 'make runserver' to start Django server" 