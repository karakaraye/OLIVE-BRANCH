# Olive Branch Hotel

This repository contains the Stage 1 development foundation. Django and Django REST Framework enforce staff sessions and permissions. Next.js provides the staff sign-in, role demo, account administration and audit search. PostgreSQL stores the fictional fixtures and append-only audit events.

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

Open [http://localhost:3000](http://localhost:3000) and sign in. The demo accounts are `demo-reception`, `demo-cashier`, `demo-stores`, `demo-accountant`, `demo-manager`, `demo-owner` and `demo-admin`. All use the password `olive-demo-local-only`. Each role can open its designated screen and try a denied screen to see the server enforce the permission. Demo screens represent access boundaries for future modules. The seeded cashier is assigned to Restaurant.

Sign in as `demo-admin` to create named accounts, change roles, assign an outlet to a cashier, or disable and re-enable accounts. Administrative changes require a reason. Use **Search audit events** to filter by actor, affected record, and Africa/Lagos business date. Failed sign-ins show the attempted username as unverified. Sessions expire 30 minutes after sign-in. Disabling an account blocks its next request and revokes old sessions, even if the account is later re-enabled.

The production settings disable demo seeding. The development login, account changes and audit search all work through the Next.js origin. Django validates permissions and CSRF on the server.

Press Ctrl+C in both terminals to stop Django and Next.js. Run `docker compose down` to stop PostgreSQL and retain its data. To use another host database port, export `OLIVE_DB_PORT` before running the Make commands in both terminals.

### Use the development demo on a trusted LAN

After initial installation, staff pages and assets are served locally. Substitute your server's LAN address for `192.168.1.10`, then open port 3000 on that address in the browser. Django and PostgreSQL stay on loopback.

```sh
# Terminal 1
DJANGO_ALLOWED_HOSTS=192.168.1.10,localhost,127.0.0.1 make start
# Terminal 2
make frontend FRONTEND_HOST=0.0.0.0
```

The example uses HTTP for the fictional LAN demo. A hotel deployment requires local HTTPS, named accounts, and the production settings. Select `config.settings.prod` with `DJANGO_SETTINGS_MODULE` and set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `POSTGRES_PASSWORD`, and the PostgreSQL connection settings. Keep Django behind a trusted proxy that replaces the forwarded host and protocol headers. If Next.js and Django run on separate hosts, set `OLIVE_BACKEND_ORIGIN` to Django's private origin when building and starting Next.js.

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

A fresh demo dump should show 20 rooms, two outlets, seven users and at least the seed audit event. Compare the actual audit count with the source database. Switch `POSTGRES_DB` back to your usual database before running the app.
