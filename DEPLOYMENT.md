# Identity runtime validation

Use the official educk-identity-db schema and an isolated PostgreSQL instance.
This API validates the schema; it does not create tables or run migrations.
The User adapter maps identity_schema.users.name/status to the domain name/active fields.

Required environment: DB_USER, DB_PASSWORD and JWT_SECRET (at least 32 UTF-8 bytes).
Configure DB_HOST, DB_PORT and DB_NAME for the selected environment. Use a distinct
database deployment, volume and signing secret for develop, qa and main.
JWT_EXPIRATION_MS defaults to 86400000. Tokens use HMAC, not RS256.

Run Java 21 Maven verification with:

    mvn verify -Dapi.version=1.44 -Didentity.db.path=/absolute/path/to/educk-identity-db

Docker must be available. The integration test copies the owning DB repository's
schema/table scripts into a disposable PostgreSQL container. It generates its own
credentials, inserts a user through the persistence adapter, then checks HTTP
login, refresh rotation, revoked-token rejection and logout. Never use production data.

GET /api/v1/auth/health is a liveness endpoint. Passing this test does not establish
the complete multi-child HU-003 acceptance criteria or full-system release readiness.
