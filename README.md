# Lariba Cloud API Specification

This repository contains the **official OpenAPI specification** for the Lariba Cloud platform.

The specification defines the REST API used by developers to send events, manage projects, and interact with the Lariba Cloud platform.

---

# Overview

Lariba Cloud is a developer platform for collecting and analyzing application events.

The API allows developers to:

* Send application events
* Authenticate using API keys
* Manage projects and organizations
* Query analytics and usage data
* Integrate with the Lariba Cloud SDKs

The OpenAPI specification in this repository serves as the **single source of truth** for the Lariba Cloud API.

---

# Specification File

The API specification is defined in:

```id="9ddnt9"
openapi.json
```

This file follows the **OpenAPI 3.x specification** and can be used with:

* Swagger UI
* Postman
* OpenAPI generators
* SDK generation tools

---

# Example API Endpoint

Example event ingestion request:

```http id="x77ntd"
POST /v1/events
Authorization: Bearer LARIBA_API_KEY
Content-Type: application/json
```

Example payload:

```json id="5ynjru"
{
  "event": "user.signup",
  "properties": {
    "plan": "starter"
  }
}
```

---

# Usage

Developers typically interact with the API using one of the official SDKs.

Example using the JavaScript SDK:

```javascript id="5zh65g"
import { Lariba } from "@laribacloud/lariba-sdk-js"

const lariba = new Lariba({
  apiKey: process.env.LARIBA_API_KEY
})

await lariba.track("user.signup", {
  plan: "starter"
})
```

---

# Related Repositories

Lariba Cloud is composed of multiple repositories:

### Core Backend

https://github.com/node63labs/lariba-cloud

FastAPI backend that powers the Lariba Cloud platform.

### Developer Documentation

https://github.com/node63labs/lariba-docs-site

Public developer documentation and integration guides.

### JavaScript SDK

https://github.com/node63labs/lariba-sdk-js

Official JavaScript SDK for sending events to Lariba Cloud.

---

# Versioning

The API follows semantic versioning.

Example:

```id="tfeq74"
v1
v1.1
v2
```

Major versions indicate breaking changes to the API.

---

# License

MIT License © Lariba Cloud
