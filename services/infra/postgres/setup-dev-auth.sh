#!/bin/bash
# Setup PostgreSQL for local development with trust authentication
# This script copies the custom pg_hba.conf and reloads PostgreSQL configuration
# 
# Usage: ./setup-dev-auth.sh
# Or via Docker: docker exec mankkoo-postgres /bin/bash < setup-dev-auth.sh

set -e

echo "Setting up PostgreSQL trust authentication for local development..."

# Copy custom pg_hba.conf to PostgreSQL data directory
docker cp services/infra/postgres/pg_hba.conf mankkoo-postgres:/var/lib/postgresql/data/pg_hba.conf

echo "Custom pg_hba.conf copied to container"

# Reload PostgreSQL configuration
docker exec mankkoo-postgres psql -U postgres -c "SELECT pg_reload_conf();" > /dev/null

echo "✅ PostgreSQL configuration reloaded successfully"
echo ""
echo "PostgreSQL is now configured for trust authentication (development only)"
echo "You can now connect from WSL without password issues"
