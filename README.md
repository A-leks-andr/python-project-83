### Hexlet tests and linter status:
[![Actions Status](https://github.com/A-leks-andr/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/A-leks-andr/python-project-83/actions)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=A-leks-andr_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=A-leks-andr_python-project-83)

# Page Analyzer
[Page Analyzer](https://python-project-83-6r2e.onrender.com) is a site that analyzes the specified pages for SEO suitability:

## Access
Application is deployed to [render.com](https://render.com/)
[Page Analyzer](https://python-project-83-6r2e.onrender.com")

## Requirements
Python 3.13+

## Local Installation
### Clone repository
```bash
git clone https://github.com/A-leks-andr/python-project-83.git
cd python-project-83
make install # Install dependencies
make build # Build package
```

### Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

### Install application
```bash
make install
```

### Put secrets to .env file
```
echo SECRET_KEY="{flask_secret_key}"
echo DATABASE_URL="postgresql://{user}:{password}@127.0.0.1:5432/sites"
```

### Start local Postgresql database
```
docker run --name postgres16 \
  -e POSTGRES_USER=appuser \
  -e POSTGRES_PASSWORD=mypassword \
  -e POSTGRES_DB=sites \
  -p 5432:5432 \
  -d postgres:16

psql -a -d $DATABASE_URL -f database.sql
```

### Start development application
```
make dev
```

[def]: https://sonarcloud.io/summary/new_code?id=A-leks-andr_python-project-83