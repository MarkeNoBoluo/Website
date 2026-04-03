# Blog Admin Dashboard Design Document

## 1. Overview

This document describes the design of the admin dashboard for the personal blog website. The dashboard provides a unified interface for managing all data (Articles, Todos, Users) with a consistent, modern UI.

### Key Requirements
- Manage all data types: Articles, Todos, Users
- Unified dashboard with statistics overview
- Enhanced search functionality (title + content for articles)
- Clean, modern UI style (white/light background)

---

## 2. Layout Design

### 2.1 Top Navigation Bar
- **Logo**: Left side
- **Breadcrumbs**: Center (shows current location: e.g., "Dashboard > Articles")
- **User Info**: Right side (username, avatar placeholder)
- **Logout Button**: Right side

### 2.2 Left Sidebar
- Fixed left sidebar with navigation links
- **Navigation Items**:
  - Dashboard (icon: grid/home)
  - Articles (icon: document)
  - Todos (icon: checkbox)
  - Users (icon: user)
- **Active State**: Highlight current section
- **Collapsed Mode**: Optional collapse for smaller screens

### 2.3 Main Content Area
- Shows content based on selected section
- Responsive design (adapts to screen size)

---

## 3. Page Designs

### 3.1 Dashboard Page (`/admin`)

#### Statistics Cards (4 cards)
1. **Total Articles**: Count + trend indicator
2. **Total Todos**: Count + trend indicator
3. **Total Users**: Count + trend indicator
4. **Article Publish Rate**: Published/Total percentage

#### Recent Activity (2-column layout)
- **Left Column**: Last 5 pending articles (title, status, time, actions)
- **Right Column**: Last 5 todos (title, quadrant, priority, actions)

---

### 3.2 Articles Management (`/admin/articles`)

#### Toolbar
- **Search**: Advanced search (title + content, exact/fuzzy match)
- **Status Filter**: All/Published/Draft
- **Sort**: By time/title/status
- **Bulk Actions**: Select all, bulk publish, bulk delete

#### Articles Table
| Column | Description |
|--------|-------------|
| Checkbox | For bulk operations |
| Title | Article title (link to edit) |
| Status | Draft/Published badge |
| Created | Creation timestamp |
| Updated | Last update timestamp |
| Actions | Edit, Delete, Publish/Unpublish, Preview |

#### Create/Edit Page
- **Title**: Text input
- **Content**: Markdown editor with live preview
- **Status**: Draft/Published selector
- **Actions**: Save, Cancel, Preview

---

### 3.3 Todos Management (`/admin/todos`)

#### Toolbar
- **Search**: Search todo title
- **Quadrant Filter**: All/1/2/3/4
- **Priority Filter**: All/1-5
- **Sort**: By priority/quadrant/creation time

#### Todos Table
| Column | Description |
|--------|-------------|
| Checkbox | For bulk operations |
| Title | Todo title (link to edit) |
| Quadrant | 1/2/3/4 badge |
| Priority | 1-5 level |
| Due Date | Deadline (if set) |
| Status | Completed/Pending |
| Actions | Edit, Delete, Mark Complete, Move Quadrant |

#### Create/Edit Page
- **Title**: Text input
- **Description**: Textarea
- **Quadrant**: Dropdown (1-4)
- **Priority**: Dropdown (1-5)
- **Due Date**: Date picker
- **Completed**: Checkbox
- **Actions**: Save, Cancel

---

### 3.4 Users Management (`/admin/users`)

#### Toolbar
- **Search**: Search username
- **Sort**: By username/registration time

#### Users Table
| Column | Description |
|--------|-------------|
| ID | User ID |
| Username | Username |
| Created | Registration time |
| Updated | Last update time |
| Actions | Edit, Delete, Change Password |

#### Create/Edit Page
- **Username**: Text input (unique)
- **Password**: Password input (required for create, optional for edit)
- **Confirm Password**: Password confirmation
- **Actions**: Save, Cancel

#### Change Password Page
- **Current Password**: Password input (for verification)
- **New Password**: Password input
- **Confirm New Password**: Password confirmation
- **Actions**: Save, Cancel

---

## 4. UI Style

### Color Scheme
- **Background**: #ffffff (white)
- **Sidebar**: #f8f9fa (light gray)
- **Primary**: #007bff (blue)
- **Success**: #28a745 (green)
- **Warning**: #ffc107 (yellow)
- **Danger**: #dc3545 (red)
- **Text**: #212529 (dark gray)

