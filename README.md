# Lariba Cloud API Specification

Public API specifications, schemas, and developer contracts for **Lariba Cloud**.

Lariba Cloud is an operational control plane for governed coordination across cloud and local systems. This repository publishes the developer-facing API contract without exposing Lariba Cloud's private production implementation, operational infrastructure, security-sensitive systems, or proprietary automation.

## OpenAPI contract

The current API contract is published in:

```text
openapi.json
```

The document uses **OpenAPI 3.1** and can be consumed by tools such as Swagger UI, Postman, API documentation generators, validation tooling, and compatible SDK generators.

Developers can use this contract to understand supported public endpoints, authentication requirements, request and response schemas, and integration boundaries.

## Usage

Clone the repository:

```bash
git clone https://github.com/node63labs/lariba-spec.git
cd lariba-spec
```

You can then load `openapi.json` into any OpenAPI 3.1-compatible tooling.

Example with a local Swagger UI or API client:

```text
openapi.json
```

The specification is intended to describe the public contract. It does not grant access to Lariba Cloud private repositories, internal infrastructure, deployment configuration, secrets, or implementation details.

## Public developer resources

- [Lariba Cloud JavaScript/TypeScript SDK](https://github.com/node63labs/lariba-sdk-js)
- [Lariba Cloud developer documentation](https://github.com/node63labs/lariba-docs-site)
- [NODE63 Labs](https://github.com/node63labs)

## Repository boundary

This repository is part of the public NODE63 Labs developer surface.

Public material may include API specifications, schemas, developer contracts, SDK integration guidance, and selected examples. Production applications, control-plane internals, operational infrastructure, security-sensitive implementation, and proprietary automation are maintained outside this public repository.

## Versioning

API compatibility is governed by the versioned public contract. Breaking API changes should be represented through an explicit version transition rather than silently changing an existing contract.

Consumers should treat `openapi.json` on the default branch as the current published contract unless a release or versioned artifact states otherwise.

## Security

Do not report credentials, API keys, secrets, or suspected vulnerabilities in public issues. Follow the security-reporting guidance published by NODE63 Labs or the relevant Lariba Cloud developer resource.

## License

Licensed under the [Apache License 2.0](./LICENSE).

Copyright © 2026 NODE63 Labs.
