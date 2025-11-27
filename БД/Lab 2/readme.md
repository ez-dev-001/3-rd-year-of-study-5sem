ІНСТРУКЦІЯ ДО ЛАБОРАТОРНОЇ РОБОТИ №2 (NoSQL)

Для здачі роботи вам потрібно відправити викладачу наступні 4 файли:

01_Theory_Report.md - Теоретичний звіт (пояснення).

02_SQL_Schema.sql - Скрипт SQL таблиці для тестів.

03_Program.cs - Код програми.

benchmark_results.txt - Файл з результатами тестів (ГЕНЕРУЄТЬСЯ АВТОМАТИЧНО).

ЯК ОТРИМАТИ ФАЙЛ РЕЗУЛЬТАТІВ:

Переконайтеся, що запущені MySQL, MongoDB та Redis.

Створіть новий проект Console App:

dotnet new console -n NoSqlLab

Встановіть бібліотеки:

dotnet add package MySql.Data
dotnet add package MongoDB.Driver
dotnet add package StackExchange.Redis

Замініть код у Program.cs на код з файлу 03_Program.cs.

Запустіть програму:

dotnet run

Після завершення роботи у папці з проектом з'явиться файл benchmark_results.txt.
Цей файл містить усі цифри (мілісекунди) і є підтвердженням виконання роботи.