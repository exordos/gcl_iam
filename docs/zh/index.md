# gcl_iam

`gcl_iam` 为 Python RESTAlchemy 服务提供认证与授权：验证 JWT，通过 IAM
驱动获取身份和权限，将数据放入请求上下文，并在控制器和字段序列化中执行策略。

## 功能

- 验证 HS256/RS256 JWT，并在密钥轮换时回退到旧密钥。
- 从远程 IAM 获取 JWKS 和 introspection，也支持自定义驱动。
- 使用 `service.resource.action` 权限格式，各层均支持 `*`。
- 按 token 的 `project_id` 限制项目资源，并保护全局和嵌套资源。
- 为指定操作要求已验证 OTP。
- 按 IAM 规则控制 RESTAlchemy 字段可见性。
- 从当前上下文访问 token、用户、项目和权限。
- 将 IAM 异常转换成一致的 HTTP 响应。

`gcl_iam` 不签发用户凭据、不定义业务角色，也不提供 IAM 数据库；这些由 IAM
服务或自定义驱动负责。

## 文档导航

1. [安装](installation.md)
2. [入门](getting-started.md)
3. 概念：
   - [认证与请求上下文](concepts/authentication-and-context.md)
   - [权限、项目与 OTP](concepts/authorization.md)
4. 指南：
   - [集成 RESTAlchemy 服务](how-to/restalchemy-service.md)
   - [实现自定义驱动](how-to/custom-driver.md)
5. [公共 API 参考](reference/api.md)

## 语言

四种语言的文件和章节结构完全一致：

- [English](../en/index.md)
- [Русский](../ru/index.md)
- [Deutsch](../de/index.md)
- [中文](../zh/index.md)

## 支持环境

- Python 3.10+
- RESTAlchemy 15.x
- PyJWT 2.x
- HS256 或 RS256 JWT 签名

依赖版本范围以 `pyproject.toml` 为准。
