# Smart Links

A lightweight URL-shortening and link-management service built with **Flask, PostgreSQL, and Redis**.

The project started as a simple URL shortener and was designed as a small **0-to-1 product exercise**: turning a common technical primitive into a usable product with clear user flows, measurable outcomes, and deliberate engineering trade-offs.

## Product Overview

Long URLs are difficult to share, remember, and use across channels such as social media, email, QR codes, and marketing campaigns.

**Smart Links** allows users to:

- Create compact short URLs from long URLs
- Redirect users to the original destination
- Track link usage
- Retrieve frequently accessed links quickly through Redis
- Generate compact, deterministic short codes using Base62 encoding

### Example

```text
Long URL
https://example.com/products/category/summer-sale?campaign=2026&utm_source=instagram

                ↓

Short URL
https://sho.rt/00021
```
When a user visits the short URL, the application decodes the short code, retrieves the corresponding URL, and redirects the user to the original destination.

## Why This Project?

This project was designed as a PM + engineering portfolio project, with emphasis on:

- Problem definition
- MVP scoping
- Product requirements
- User workflows
- Product metrics
- Technical trade-offs
- Performance considerations
- End-to-end execution

Rather than building every possible URL-shortening feature, the project focuses on creating a small, reliable core product and establishing a foundation for future capabilities such as analytics, custom domains, QR codes, and team collaboration.

## Core Product Flow
```
User enters long URL
        │
        ▼
Flask API
        │
        ▼
PostgreSQL creates unique ID
        │
        ▼
ID encoded using Base62
        │
        ▼
Short URL generated
        │
        ▼
User shares short URL
        │
        ▼
Flask receives redirect request
        │
        ▼
Redis lookup
   ┌────┴────┐
   │         │
 Cache HIT  Cache MISS
   │         │
   │         ▼
   │     PostgreSQL
   │         │
   │         ▼
   │        Redis
   │         │
   └────┬────┘
        ▼
   Original URL
        │
        ▼
     Redirect
```

## Tech Stack

| Layer            | Technology | Purpose                                      |
| ---------------- | ---------- | -------------------------------------------- |
| Backend          | Flask      | REST API and application logic               |
| Database         | PostgreSQL | Persistent storage and source of truth       |
| Cache            | Redis      | Fast lookups for frequently accessed links   |
| Encoding         | Base62     | Compact short-code generation                |
| Language         | Python     | Application development                      |
| Containerization | Docker     | Local development and deployment consistency |

