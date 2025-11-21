-- This script creates the tables for the Project Management System in PostgreSQL.
-- It satisfies requirements 2 (15+ entities) and 4 (PostgreSQL implementation).
-- It includes fields for requirement 3 (Soft Delete and Audit fields).

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Departments Table
CREATE TABLE Departments (
    department_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manager_id UUID -- Foreign key added later after Users table
);

-- 2. Users Table
CREATE TABLE Users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    department_id INT REFERENCES Departments(department_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by_user_id UUID REFERENCES Users(user_id), -- Self-reference
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Add the foreign key constraint for Departments.manager_id
ALTER TABLE Departments
ADD CONSTRAINT fk_department_manager
FOREIGN KEY (manager_id) REFERENCES Users(user_id);

-- 3. Roles Table
CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- 4. UserRoles (Junction Table)
CREATE TABLE UserRoles (
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES Roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 5. Clients Table
CREATE TABLE Clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    contact_email VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Projects Table
CREATE TABLE Projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client_id INT REFERENCES Clients(client_id),
    project_manager_id UUID REFERENCES Users(user_id),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_user_id UUID REFERENCES Users(user_id),
    updated_by_user_id UUID REFERENCES Users(user_id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 7. ProjectMembers (Junction Table)
CREATE TABLE ProjectMembers (
    project_member_id SERIAL PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    role_on_project VARCHAR(100),
    UNIQUE(project_id, user_id)
);

-- 8. Milestones Table
CREATE TABLE Milestones (
    milestone_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by_user_id UUID REFERENCES Users(user_id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 9. TaskStatus (Lookup Table)
CREATE TABLE TaskStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    sort_order INT
);

-- 10. TaskPriority (Lookup Table)
CREATE TABLE TaskPriority (
    priority_id SERIAL PRIMARY KEY,
    priority_name VARCHAR(50) NOT NULL UNIQUE
);

-- 11. Tags (Lookup Table)
CREATE TABLE Tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) NOT NULL UNIQUE,
    color_hex VARCHAR(7)
);

-- 12. Tasks Table
CREATE TABLE Tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,
    milestone_id UUID REFERENCES Milestones(milestone_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status_id INT NOT NULL REFERENCES TaskStatus(status_id),
    priority_id INT REFERENCES TaskPriority(priority_id),
    parent_task_id UUID REFERENCES Tasks(task_id), -- For sub-tasks
    due_date TIMESTAMPTZ,
    estimated_hours DECIMAL(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_user_id UUID REFERENCES Users(user_id),
    updated_by_user_id UUID REFERENCES Users(user_id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- 13. TaskAssignments (Junction Table)
CREATE TABLE TaskAssignments (
    task_assignment_id SERIAL PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES Tasks(task_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    UNIQUE(task_id, user_id)
);

-- 14. TaskTags (Junction Table)
CREATE TABLE TaskTags (
    task_id UUID NOT NULL REFERENCES Tasks(task_id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES Tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

-- 15. Comments Table
CREATE TABLE Comments (
    comment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES Tasks(task_id) ON DELETE CASCADE,
    project_id UUID REFERENCES Projects(project_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES Users(user_id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by_user_id UUID REFERENCES Users(user_id),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_comment_target CHECK (
        (task_id IS NOT NULL AND project_id IS NULL) OR
        (task_id IS NULL AND project_id IS NOT NULL)
    )
);

-- 16. TimeEntries Table
CREATE TABLE TimeEntries (
    time_entry_id SERIAL PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES Tasks(task_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES Users(user_id),
    entry_date DATE NOT NULL,
    hours_spent DECIMAL(5, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by_user_id UUID REFERENCES Users(user_id)
);

-- 17. Attachments Table
CREATE TABLE Attachments (
    attachment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES Tasks(task_id) ON DELETE CASCADE,
    project_id UUID REFERENCES Projects(project_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES Users(user_id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    file_type VARCHAR(100),
    file_size_bytes BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_attachment_target CHECK (
        (task_id IS NOT NULL AND project_id IS NULL) OR
        (task_id IS NULL AND project_id IS NOT NULL)
    )
);

-- Insert some basic lookup data
INSERT INTO TaskStatus (status_name, sort_order) VALUES
('To Do', 1),
('In Progress', 2),
('In Review', 3),
('Done', 4),
('Archived', 5);

INSERT INTO TaskPriority (priority_name) VALUES
('Low'),
('Medium'),
('High'),
('Critical');

INSERT INTO Roles (role_name) VALUES
('Admin'),
('Project Manager'),
('Team Member'),
('Read Only');