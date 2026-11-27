# TicketPro
### Internal Ticket Management System

A desktop-based ticket management application designed to help teams create, assign, prioritise, and track support tickets through their complete lifecycle.

TicketPro combines role-based access control, relational database management, threaded discussions, activity auditing, and an operational dashboard in a standalone Python desktop application.

**Built with:** Python · PyQt5 · SQLite  
**Version:** 1.0.0  
**Architecture:** Layered MVC

---

## Overview

TicketPro is an internal ticket management system developed to model the core workflows of a team-based support environment.

The application provides three distinct user roles, each with a defined set of permissions:

- **Admin:** Full system access, including ticket management and user administration.
- **Agent:** Ticket management, assignment, status updates, and collaboration.
- **User:** Creation and tracking of personal tickets, with commenting capabilities.

The application follows a layered Model-View-Controller (MVC) architecture, separating database operations, interface components, and application logic.

It operates locally using SQLite, without requiring a web server or external database service.

## Features

### 1. Ticket Lifecycle Management

Manage support tickets from creation through resolution.

- Create, edit, and delete tickets according to user permissions.
- Assign tickets to team members.
- Organise tickets by category and priority.
- Track ticket status through four stages:
  - Open
  - In Progress
  - Resolved
  - Closed
- Search tickets by title and description.
- Filter tickets independently by status and priority.

### 2. Role-Based Access Control

Three user roles provide differentiated access to application functionality.

| Capability | Admin | Agent | User |
|---|:---:|:---:|:---:|
| Create tickets | Yes | Yes | Yes |
| Edit tickets | Yes | Yes | Own tickets |
| Delete tickets | Yes | No | No |
| Assign tickets | Yes | Yes | No |
| Change ticket status | Yes | Yes | No |
| Add comments | Yes | Yes | Yes |
| Manage user accounts | Yes | No | No |

Permissions are reflected in the application interface, with restricted navigation elements and actions excluded for unauthorised roles.

### 3. Comments & Activity Audit Trail

Each ticket supports collaborative discussions and an associated activity history.

- Add comments to tickets.
- Display comment authors and timestamps.
- Automatically record ticket creation, updates, comments, and deletion events.
- Maintain a chronological activity history.
- Associate activity records with the corresponding user and ticket.

Activity logging is integrated into database transactions so that the recorded operation and its audit entry are committed together.

### 4. Operational Dashboard

A central dashboard provides an overview of ticket activity.

**Statistics include:**
- Total tickets
- Open tickets
- In-progress tickets
- Resolved tickets
- Closed tickets
- Critical-priority tickets

**Activity feed:**

Displays the latest 30 recorded events across tickets, ordered from newest to oldest.

The dashboard also retrieves per-agent assignment statistics for operational visibility.

### 5. User Management

An administrative interface for managing application accounts.

- View registered users.
- Create new user accounts.
- Assign or change user roles.
- Delete user accounts.
- Prevent administrators from changing their own role or deleting their own account.

### 6. Desktop Interface

A custom dark-slate interface built with PyQt5 and Qt Style Sheets (QSS).

- Sidebar-based navigation.
- Dedicated dashboard, ticket, and user management views.
- Colour-coded ticket statuses and priorities.
- Customised tables, dialogs, buttons, and statistic cards.
- Centralised styling and colour definitions.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core application development |
| PyQt5 | Desktop interface and event-driven interaction |
| SQLite | Relational database |
| sqlite3 | Database connectivity and SQL operations |
| Qt Style Sheets | Interface styling and theming |

The application uses Python's built-in SQLite interface, so no separate database server or ORM is required.

## Architecture

TicketPro follows a layered MVC architecture adapted for desktop application development.

| Layer | Implementation | Responsibility |
|---|---|---|
| Model | `db/database.py` | Database schema, queries, CRUD operations, business rules, and activity logging |
| View | `ui/*.py` | Interface components, data presentation, and user input |
| Controller | Signal handlers in `ui/*.py` | Event handling, model interaction, and view updates |
| Styling | `ui/styles.py` | Centralised visual theme and QSS stylesheet |
| Entry Point | `main.py` | Application initialisation, database setup, and authentication flow |

### Application Data Flow

The application uses a unidirectional interaction flow:

`User Action → View Event → Controller Handler → Model → Database → View Refresh`

For example, creating a ticket involves opening the ticket dialog, submitting the form, invoking the database operation, and refreshing the ticket list with the updated data.

### Database Design

