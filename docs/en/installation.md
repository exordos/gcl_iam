# Installation

## Install the package

`gcl_iam` requires Python 3.10 or newer.

```bash
python -m pip install gcl_iam
```

For development from a checkout, use the repository's standard tox
environment:

```bash
tox -e develop
```

The environment is created in `.tox/develop`.

## Runtime configuration

Services using the built-in `HttpDriver` need three values:

| Setting | Purpose |
| --- | --- |
| `iam_endpoint` | Client-specific IAM endpoint. The driver calls `actions/jwks` and `actions/introspect` below it. |
| `audience` | Expected JWT `aud` claim for the service. |
| `hs256_jwks_decryption_key` | 32-byte A256GCM key used to decrypt HS256 secrets returned by JWKS. It may be raw UTF-8 or URL-safe base64. |

Applications using `oslo.config` can register these options in the `iam`
group:

```python
from gcl_iam import opts as iam_opts
from oslo_config import cfg

iam_opts.register_iam_cli_opts(cfg.CONF)
```

Read the values only after parsing the application configuration, then build
the driver:

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    cfg.CONF.iam.iam_endpoint,
    cfg.CONF.iam.audience,
    cfg.CONF.iam.hs256_jwks_decryption_key,
)
```

## Secret handling

Treat the HS256 JWKS decryption key and all signing keys as secrets:

- load them from a secret manager or protected runtime configuration;
- never commit them to a repository;
- do not include them in logs or error reports; and
- rotate them using the current/previous-key support described in the API
  reference.

RS256 consumers receive public keys from JWKS and do not need private signing
keys. Only token issuers should construct `RS256` with a private key.

## Verify the installation

```bash
python -c "from gcl_iam.enforcers import Enforcer; assert Enforcer(['demo.item.read']).enforce_raw('demo.item.read')"
```

The command completes without output when the package can be imported and the
permission engine works.
