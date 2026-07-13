# 安装

## 安装包

`gcl_iam` 需要 Python 3.10 或更高版本。

```bash
python -m pip install gcl_iam
```

从源码开发时使用仓库的标准 tox 环境：

```bash
tox -e develop
```

环境创建在 `.tox/develop`。

## 运行时配置

内置 `HttpDriver` 需要三个值：

| 设置 | 用途 |
| --- | --- |
| `iam_endpoint` | 客户端专用 IAM endpoint；驱动在其下调用 `actions/jwks` 和 `actions/introspect`。 |
| `audience` | 服务期望的 JWT `aud` claim。 |
| `hs256_jwks_decryption_key` | 解密 JWKS 中 HS256 secret 的 32 字节 A256GCM key，可为 UTF-8 或 URL-safe base64。 |

使用 `oslo.config` 时可注册 `iam` 配置组：

```python
from gcl_iam import opts as iam_opts
from oslo_config import cfg

iam_opts.register_iam_cli_opts(cfg.CONF)
```

解析配置后创建驱动：

```python
from gcl_iam import drivers

iam_driver = drivers.HttpDriver(
    cfg.CONF.iam.iam_endpoint,
    cfg.CONF.iam.audience,
    cfg.CONF.iam.hs256_jwks_decryption_key,
)
```

## Secret 管理

HS256 JWKS 解密 key 和签名 key 都是 secret：从 secret manager 或受保护配置中
读取；不要提交、记录或放入错误报告；轮换时按 API 参考使用当前/旧 key。

RS256 使用方只需 JWKS 公钥。只有 token 签发方才应以私钥构造 `RS256`。

## 验证安装

```bash
python -c "from gcl_iam.enforcers import Enforcer; assert Enforcer(['demo.item.read']).enforce_raw('demo.item.read')"
```

导入和权限引擎正常时命令不会输出内容。
