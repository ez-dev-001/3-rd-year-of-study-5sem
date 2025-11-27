using System;
using System.IO;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MySql.Data.MySqlClient; 
using MongoDB.Driver;         
using MongoDB.Bson;           
using StackExchange.Redis;    

namespace NoSQL_Lab_ProjectManagement
{
    // Модель даних для генерації
    public class ActivityLog
    {
        public int ProjectId { get; set; }
        public int UserId { get; set; }
        public string ActionType { get; set; }
        public string DetailsPayload { get; set; } // JSON контент
        public DateTime Timestamp { get; set; }
    }

    class Program
    {
        // НАЛАШТУВАННЯ ПІДКЛЮЧЕННЯ
        const string MySqlConnStr = "Server=localhost;Database=project_management;Uid=root;Pwd=password;";
        const string MongoConnStr = "mongodb://localhost:27017";
        const string RedisConnStr = "localhost:6379";
        
        const string ReportFile = "benchmark_results.txt"; // Файл звіту
        const int DATA_SIZE = 10000; // Кількість записів для тесту

        static async Task Main(string[] args)
        {
            // Очищення старого звіту
            File.WriteAllText(ReportFile, $"=== ЗВІТ ЛАБОРАТОРНОЇ РОБОТИ №2 ===\nДата: {DateTime.Now}\n\n");
            
            Log($"=== SQL vs NoSQL Benchmark ({DATA_SIZE} записів) ===\n");

            // 1. Генерація тестових даних
            Log("Генерація даних...");
            var logs = GenerateLogs(DATA_SIZE);

            // 2. Тестування MySQL (Реляційна)
            Log("\n--- 1. MySQL Benchmark ---");
            await RunMySqlBenchmark(logs);

            // 3. Тестування MongoDB (Документна)
            Log("\n--- 2. MongoDB Benchmark ---");
            await RunMongoBenchmark(logs);

            // 4. Тестування Redis (Key-Value)
            Log("\n--- 3. Redis (Key-Value) Implementation ---");
            await RunRedisDemo();

            Log("\nТестування завершено. Результати збережено у файл.");
        }

        // Логування в консоль та файл одночасно
        static void Log(string message)
        {
            Console.WriteLine(message);
            File.AppendAllText(ReportFile, message + Environment.NewLine);
        }

        // --- ГЕНЕРАТОР ---
        static List<ActivityLog> GenerateLogs(int count)
        {
            var list = new List<ActivityLog>();
            var rnd = new Random();
            var actions = new[] { "TaskCreated", "StatusUpdate", "FileUploaded", "CommentAdded" };

            for (int i = 0; i < count; i++)
            {
                list.Add(new ActivityLog
                {
                    ProjectId = rnd.Next(1, 50),
                    UserId = rnd.Next(1, 100),
                    ActionType = actions[rnd.Next(actions.Length)],
                    Timestamp = DateTime.Now,
                    DetailsPayload = $@"{{ ""description"": ""Log entry #{i}"", ""meta_code"": {rnd.Next(9999)} }}"
                });
            }
            return list;
        }