The SQLite database uses a normalised four-table structure with foreign key relationships.

| Table | Responsibility |
|---|---|
| `users` | User accounts, roles, and credentials |
| `tickets` | Ticket details, status, priority, creator, and assignee |
| `comments` | Ticket-specific discussions and authorship |
| `activity_log` | Chronological record of ticket-related events |

Foreign key enforcement maintains relational integrity, while cascading deletion handles dependent ticket comments.

### Project Structure

```text
ticketpro/
│
├── main.py
├── requirements.txt
├── ticketpro.db
│
├── db/
│   ├── __init__.py
│   └── database.py
│
└── ui/
    ├── __init__.py
    ├── styles.py
    ├── login.py
    ├── main_window.py
    ├── dashboard.py
    ├── tickets.py
    └── users.py
```

**Key implementation responsibilities:**

- `main.py` — Application entry point and initialisation.
- `db/database.py` — Centralised database operations and business logic.
- `ui/login.py` — Authentication interface.
- `ui/main_window.py` — Main application shell and navigation.
- `ui/dashboard.py` — Statistics and activity feed.
- `ui/tickets.py` — Ticket listing, creation, editing, and details.
- `ui/users.py` — Administrative user management.
- `ui/styles.py` — Global theme and interface styling.

---

## Installation & Setup

### Prerequisites

- Python 3.9 or newer
- pip

### 1. Clone the repository

```bash
git clone https://github.com/pylhr/pythonticketpro.git
```

### 2. Navigate to the project directory

```bash
cd pythonticketpro
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
python main.py
```

The application initialises the SQLite database and loads demonstration data on first setup.

No additional database server or configuration is required.

---

## Demo Credentials

The application includes three demonstration accounts for exploring its role-based functionality.

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin |
| `agent1` | `agent123` | Agent |
| `user1` | `user123` | User |

These accounts are intended for demonstration purposes only. Do not use the default credentials or demonstration configuration for real deployments.

---

## Engineering Practices

Several software engineering principles were incorporated into the implementation.

**Separation of Concerns**

Database operations, interface components, and styling are maintained in separate modules.

**Single Responsibility Principle**

Individual modules and classes handle specific application responsibilities.

**DRY (Don't Repeat Yourself)**

Shared styling definitions, colour mappings, and activity logging logic reduce duplication.

**Parameterized SQL Queries**

Database queries use parameterized statements to prevent user input from being interpreted as executable SQL.

**Transactional Activity Logging**

Activity records are written through the same database connection and transaction as their associated operations.

**Event-Driven Programming**

PyQt5 signals and slots facilitate communication between interface components without tightly coupling navigation and authentication logic.

**Defensive Programming**

Input validation, administrative safeguards, and permission-aware interface construction help prevent invalid or unauthorised operations.

**Idempotent Database Initialisation**

Database initialisation uses `CREATE TABLE IF NOT EXISTS`, allowing the setup routine to be executed repeatedly without recreating existing tables.

---

## Current Scope & Future Development

TicketPro v1.0 implements the core functionality of an internal ticket management system. Several improvements have been identified for future iterations.

| Area | Potential Improvement |
|---|---|
| Authentication | Salted password hashing using Argon2 or bcrypt |
| Session Management | Automatic session timeout |
| Database | PostgreSQL integration for concurrent multi-user deployments |
| Database Management | Version-controlled schema migrations |
| Dashboard | Visual analytics and ticket trend charts |
| Performance | Ticket pagination |
| Collaboration | File attachments and email notifications |
| Workflow | Due dates and SLA tracking |
| Reporting | CSV and PDF exports |
| Testing | Automated unit and integration tests |
| Distribution | Standalone application packaging |

These are proposed improvements, not features currently implemented in v1.0.

## Testing

The initial version was evaluated through manual testing across all three user roles.

Testing covered:

- Authentication and credential validation.
- Ticket creation, editing, status changes, and deletion.
- Role-based permission restrictions.
- Comment submission and activity history.
- Search and filter combinations.
- User management safeguards.
- Edge cases involving unassigned tickets and user deletion.

Automated test coverage and continuous integration are not currently included.

## Project Information

**Project:** TicketPro  
**Version:** 1.0.0  
**Type:** Software Engineering / Portfolio Project  
**Platform:** Cross-platform Python desktop application  
**Repository:** [github.com/pylhr/pythonticketpro](https://github.com/pylhr/pythonticketpro)

---

*TicketPro — An exploration of structured desktop application development, relational data management, access control, and software engineering principles.*