### Typography
- **Font**: system-ui, -apple-system, "Segoe UI", Roboto
- **Headings**: Bold, 1.5rem-2rem
- **Body**: Regular, 1rem

### Components
- **Buttons**: Rounded corners, hover states, primary/secondary variants
- **Tables**: Striped rows, hover effect, sortable headers
- **Cards**: Shadow, rounded corners, padding
- **Forms**: Consistent input styles, validation feedback
- **Badges**: Status indicators (draft/published, priority levels)

---

## 5. Routes and Endpoints

### Dashboard
- `GET /admin` - Dashboard page

### Articles
- `GET /admin/articles` - List articles (with search/filter/sort/pagination)
- `GET /admin/articles/new` - Create article form
- `POST /admin/articles/new` - Create article
- `GET /admin/articles/<id>/edit` - Edit article form
- `POST /admin/articles/<id>/edit` - Update article
- `POST /admin/articles/<id>/delete` - Delete article
- `POST /admin/articles/<id>/publish` - Publish article
- `POST /admin/articles/<id>/unpublish` - Unpublish article
- `POST /admin/articles/bulk` - Bulk operations

### Todos
- `GET /admin/todos` - List todos (with search/filter/sort/pagination)
- `GET /admin/todos/new` - Create todo form
- `POST /admin/todos/new` - Create todo
- `GET /admin/todos/<id>/edit` - Edit todo form
- `POST /admin/todos/<id>/edit` - Update todo
- `POST /admin/todos/<id>/delete` - Delete todo
- `POST /admin/todos/<id>/complete` - Mark complete
- `POST /admin/todos/<id>/move` - Move to quadrant
- `POST /admin/todos/bulk` - Bulk operations

### Users
- `GET /admin/users` - List users (with search/sort/pagination)
- `GET /admin/users/new` - Create user form
- `POST /admin/users/new` - Create user
- `GET /admin/users/<id>/edit` - Edit user form
- `POST /admin/users/<id>/edit` - Update user
- `POST /admin/users/<id>/delete` - Delete user
- `GET /admin/users/<id>/password` - Change password form
- `POST /admin/users/<id>/password` - Change password

---

## 6. File Structure

```
app/
├── admin/
│   ├── __init__.py              # Blueprint registration
│   ├── routes.py                # Article routes (existing, enhance)
│   ├── utils.py                 # Utility functions
│   ├── todo_admin.py            # Todo admin routes (new)
│   ├── user_admin.py            # User admin routes (new)
│   └── templates/
│       └── admin/
│           ├── base.html        # Base admin layout
│           ├── dashboard.html   # Dashboard page
│           ├── articles/
│           │   ├── list.html    # Articles list
│           │   ├── create.html  # Create article
│           │   └── edit.html    # Edit article
│           ├── todos/
│           │   ├── list.html    # Todos list
│           │   ├── create.html  # Create todo
│           │   └── edit.html    # Edit todo
│           └── users/
│               ├── list.html    # Users list
│               ├── create.html  # Create user
│               ├── edit.html    # Edit user
│               └── password.html # Change password
└── static/
    └── css/
        └── admin-modern.css     # Modern admin styles
```

---

## 7. Implementation Notes

### Search Functionality
- **Articles**: Search title + content (full-text)
- **Todos**: Search title only
- **Users**: Search username only
- **Implementation**: Use SQLAlchemy `contains()` or `like()` for search

### Pagination
- **Default**: 10 items per page
- **Controls**: Previous/Next, page numbers, items per page selector
- **Implementation**: Use SQLAlchemy `paginate()`

### Bulk Operations
- **Articles**: Bulk publish, bulk delete
- **Todos**: Bulk complete, bulk delete, bulk move
- **Users**: Bulk delete (optional)
- **Implementation**: Process multiple IDs in single request

### Security
- All routes require `@login_required`
- All mutating routes require `@csrf_protected`
- User can only manage their own todos (existing constraint)
- Users can only manage themselves (no multi-user management yet)

---

## 8. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Modern clean UI (white/light) | User preference, easier on eyes |
| Sidebar navigation | Standard admin pattern, easy to navigate |
| Breadcrumbs | Clear location tracking |
| Advanced search for articles | User request for title + content search |
| Separate routes for each module | Better code organization |
| Reuse existing admin blueprint | Minimize code changes |

---

_Document created: 2026-03-23_
_Version: 1.0_
_Author: Claude (brainstorming skill)_