        // --- MYSQL ЛОГІКА ---
        static async Task RunMySqlBenchmark(List<ActivityLog> logs)
        {
            using (var conn = new MySqlConnection(MySqlConnStr))
            {
                try { await conn.OpenAsync(); }
                catch (Exception ex) { Log($"MySQL Error: {ex.Message}"); return; }

                using (var cmd = new MySqlCommand("TRUNCATE TABLE project_logs_benchmark", conn))
                    await cmd.ExecuteNonQueryAsync();

                var sw = Stopwatch.StartNew();
                using (var trans = await conn.BeginTransactionAsync())
                {
                    foreach (var log in logs)
                    {
                        var sql = @"INSERT INTO project_logs_benchmark 
                                   (project_id, user_id, action_type, details_json, created_at) 
                                   VALUES (@pid, @uid, @act, @det, @date)";
                        using (var cmd = new MySqlCommand(sql, conn, (MySqlTransaction)trans))
                        {
                            cmd.Parameters.AddWithValue("@pid", log.ProjectId);
                            cmd.Parameters.AddWithValue("@uid", log.UserId);
                            cmd.Parameters.AddWithValue("@act", log.ActionType);
                            cmd.Parameters.AddWithValue("@det", log.DetailsPayload);
                            cmd.Parameters.AddWithValue("@date", log.Timestamp);
                            await cmd.ExecuteNonQueryAsync();
                        }
                    }
                    await trans.CommitAsync();
                }
                sw.Stop();
                Log($"[INSERT] Час запису {DATA_SIZE} рядків: {sw.ElapsedMilliseconds} ms");

                sw.Restart();
                using (var cmd = new MySqlCommand("SELECT * FROM project_logs_benchmark WHERE project_id = 10", conn))
                using (var reader = await cmd.ExecuteReaderAsync())
                {
                    int count = 0;
                    while (await reader.ReadAsync()) count++;
                    sw.Stop();
                    Log($"[SELECT] Пошук по ProjectId=10: {sw.ElapsedMilliseconds} ms (Знайдено: {count})");
                }
            }
        }

        // --- MONGODB ЛОГІКА ---
        static async Task RunMongoBenchmark(List<ActivityLog> logs)
        {
            var client = new MongoClient(MongoConnStr);
            var db = client.GetDatabase("pm_system_nosql");
            var collection = db.GetCollection<BsonDocument>("activity_logs");

            await db.DropCollectionAsync("activity_logs");

            var bsonDocs = logs.Select(l => new BsonDocument
            {
                { "project_id", l.ProjectId },
                { "user_id", l.UserId },
                { "action", l.ActionType },
                { "created_at", l.Timestamp },
                { "details", BsonDocument.Parse(l.DetailsPayload) }
            }).ToList();

            var sw = Stopwatch.StartNew();
            await collection.InsertManyAsync(bsonDocs);
            sw.Stop();
            Log($"[INSERT] Час запису {DATA_SIZE} документів: {sw.ElapsedMilliseconds} ms");

            var indexKeys = Builders<BsonDocument>.IndexKeys.Ascending("project_id");
            await collection.Indexes.CreateOneAsync(new CreateIndexModel<BsonDocument>(indexKeys));

            sw.Restart();
            var filter = Builders<BsonDocument>.Filter.Eq("project_id", 10);
            var result = await collection.Find(filter).ToListAsync();
            sw.Stop();
            Log($"[FIND]   Пошук по ProjectId=10: {sw.ElapsedMilliseconds} ms (Знайдено: {result.Count})");
        }

        // --- REDIS ЛОГІКА ---
        static async Task RunRedisDemo()
        {
            ConnectionMultiplexer redis;
            try { redis = await ConnectionMultiplexer.ConnectAsync(RedisConnStr); }
            catch { Log("Redis недоступний."); return; }

            var db = redis.GetDatabase();
            string key = "project:10:stats";

            Log("Сценарій: Отримання статистики проекту для Dashboard.");
            
            var sw = Stopwatch.StartNew();
            string cachedData = await db.StringGetAsync(key);
            
            if (string.IsNullOrEmpty(cachedData))
            {
                Log("Cache MISS. Виконуємо 'важкий' розрахунок...");
                await Task.Delay(500); 
                string freshData = "{ \"tasks_open\": 15, \"budget_used\": 45000.00 }";
                await db.StringSetAsync(key, freshData, TimeSpan.FromSeconds(60));
                Log("Дані збережено в Redis.");
            }
            sw.Stop();

            sw.Restart();
            string hitData = await db.StringGetAsync(key);
            sw.Stop();
            
            Log($"Cache HIT. Дані: {hitData}");
            Log($"Час доступу до Redis: {sw.ElapsedTicks} тіків (менше 1 мс)");
        }
    }
}