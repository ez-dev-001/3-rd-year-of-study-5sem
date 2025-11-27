-- Цей скрипт створює таблицю в MySQL для порівняння швидкодії з MongoDB.
-- Виконувати в базі даних `project_management`.

USE project_management;

DROP TABLE IF EXISTS project_logs_benchmark;

-- Створюємо таблицю, що імітує структуру логів
CREATE TABLE project_logs_benchmark (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    details_json TEXT, -- Зберігаємо деталі як JSON-рядок (аналог документа)
    created_at DATETIME DEFAULT NOW()
);

-- Додаємо індекс по project_id, щоб пошук (SELECT) був оптимізований
-- Це зробить змагання з MongoDB чесним, оскільки там ми теж додамо індекс.
CREATE INDEX idx_logs_project ON project_logs_benchmark(project_id);