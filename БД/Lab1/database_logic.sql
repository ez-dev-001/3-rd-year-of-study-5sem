-- This script creates Triggers, Functions, Stored Procedures,
-- Views, and Indexes.
-- It satisfies requirements 5 (10+ objects) and 6 (2+ index types).

---
--- OBJECT SET 1: TRIGGERS AND FUNCTIONS (Total: 1 Func + 5 Triggers = 6 objects)
--- Automates the `updated_at` field for audit.
---

-- 1. (Function) A generic trigger function to update the `updated_at` timestamp.
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. (Trigger) for Users
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON Users
FOR EACH ROW
EXECUTE FUNCTION fn_set_updated_at();

-- 3. (Trigger) for Projects
CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON Projects
FOR EACH ROW
EXECUTE FUNCTION fn_set_updated_at();

-- 4. (Trigger) for Tasks
CREATE TRIGGER trg_tasks_updated_at
BEFORE UPDATE ON Tasks
FOR EACH ROW
EXECUTE FUNCTION fn_set_updated_at();

-- 5. (Trigger) for Comments
CREATE TRIGGER trg_comments_updated_at
BEFORE UPDATE ON Comments
FOR EACH ROW
EXECUTE FUNCTION fn_set_updated_at();

-- 6. (Trigger) for Milestones
CREATE TRIGGER trg_milestones_updated_at
BEFORE UPDATE ON Milestones
FOR EACH ROW
EXECUTE FUNCTION fn_set_updated_at();


---
--- OBJECT SET 2: VIEWS (Total: 3 objects)
--- Provides read-only access, automatically filtering for soft-deleted records.
---

-- 7. (View) v_active_users
-- Shows all users that are not soft-deleted.
CREATE VIEW v_active_users AS
SELECT
    user_id,
    first_name,
    last_name,
    email,
    department_id,
    created_at,
    updated_at
FROM Users
WHERE is_deleted = FALSE;

-- 8. (View) v_active_projects
-- Shows all projects that are not soft-deleted.
CREATE VIEW v_active_projects AS
SELECT
    p.project_id,
    p.name,
    p.description,
    p.client_id,
    c.client_name,
    p.project_manager_id,
    u.first_name AS manager_first_name,
    u.last_name AS manager_last_name,
    p.start_date,
    p.end_date,
    p.status
FROM Projects p
LEFT JOIN Clients c ON p.client_id = c.client_id
LEFT JOIN v_active_users u ON p.project_manager_id = u.user_id
WHERE p.is_deleted = FALSE;

-- 9. (View) v_project_task_details
-- A comprehensive view of active tasks with their project, status, and priority.
CREATE VIEW v_project_task_details AS
SELECT
    t.task_id,
    t.name AS task_name,
    t.description AS task_description,
    t.due_date,
    t.estimated_hours,
    p.project_id,
    p.name AS project_name,
    ts.status_name AS task_status,
    tp.priority_name AS task_priority,
    t.created_at,
    t.updated_at
FROM Tasks t
JOIN v_active_projects p ON t.project_id = p.project_id
JOIN TaskStatus ts ON t.status_id = ts.status_id
LEFT JOIN TaskPriority tp ON t.priority_id = tp.priority_id
WHERE t.is_deleted = FALSE;


---
--- OBJECT SET 3: STORED PROCEDURES (Total: 4 objects)
--- Encapsulates CUD logic, especially for soft-delete and audit fields.
---

