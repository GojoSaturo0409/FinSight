#!/bin/bash
set -e

# Update and add everything selectively
git add services/api_gateway
git commit -m "feat(arch): Implement Nginx API Gateway proxy routing"

git add services/transaction_service
git commit -m "feat(ingestion): Isolate transaction parsing modules, hook ML Active Learning feedback endpoints and migrate handlers"

git add services/budget_service
git commit -m "feat(budget): Complete Celery background worker setup passing Observer message deliveries through RabbitMQ"

git add services/analytics_service
git commit -m "feat(analytics): Migrate recommendations and report builder out of monolithic core"

git add services/shared
git commit -m "refactor(core): Decouple monolithic Database architecture into internal shared routing boundaries"

git add services/tests run_tests.sh
git commit -m "test(restructure): Deconstruct linear test suites into robust Pytest hierarchy running inside isolated conda scopes"

git add refactor_imports.py
git commit -m "chore: Automate codebase module refactoring" || true

# Try adding anything else leftover
git add .
git commit -m "chore: Final cleanup and alignment" || true

# Push all to remote repo
git push origin HEAD || echo "No remote configured or push failed, but commits are staged locally."
