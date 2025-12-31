# Backend Architecture — Legal Tech ERP (MVP)

## 1. Purpose

This backend powers a **multi-tenant legal ERP system** for:

* Law firms
* Solo lawyers

It ensures:

* Data isolation between firms
* Secure authentication
* Role-based access control (RBAC)

---

## 2. Core Principles

* **Multi-tenant by design**
* **Security first**
* **Simple, scalable MVP**
* **No direct permission assignment to users**

---

## 3. Tech Stack (MVP)

* **Backend Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Auth:** JWT (Access + Refresh tokens)
* **RBAC:** Role → Permission model
* **Migrations:** Alembic

---

## 4. Multi-Tenancy Model

* Each law firm or solo lawyer is an **Organization**
* Every user belongs to **exactly one organization**
* All queries are scoped by `organization_id`

This prevents cross-firm data access.

---

## 5. Authentication Flow

1. User logs in with email + password
2. Credentials are verified
3. JWT token is issued
4. Token contains:

   * `user_id`
   * `organization_id`

Tokens identify **who** the user is and **which firm** they belong to.

---

## 6. Authorization (RBAC)

### Entities

* Users
* Roles (organization-scoped)
* Permissions (global)

### Rule

```
User → Role → Permissions
```

Users **never** receive permissions directly.

---

## 7. Permission Checking

* Each API route declares required permission(s)
* On request:

  1. User is identified via JWT
  2. User roles are loaded
  3. Role permissions are resolved
  4. Access is allowed or denied

Only `permission.code` is used for checks.

---

## 8. Database Design (Core Tables)

* organizations
* users
* roles
* permissions
* user_roles
* role_permissions


![ER Diagram](er_diagram.png)

This supports secure multi-tenancy and flexible RBAC.

---

## 9. API Structure

```
/auth
  - /login
  - /refresh

/organizations
  - create
  - update

/users
  - create
  - list
  - deactivate

/roles
  - create
  - assign permissions

/cases (future)
  - create
  - view
  - update
```

---

## 10. Security Rules

* All endpoints require authentication (except login)
* Organization data is always scoped
* Inactive users and organizations are blocked
* Permission codes are immutable (seeded)

---

## 11. MVP Limitations (Intentional)

* No permission UI
* No role hierarchy
* No cross-organization users
* No attribute-based access (ABAC)

These can be added later without schema changes.

---

## 12. Scalability Path

Future upgrades:

* Case-level permissions
* Audit logs
* Admin dashboards
* Mobile app support

Core architecture remains unchanged.

---

## 13. Summary

This backend:

* Is simple
* Is secure
* Supports real legal workflows
* Scales without redesign

**MVP-ready. Production-safe.**