-- 10. (Procedure) sp_create_project
-- Creates a new project and correctly sets audit fields.
CREATE OR REPLACE PROCEDURE sp_create_project(
    IN p_name VARCHAR(255),
    IN p_description TEXT,
    IN p_client_id INT,
    IN p_project_manager_id UUID,
    IN p_start_date DATE,
    IN p_end_date DATE,
    IN p_creator_user_id UUID,
    OUT p_project_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Projects (
        project_id, name, description, client_id, project_manager_id,
        start_date, end_date, status,
        created_by_user_id, updated_by_user_id
    )
    VALUES (
        uuid_generate_v4(), p_name, p_description, p_client_id, p_project_manager_id,
        p_start_date, p_end_date, 'Pending',
        p_creator_user_id, p_creator_user_id
    )
    RETURNING project_id INTO p_project_id;
END;
$$;

-- 11. (Procedure) sp_soft_delete_project
-- Performs a soft delete on a project.
CREATE OR REPLACE PROCEDURE sp_soft_delete_project(
    IN p_project_id UUID,
    IN p_user_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE Projects
    SET
        is_deleted = TRUE,
        status = 'Archived',
        updated_by_user_id = p_user_id
        -- updated_at is handled by the trigger
    WHERE project_id = p_project_id;
END;
$$;

-- 12. (Procedure) sp_update_task_status
-- Updates a task's status and the audit fields.
CREATE OR REPLACE PROCEDURE sp_update_task_status(
    IN p_task_id UUID,
    IN p_status_id INT,
    IN p_user_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE Tasks
    SET
        status_id = p_status_id,
        updated_by_user_id = p_user_id
        -- updated_at is handled by the trigger
    WHERE task_id = p_task_id;
END;
$$;

-- 13. (Procedure) sp_archive_project_and_tasks
-- A transactional procedure to soft-delete a project AND all its child tasks.
CREATE OR REPLACE PROCEDURE sp_archive_project_and_tasks(
    IN p_project_id UUID,
    IN p_user_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_archived_status_id INT;
BEGIN
    -- Get the ID for 'Archived' status
    SELECT status_id INTO v_archived_status_id
    FROM TaskStatus
    WHERE status_name = 'Archived'
    LIMIT 1;

    -- Soft-delete all tasks associated with the project
    UPDATE Tasks
    SET
        is_deleted = TRUE,
        status_id = v_archived_status_id,
        updated_by_user_id = p_user_id
    WHERE project_id = p_project_id AND is_deleted = FALSE;

    -- Soft-delete the project itself
    UPDATE Projects
    SET
        is_deleted = TRUE,
        status = 'Archived',
        updated_by_user_id = p_user_id
    WHERE project_id = p_project_id;
END;
$$;

---
--- OBJECT SET 4: USER-DEFINED FUNCTION (Total: 1 object)
---

-- 14. (Function) fn_get_user_active_task_count
-- Returns the count of active (not deleted, not done) tasks for a user.
CREATE OR REPLACE FUNCTION fn_get_user_active_task_count(p_user_id UUID)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    task_count INT;
BEGIN
    SELECT COUNT(t.task_id)
    INTO task_count
    FROM Tasks t
    JOIN TaskAssignments ta ON t.task_id = ta.task_id
    JOIN TaskStatus ts ON t.status_id = ts.status_id
    WHERE ta.user_id = p_user_id
      AND t.is_deleted = FALSE
      AND ts.status_name NOT IN ('Done', 'Archived');
      
    RETURN task_count;
END;
$$;


---
--- INDEXES (Requirement 6)
---

-- 1. B-Tree Index (Standard)
-- For fast lookups on foreign keys.
CREATE INDEX idx_tasks_project_id ON Tasks (project_id);
CREATE INDEX idx_taskassignments_user_id ON TaskAssignments (user_id);
CREATE INDEX idx_timeentries_user_task ON TimeEntries (user_id, task_id);

-- 2. Unique B-Tree Index
-- Used for the Users.email, but we add another for project names.
-- (Note: Users.email already has a unique index from the CREATE TABLE statement)
CREATE UNIQUE INDEX idx_projects_name_unique_active
ON Projects (name)
WHERE is_deleted = FALSE;

-- 3. Partial Index
-- Speeds up queries that only look for active records.
CREATE INDEX idx_tasks_active
ON Tasks (task_id)
WHERE is_deleted = FALSE;

CREATE INDEX idx_projects_active_manager
ON Projects (project_manager_id)
WHERE is_deleted = FALSE;

-- 4. GIN Index (Full-Text Search)
-- Allows for fast full-text search on task names and descriptions.
CREATE INDEX idx_tasks_fts
ON Tasks
USING GIN (to_tsvector('english', name || ' ' || description));

-- Example FTS Query:
-- SELECT task_id, name FROM Tasks
-- WHERE to_tsvector('english', name || ' ' || description) @@ to_tsquery('english', 'database & performance');