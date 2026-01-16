# Legal Tech Backend Architecture Guide

This guide provides a comprehensive overview of the backend system for the Legal Tech project. It is written for developers to understand the structural decisions, database schema, API interactions, and core logic that powers the system.

---

## 1. Tech Stack Overview

*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/), chosen for its high performance, automatic interactive API documentation (Swagger/OpenAPI), and native support for Python type hinting.
*   **Database**: PostgreSQL.
*   **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/), used for database modeling and query abstraction.
*   **Validation**: [Pydantic](https://docs.pydantic.dev/), used for data validation and settings management.
*   **Authentication**: JWT (JSON Web Tokens) with HttpOnly cookies for security.

---

## 2. Project Structure

The project follows a scalable modular structure:

*   **`app/main.py`**: The entry point. Initializes the FastAPI application, sets up CORS middleware, and mounts routers.
*   **`app/api/v1/`**: Contains all API route handlers, versioned.
*   **`app/core/`**: Core configuration (env vars, database connection, security logic).
*   **`app/models/`**: SQLAlchemy ORM models (Database Tables).
*   **`app/schemas/`**: Pydantic models (Data Validation for Requests/Responses).
*   **`create_tables.py`**: A utility script to initialize or reset the database schema.
*   **`run.py`**: The script to launch the application server using Uvicorn.

---

## 3. Database Schema & Models (`app/models/`)

The system uses a strictly relational schema designed for multi-tenancy and robust role-based access control (RBAC).

### Why these models exist:

#### 1. `Organization`
*   **Purpose**: Represents the "Tenant". This could be a large `FIRM` or a `SOLO` practice.
*   **Key Fields**:
    *   `org_type`: Either `"FIRM"` (partnerships, associates) or `"SOLO"` (single lawyer owner).
    *   `name`: The legal name of the entity.

#### 2. `User`
*   **Purpose**: Represents an individual human logging into the system.
*   **Key Fields**:
    *   `primary_profession`: Determines the global persona (`"LAWYER"` or `"CLERK"`).
    *   **NO Foreign Keys**: Notice that `User` does *not* have an `organization_id` column. Users are "free agents" until linked to an organization.

#### 3. `OrganizationMember` (The Linkage Table)
*   **Purpose**: Connects a `User` to an `Organization`. This allows a user (especially clerks/contractors) to potentially belong to multiple organizations in the future, or just one.
*   **Key Fields**:
    *   `is_exclusive`: If `True`, this user belongs *only* to this org (typical for Firm Partners). If `False`, they can join others (Freelancers).
    *   `status`: Tracks lifecycle (`active`, `invited`, `left`).

#### 4. `Role`
*   **Purpose**: Defines a job title scoped to a specific Organization (e.g., "Senior Partner" at Firm A, "Contractor" at Firm B).
*   **Scope**: Linked to `Organization`. A role named "Admin" in Org A is different from "Admin" in Org B.

#### 5. `MemberRole` (The Assignment Table)
*   **Purpose**: Assigns a `Role` to a specific `OrganizationMember`.
*   **Why**: We link Roles to the *Membership*, not the User directly. This ensures that if a User belongs to two Orgs, their roles in Org A do not bleed into Org B.

#### 6. `Permission` & `RolePermission`
*   **Purpose**: Granular access control (e.g., `can_view_cases`, `can_edit_billing`). Permissions are linked to Roles.

---

## 4. Schemas (`app/schemas/`)

Schemas define the "Shape" of data moving In and Out of the API. They sanitize inputs and format outputs.

*   **`auth.py` (Registration)**:
    *   **`UserRegister`**: A "Smart Schema". It accepts flags (`law_firm`, `lawyer`, `tarik`) and conditionally requires fields. For example, if `law_firm=True`, it demands `law_firm_name` and `admin_name`. This allows one API endpoint to handle three drastically different signup flows.
*   **`user.py` (Response)**:
    *   **`UserMe`**: Defines what the frontend sees when it asks "Who am I?". It flattens the complex database relationships (User -> Membership -> Org/Roles) into a simple JSON object for the UI to consume.

---

## 5. API Endpoints (`app/api/`)

### Authentication (`/api/v1/auth`)

*   **`POST /register`**:
    *   **Logic**: This is the most complex function. It switches logic based on the user type:
        1.  **Law Firm**: Creates User + Creates Org (Firm) + Links User as Exclusive Member + Assigns `FIRM_ADMIN` & `FIRM_LAWYER` roles.
        2.  **Solo Lawyer**: Creates User + Creates Org (Solo) + Links User as Exclusive Member + Assigns `SOLO_LAWYER` role.
        3.  **Clerk (Tarik)**: Creates User only. No Org created. They exist as a "Free Agent" ready to be hired.
*   **`POST /login`**:
    *   **Logic**: Verifies credentials. **Crucially**, it looks up the user's active `OrganizationMember` record to place the `org_id` and `primary_profession` into the JWT Token.

### User Management (`/api/v1/users`)

*   **`GET /me`**:
    *   **Purpose**: The "Bootstrap" endpoint called by the frontend on every page load.
    *   **Work**: It queries the database to find the user's current context: "Which Org are they active in? What roles do they have *in that org*?".
    *   **Return**: Returns the `UserMe` schema, which dictates exactly which Dashboard the frontend redirects to.

---

## 6. Database Connection & Configuration

*   **`app/core/database.py`**:
    *   Establishes the connection pool to PostgreSQL using `psycopg2`.
    *   **Pool Settings**: Configured with `pool_pre_ping=True` to prevent SSL/Stale connection errors in production environments (like Render/Heroku).
*   **`app/core/config.py`**:
    *   Uses Pydantic's `BaseSettings` to read from `.env` files or environment variables. This ensures the app crashes early if a critical var (like `DATABASE_URL`) is missing, rather than failing silently later.

---

## 7. How It All Connects

1.  **Frontend** sends JSON to `/register`.
2.  **Pydantic** (`UserRegister`) validates the JSON structure.
3.  **FastAPI** passes valid data to the `register` function.
4.  **SQLAlchemy** converts this data into SQL `INSERT` statements for `users`, `organizations`, `organization_members`, and `member_roles` tables.
5.  **PostgreSQL** stores the data with transactional integrity (all or nothing).
6.  **Frontend** sends credentials to `/login`.
7.  **Backend** issues a JWT containing the User ID.
8.  **Frontend** asks `/users/me`.
9.  **Backend** joins the tables (User -> Member -> Role) to tell the frontend: "This is Jessica, she is the Admin of Pearson Specter Firm".
10. **Frontend** redirects Jessica to `/dashboard/firm/admin`.
