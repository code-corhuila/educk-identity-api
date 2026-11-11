# Identity runtime validation

Use the official `educk-identity-db` schema and an isolated PostgreSQL instance.
This API validates the schema; it does not create tables or run migrations.
The User adapter maps `identity_schema.users.name` / `status` to the domain `name` / `active` fields.

Required environment variables:
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- `JWT_PRIVATE_KEY`: PKCS#8 PEM RSA private key (at least 2048 bits), used solely by Identity to sign access tokens with `RS256`
- `JWT_PUBLIC_KEY`: X.509 SPKI PEM RSA public key shared with downstream services for token verification
- `JWT_EXPIRATION_SECONDS`: access-token lifetime in seconds (defaults to `900`, hard maximum `3600`)

Use a distinct database deployment, volume, and RSA key pair for `develop`, `qa`, and `main`.

## Generating a local development RSA key pair

```sh
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out private.pem
openssl rsa -pubout -in private.pem -out public.pem
```

Never commit PEM files or private keys to git. Pass their PEM content via environment variables.

## Running verification

Run Java 21 Maven verification with:

    mvn verify -Dapi.version=1.44 -Didentity.db.path=/absolute/path/to/educk-identity-db

Docker must be available for PostgreSQL integration tests. Unit tests can run standalone via `mvn test -Dtest=JwtSecurityTest`.
`GET /api/v1/auth/health` is a liveness endpoint.
