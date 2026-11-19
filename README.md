# Olive Branch Hotel

This repository contains the Stage 1 development foundation. Django and Django REST Framework handle staff sign-in and permissions. Next.js provides the local staff entry page. PostgreSQL stores the fictional fixtures and append-only audit events.

## Start on your computer

Install Docker with Docker Compose v2, Python 3.12, [uv](https://docs.astral.sh/uv/getting-started/installation/), Node.js 24 with npm, and GNU Make. On Windows, use WSL 2 with Docker Desktop integration and install the command-line tools inside WSL.

From a terminal:

```sh
git clone https://github.com/karakaraye/OLIVE-BRANCH.git
cd OLIVE-BRANCH
make install
make db
make migrate
make seed
make start
```

Keep that terminal open. In a second terminal, from the same repository directory:

```sh
make frontend
```

Open [http://localhost:3000](http://localhost:3000) and select **Staff sign in**. Sign in as `demo-manager` with password `olive-demo-local-only`. Select **Foundation records** to see the 20 fictional rooms and two outlets. Try `demo-reception` with the same password to see the restricted workspace. The review screen and its API return HTTP 403 for reception.

The other demo accounts are `demo-cashier`, `demo-stores`, `demo-accountant`, `demo-owner`, and `demo-admin`. They share the local demo password. These are Django group memberships. The demo admin has foundation access and is a regular Django user. The production settings disable demo seeding.

Press Ctrl+C in both terminals to stop Django and Next.js. Run `docker compose down` to stop PostgreSQL and retain its data. To use another host database port, export `OLIVE_DB_PORT` before running the Make commands in both terminals.

### Use the development demo on a trusted LAN

After the first installation, the staff pages, dependencies and assets are served locally. To use another computer on the LAN, substitute the server's LAN address for `192.168.1.10` in the following commands, then open port 3000 on that address in the browser. PostgreSQL stays bound to loopback.

```sh
# Terminal 1
DJANGO_ALLOWED_HOSTS=192.168.1.10,localhost,127.0.0.1 make start BACKEND_HOST=0.0.0.0
# Terminal 2
OLIVE_STAFF_ORIGIN=http://192.168.1.10:8000 make frontend FRONTEND_HOST=0.0.0.0
```

The LAN commands are for the fictional HTTP demo. A hotel deployment requires local HTTPS, named staff accounts and the production settings. Select `config.settings.prod` with `DJANGO_SETTINGS_MODULE` and provide `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `POSTGRES_PASSWORD`, and the appropriate PostgreSQL connection settings. The production settings enforce HTTPS and secure session and CSRF cookies.

## Checks and build

Run from the repository root with PostgreSQL running:

```sh
make lint
make test
make build
```

`make test` creates and drops a separate PostgreSQL test database and runs the frontend tests. CI also applies migrations, seeds fixtures and checks for missing migrations. The backend and frontend lockfiles support repeatable dependency installation. For a source release, archive a tagged commit with `git archive` and use the same install, migration and build commands.

## Verify a demo database restore

Use a fresh database name. The `createdb` command exits with an error if the example database already exists. Run the commands from the repository root after migrating and seeding.

```sh
docker compose exec -T db pg_dump -U olive_branch -Fc olive_branch > /tmp/olive-branch-demo.dump
docker compose exec -T db createdb -U olive_branch olive_branch_restore
docker compose exec -T db pg_restore --exit-on-error --single-transaction -U olive_branch -d olive_branch_restore < /tmp/olive-branch-demo.dump
POSTGRES_DB=olive_branch_restore uv run --locked --project backend python backend/manage.py migrate --check
docker compose exec -T db psql -U olive_branch -d olive_branch_restore -c \
  'SELECT (SELECT count(*) FROM rooms_room) AS rooms, (SELECT count(*) FROM outlets_outlet) AS outlets, (SELECT count(*) FROM auth_user) AS users, (SELECT count(*) FROM audit_auditevent) AS audit_events;'
```

A fresh demo dump should show 20 rooms, two outlets, seven users and one audit event. Switch `POSTGRES_DB` back to your usual database before running the app.
