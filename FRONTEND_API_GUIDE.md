# Frontend API Guide: `/users/me`

This document serves as the reference for using the `/users/me` endpoint to bootstrap the user session, handle routing, and manage permissions on the frontend.

## 1. Overview

The `GET /api/v1/users/me` endpoint is the **Identity Provider** for the frontend application. It aggregates data from multiple database tables (`users`, `organizations`, `roles`) into a single, flattened JSON object that describes the current user's context.

**When to call this:**
*   On application load (in `layout.tsx` or a dedicated auth provider).
*   After a successful login.
*   When a user switches organizations (future feature).

## 2. Response Schema

```json
{
  "id": 101,
  "user_name": "Harvey Specter",
  "user_email": "harvey@pearson.com",
  
  // Organization Context
  "org_id": 50,
  "org_name": "Pearson Specter Litt",
  "org_type": "FIRM",
  
  // Role & Permission Context
  "primary_profession": "LAWYER",
  "user_roles": [
    "FIRM_ADMIN",
    "FIRM_LAWYER"
  ]
}
```

## 3. Field Reference & Database Mapping

Here is what each field represents and where it comes from in the backend.

### User Identity
| Field | Type | Description | DB Source |
| :--- | :--- | :--- | :--- |
| `id` | `number` | The unique primary key of the user. | `users.id` |
| `user_name` | `string` | The display name of the user. | `users.name` |
| `user_email` | `string` | Unique email address. | `users.email` |

### Organization Context (The "Tenant")
*These fields are `null` if the user is a Freelancer (Tarik) with no active engagement.*

| Field | Type | Description | DB Source |
| :--- | :--- | :--- | :--- |
| `org_id` | `number` | **Crucial for Routing**. The ID of the current active organization. Use this in your dynamic routes (e.g., `/dashboard/[org_id]/...`). | `organizations.id` |
| `org_name` | `string` | Display name of the Firm or Solo Practice. | `organizations.name` |
| `org_type` | `string` | Determines **Which Dashboard** to load. <br>• `"FIRM"`: Load Firm Dashboard.<br>• `"SOLO"`: Load Solo Dashboard.<br>• `"NONE"` (or null): Load Freelancer Dashboard. | `organizations.org_type` |

### Role Configuration
| Field | Type | Description | DB Source |
| :--- | :--- | :--- | :--- |
| `primary_profession` | `string` | The user's global persona. Determines broad capabilities. <br>• `"LAWYER"`<br>• `"CLERK"` | `users.primary_profession` |
| `user_roles` | `string[]` | List of specific permission sets assigned to this user **within this specific organization**. Used for **Access Control** (showing/hiding buttons). | `roles.name` (via `member_roles`) |

## 4. Common Role Scenarios

### Scenario A: The Firm Administrator
This user manages the firm but also practices law.
*   `org_type`: `"FIRM"`
*   `user_roles`: `["FIRM_ADMIN", "FIRM_LAWYER"]`
*   **Routing**: Redirect to `/dashboard/[org_id]/admin`.
*   **UI**: Show "Switch to Lawyer View" button because both roles are present.

### Scenario B: The Solo Practitioner
This user owns their own small practice.
*   `org_type`: `"SOLO"`
*   `user_roles`: `["SOLO_LAWYER"]`
*   **Routing**: Redirect to `/dashboard/[org_id]/lawyer`.

### Scenario C: The Freelance Clerk ("Tarik")
This user is signed up but not employed by any specific firm yet.
*   `org_type`: `null` (or "NONE")
*   `org_id`: `null`
*   `user_roles`: `[]`
*   **Routing**: Redirect to `/dashboard/[user_id]` (Use their own User ID as the context).
