# PostgreSQL with pgvector Extension

This directory contains the Dockerfile and initialization scripts needed to set up a PostgreSQL database with the pgvector extension for vector similarity search capabilities.

## What's included

- `Dockerfile` - Creates a PostgreSQL 14 instance with the pgvector extension installed
- `init-pgvector.sql` - SQL initialization script that enables the pgvector extension when the container starts

## How it works

The Dockerfile:

1. Uses the official PostgreSQL 14 image as a base
2. Installs necessary build dependencies
3. Downloads pgvector from GitHub (v0.5.1)
4. Compiles and installs the pgvector extension
5. Copies the init script that enables the extension when the container starts

## Usage

This database is automatically started as part of the python-backend service. You don't need to start it separately.

If you need to modify the database setup, edit files in this directory and rebuild the containers:

```bash
# From the python-backend directory
docker-compose down
docker-compose build
docker-compose up -d
```
