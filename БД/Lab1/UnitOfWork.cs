using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;

// This example uses Dapper for data access, as it maps cleanly to
// Stored Procedures and Views as required by Task 7.

// --- 1. ENTITY MODELS (POCOs) ---
// These models map to our Views, not tables directly for reads.

public class ProjectView
{
    public Guid ProjectId { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public int? ClientId { get; set; }
    public string ClientName { get; set; }
    public Guid? ProjectManagerId { get; set; }
    public string ManagerFirstName { get; set; }
    public string ManagerLastName { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string Status { get; set; }
}

public class TaskDetailView
{
    public Guid TaskId { get; set; }
    public string TaskName { get; set; }
    public Guid ProjectId { get; set; }
    public string ProjectName { get; set; }
    public string TaskStatus { get; set; }
    public string TaskPriority { get; set; }
    public DateTime? DueDate { get; set; }
}

// Model for creating/updating
public class Project
{
    public Guid ProjectId { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public int? ClientId { get; set; }
    public Guid? ProjectManagerId { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
}


// --- 2. REPOSITORY INTERFACES ---

public interface IProjectRepository
{
    // Read operations use VIEWS
    Task<IEnumerable<ProjectView>> GetAllActiveProjectsAsync();
    Task<ProjectView> GetActiveProjectByIdAsync(Guid id);
    
    // Write operations use STORED PROCEDURES
    Task<Guid> CreateProjectAsync(Project project, Guid creatorUserId);
    Task SoftDeleteProjectAsync(Guid projectId, Guid currentUserId);
}

public interface ITaskRepository
{
    // Read operations use VIEWS
    Task<IEnumerable<TaskDetailView>> GetTasksForProjectAsync(Guid projectId);
    
    // Write operations use STORED PROCEDURES
    Task UpdateTaskStatusAsync(Guid taskId, int newStatusId, Guid currentUserId);
}

// --- 3. UNIT OF WORK INTERFACE ---

public interface IUnitOfWork : IDisposable
{
    IProjectRepository Projects { get; }
    ITaskRepository Tasks { get; }
    
    Task CompleteAsync(); // Commits the transaction
    // Rollback is handled by Dispose() if CompleteAsync() is not called
}

// --- 4. CONCRETE IMPLEMENTATIONS ---

public class NpgsqlUnitOfWork : IUnitOfWork
{
    private readonly IDbConnection _connection;
    private IDbTransaction _transaction;
    private bool _disposed;

    public IProjectRepository Projects { get; private set; }
    public ITaskRepository Tasks { get; private set; }

    public NpgsqlUnitOfWork(string connectionString)
    {
        _connection = new NpgsqlConnection(connectionString);
        _connection.Open();
        _transaction = _connection.BeginTransaction();

        // Pass the transaction to the repositories
        Projects = new ProjectRepository(_transaction);
        Tasks = new TaskRepository(_transaction);
    }

    public async Task CompleteAsync()
    {
        try
        {
            await _transaction.CommitAsync();
        }
        catch
        {
            await _transaction.RollbackAsync();
            throw;
        }
        finally
        {
            _transaction.Dispose();
            // Start a new transaction for subsequent work
            _transaction = await ((NpgsqlConnection)_connection).BeginTransactionAsync();
            
            // Re-assign transaction to repositories
            ((ProjectRepository)Projects).SetTransaction(_transaction);
            ((TaskRepository)Tasks).SetTransaction(_transaction);
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        
        if (disposing)
        {
            // If transaction is still active (i.e., CompleteAsync not called), roll it back
            _transaction?.Rollback();
            _transaction?.Dispose();
            _connection?.Dispose();
        }
        
        _disposed = true;
    }
}

public class ProjectRepository : IProjectRepository
{
    private IDbTransaction _transaction;
    private IDbConnection _connection => _transaction.Connection;

    public ProjectRepository(IDbTransaction transaction)
    {
        _transaction = transaction;
    }
    
    // Internal method to allow UoW to update the transaction
    public void SetTransaction(IDbTransaction transaction)
    {
        _transaction = transaction;
    }

    public async Task<Guid> CreateProjectAsync(Project project, Guid creatorUserId)
    {
        // CALLING STORED PROCEDURE FOR WRITE
        var parameters = new DynamicParameters();
        parameters.Add("p_name", project.Name);
        parameters.Add("p_description", project.Description);
        parameters.Add("p_client_id", project.ClientId);
        parameters.Add("p_project_manager_id", project.ProjectManagerId);
        parameters.Add("p_start_date", project.StartDate);
        parameters.Add("p_end_date", project.EndDate);
        parameters.Add("p_creator_user_id", creatorUserId);
        parameters.Add("p_project_id", dbType: DbType.Guid, direction: ParameterDirection.Output);

        await _connection.ExecuteAsync(
            "sp_create_project", 
            parameters, 
            transaction: _transaction, 
            commandType: CommandType.StoredProcedure
        );

        return parameters.Get<Guid>("p_project_id");
    }

    public async Task SoftDeleteProjectAsync(Guid projectId, Guid currentUserId)
    {
        // CALLING STORED PROCEDURE FOR WRITE (soft delete)
        await _connection.ExecuteAsync(
            "sp_soft_delete_project",
            new { p_project_id = projectId, p_user_id = currentUserId },
            transaction: _transaction,
            commandType: CommandType.StoredProcedure
        );
    }

    public async Task<IEnumerable<ProjectView>> GetAllActiveProjectsAsync()
    {
        // READING FROM VIEW
        var sql = "SELECT * FROM v_active_projects";
        return await _connection.QueryAsync<ProjectView>(sql, transaction: _transaction);
    }

    public async Task<ProjectView> GetActiveProjectByIdAsync(Guid id)
    {
        // READING FROM VIEW
        var sql = "SELECT * FROM v_active_projects WHERE project_id = @id";
        return await _connection.QuerySingleOrDefaultAsync<ProjectView>(sql, new { id }, transaction: _transaction);
    }
}

public class TaskRepository : ITaskRepository
{
    private IDbTransaction _transaction;
    private IDbConnection _connection => _transaction.Connection;

    public TaskRepository(IDbTransaction transaction)
    {
        _transaction = transaction;
    }

    // Internal method to allow UoW to update the transaction
    public void SetTransaction(IDbTransaction transaction)
    {
        _transaction = transaction;
    }
    
    public async Task<IEnumerable<TaskDetailView>> GetTasksForProjectAsync(Guid projectId)
    {
        // READING FROM VIEW
        var sql = "SELECT * FROM v_project_task_details WHERE project_id = @projectId";
        return await _connection.QueryAsync<TaskDetailView>(sql, new { projectId }, transaction: _transaction);
    }

    public async Task UpdateTaskStatusAsync(Guid taskId, int newStatusId, Guid currentUserId)
    {
        // CALLING STORED PROCEDURE FOR WRITE
        await _connection.ExecuteAsync(
            "sp_update_task_status",
            new { p_task_id = taskId, p_status_id = newStatusId, p_user_id = currentUserId },
            transaction: _transaction,
            commandType: CommandType.StoredProcedure
        );
    }
}

// --- 5. EXAMPLE SERVICE LAYER USAGE ---

public class ProjectService
{
    private readonly string _connectionString;

    public ProjectService(string connectionString)
    {
        _connectionString = connectionString;
    }

    // This method demonstrates the Unit of Work pattern.
    // It archives a project and all its tasks in a single transaction.
    public async Task ArchiveProject(Guid projectId, Guid adminUserId)
    {
        // The service logic doesn't know about transactions,
        // it just knows about the Unit of Work.
        
        using (var uow = new NpgsqlUnitOfWork(_connectionString))
        {
            try
            {
                // We can use our custom transactional SP
                await uow.Projects.SoftDeleteProjectAsync(projectId, adminUserId);
                
                // OR, if we didn't have that SP, we could do it manually:
                
                // 1. Get all tasks for the project (from the view)
                // var tasks = await uow.Tasks.GetTasksForProjectAsync(projectId);
                // var archivedStatusId = 5; // Get this from lookup
                
                // 2. Update each task (calls sp_update_task_status)
                // foreach (var task in tasks)
                // {
                //     await uow.Tasks.UpdateTaskStatusAsync(task.TaskId, archivedStatusId, adminUserId);
                // }

                // 3. Soft delete the project (calls sp_soft_delete_project)
                // await uow.Projects.SoftDeleteProjectAsync(projectId, adminUserId);
                
                // 4. Commit the entire transaction
                await uow.CompleteAsync();
            }
            catch (Exception ex)
            {
                // Rollback is handled automatically by uow.Dispose()
                Console.WriteLine($"Failed to archive project: {ex.Message}");
                throw;
            }
        }
    }
}