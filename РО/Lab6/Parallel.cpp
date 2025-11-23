#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <mpi.h>

int ProcNum;  // Кількість процесів
int ProcRank; // Ранг поточного процесу

// === Допоміжні функції ===

// Функція для виводу матриці (або її смуги)
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j;
    for (i = 0; i < RowCount; i++) {
        for (j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        printf("\n");
    }
}

// Ініціалізація даних (Task 10: Випадкові числа всередині, 100 на межах)
void DataInitialization(double* pMatrix, int Size) {
    int i, j;
    srand(unsigned(clock()));
    for (i = 0; i < Size; i++) {
        for (j = 0; j < Size; j++) {
            if ((i == 0) || (i == Size - 1) || (j == 0) || (j == Size - 1))
                pMatrix[i * Size + j] = 100.0; // Граничні умови
            else
                pMatrix[i * Size + j] = rand() / (double)RAND_MAX * 10.0; // Випадкові значення
        }
    }
}

// === Логіка розподілу даних (Task 11: Довільний розмір сітки) ===

// Функція розподілу даних (використовує Scatterv для нерівних частин)
void DataDistribution(double* pMatrix, double* pProcRows, int Size, int RowNum, int* sendCounts, int* displs) {
    
    // 1. Розсилаємо внутрішні рядки матриці (від 1 до Size-2)
    // pMatrix + Size пропускає перший граничний рядок глобальної матриці
    // pProcRows + Size пропускає верхній "тіньовий" рядок локальної смуги
    MPI_Scatterv(pMatrix + Size, sendCounts, displs, MPI_DOUBLE,
                 pProcRows + Size, (RowNum - 2) * Size, MPI_DOUBLE,
                 0, MPI_COMM_WORLD);

    // 2. Копіюємо верхній граничний рядок для процесу 0
    if (ProcRank == 0) {
        for (int j = 0; j < Size; j++) pProcRows[j] = pMatrix[j];
    }

    // 3. Процес 0 відправляє нижній граничний рядок останньому процесу
    // Це потрібно, бо Scatterv розсилав тільки внутрішню частину
    if (ProcRank == 0) {
        // Останній рядок глобальної матриці
        MPI_Send(pMatrix + Size * (Size - 1), Size, MPI_DOUBLE, ProcNum - 1, 101, MPI_COMM_WORLD);
    }
    
    // Останній процес отримує свій нижній граничний рядок (останній рядок локальної смуги)
    if (ProcRank == ProcNum - 1) {
        MPI_Recv(pProcRows + Size * (RowNum - 1), Size, MPI_DOUBLE, 0, 101, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }
}

// Функція збору результатів (Gatherv)
void ResultCollection(double* pMatrix, double* pProcRows, int Size, int RowNum, int* recvCounts, int* displs) {
    // Збираємо тільки внутрішні розраховані рядки (зсув +Size)
    MPI_Gatherv(pProcRows + Size, (RowNum - 2) * Size, MPI_DOUBLE,
                pMatrix + Size, recvCounts, displs, MPI_DOUBLE,
                0, MPI_COMM_WORLD);
}

// === Обчислювальне ядро ===

// Обмін тіньовими гранями (halo rows)
void ExchangeData(double* pProcRows, int Size, int RowNum) {
    MPI_Status status;
    int NextProc = (ProcRank == ProcNum - 1) ? MPI_PROC_NULL : ProcRank + 1;
    int PrevProc = (ProcRank == 0) ? MPI_PROC_NULL : ProcRank - 1;

    // Обмін з наступним (відправляємо свій останній робочий, отримуємо його перший як наш нижній тіньовий)
    // RowNum-2 — індекс останнього робочого рядка
    MPI_Sendrecv(pProcRows + Size * (RowNum - 2), Size, MPI_DOUBLE, NextProc, 4,
                 pProcRows + Size * (RowNum - 1), Size, MPI_DOUBLE, NextProc, 4,
                 MPI_COMM_WORLD, &status);

    // Обмін з попереднім (відправляємо свій перший робочий, отримуємо його останній як наш верхній тіньовий)
    MPI_Sendrecv(pProcRows + Size, Size, MPI_DOUBLE, PrevProc, 5,
                 pProcRows, Size, MPI_DOUBLE, PrevProc, 5,
                 MPI_COMM_WORLD, &status);
}

// Одна ітерація методу Гаусса-Зейделя
double IterationCalculation(double* pProcRows, int Size, int RowNum) {
    double dmax = 0.0;
    for (int i = 1; i < RowNum - 1; i++) { // Проходимо тільки по власних рядках (1 .. RowNum-2)
        for (int j = 1; j < Size - 1; j++) {
            double temp = pProcRows[i * Size + j];
            pProcRows[i * Size + j] = 0.25 * (
                pProcRows[(i + 1) * Size + j] +
                pProcRows[(i - 1) * Size + j] +
                pProcRows[i * Size + j + 1] +
                pProcRows[i * Size + j - 1]
            );
            double dm = fabs(pProcRows[i * Size + j] - temp);
            if (dmax < dm) dmax = dm;
        }
    }
    return dmax;
}

// Паралельний розрахунок
void ParallelResultCalculation(double* pProcRows, int Size, int RowNum, double Eps, int &Iterations) {
    double ProcDelta, GlobalDelta;
    Iterations = 0;
    do {
        Iterations++;
        // 1. Обмін даними між процесами
        ExchangeData(pProcRows, Size, RowNum);
        
        // 2. Локальна ітерація
        ProcDelta = IterationCalculation(pProcRows, Size, RowNum);
        
        // 3. Збір максимальної похибки з усіх процесів
        MPI_Allreduce(&ProcDelta, &GlobalDelta, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
        
    } while (GlobalDelta > Eps);
}

// === Верифікація (Task 10) ===

// Послідовний алгоритм (для перевірки)
void SerialResultCalculation(double* pMatrixCopy, int Size, double Eps) {
    int Iterations = 0;
    double dmax, temp;
    do {
        dmax = 0.0;
        for (int i = 1; i < Size - 1; i++) {
            for (int j = 1; j < Size - 1; j++) {
                temp = pMatrixCopy[i * Size + j];
                pMatrixCopy[i * Size + j] = 0.25 * (
                    pMatrixCopy[(i + 1) * Size + j] +
                    pMatrixCopy[(i - 1) * Size + j] +
                    pMatrixCopy[i * Size + j + 1] +
                    pMatrixCopy[i * Size + j - 1]
                );
                double dm = fabs(pMatrixCopy[i * Size + j] - temp);
                if (dmax < dm) dmax = dm;
            }
        }
        Iterations++;
    } while (dmax > Eps);
}

// Функція тестування результатів
void TestResult(double* pMatrix, double* pMatrixSerial, int Size, double Eps) {
    double max_diff = 0.0;
    int errors = 0;

    // Виконуємо послідовний розрахунок на копії даних
    SerialResultCalculation(pMatrixSerial, Size, Eps);

    for (int i = 0; i < Size * Size; i++) {
        if (fabs(pMatrix[i] - pMatrixSerial[i]) > 0.001) { // Допуск трохи більший за Eps через похибки округлення float
            errors++;
            double diff = fabs(pMatrix[i] - pMatrixSerial[i]);
            if (diff > max_diff) max_diff = diff;
        }
    }

    if (errors == 0) {
        printf("\n[TEST PASSED] Parallel and Serial results match!\n");
    } else {
        printf("\n[TEST FAILED] Found %d mismatches. Max diff: %f\n", errors, max_diff);
    }
}

// === Main ===

int main(int argc, char* argv[]) {
    double* pMatrix = NULL;       // Глобальна матриця (тільки на root)
    double* pMatrixSerial = NULL; // Копія для послідовного тесту (тільки на root)
    double* pProcRows = NULL;     // Локальна смуга
    int Size;                     // Розмір сторони сітки
    int RowNum;                   // Кількість рядків у локальній смузі
    double Eps;                   // Точність
    int Iterations;
    double Start, Finish, Duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0) {
        printf("--- Perfect Parallel Gauss-Seidel Algorithm ---\n");
        
        // Ввід даних
        do {
            printf("\nEnter grid size (must be > %d): ", ProcNum);
            if (scanf("%d", &Size) != 1) Size = 0;
        } while (Size <= ProcNum);

        do {
            printf("Enter accuracy (e.g., 0.01): ");
            if (scanf("%lf", &Eps) != 1) Eps = 0;
        } while (Eps <= 0);
    }

    // Розсилка параметрів усім процесам
    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&Eps, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    // === Розрахунок балансування навантаження (Task 11) ===
    // Визначаємо, скільки рядків отримає кожен процес
    // Внутрішніх рядків: Size - 2. Ділимо їх між процесами.
    int restRows = Size - 2;
    int baseRows = restRows / ProcNum;
    int remainder = restRows % ProcNum;

    // Локальна кількість внутрішніх рядків
    int localInternalRows = baseRows + (ProcRank < remainder ? 1 : 0);
    RowNum = localInternalRows + 2; // +2 тіньових рядки

    // Виділення пам'яті під локальну смугу
    pProcRows = new double[RowNum * Size];

    // Підготовка масивів для Scatterv/Gatherv (тільки на root)
    int *sendCounts = NULL;
    int *displs = NULL;

    if (ProcRank == 0) {
        pMatrix = new double[Size * Size];
        pMatrixSerial = new double[Size * Size];
        
        DataInitialization(pMatrix, Size);
        // Створюємо копію для верифікації
        for(int k=0; k<Size*Size; k++) pMatrixSerial[k] = pMatrix[k];

        printf("Initial Matrix generated.\n");

        // Розрахунок зміщень для Scatterv
        sendCounts = new int[ProcNum];
        displs = new int[ProcNum];
        
        int currentDisp = 0;
        for (int i = 0; i < ProcNum; i++) {
            int rowsForProc = baseRows + (i < remainder ? 1 : 0);
            sendCounts[i] = rowsForProc * Size;
            displs[i] = currentDisp;
            currentDisp += sendCounts[i];
        }
    }

    // === Початок роботи ===
    Start = MPI_Wtime();

    // 1. Розподіл даних
    DataDistribution(pMatrix, pProcRows, Size, RowNum, sendCounts, displs);

    // 2. Обчислення
    ParallelResultCalculation(pProcRows, Size, RowNum, Eps, Iterations);

    // 3. Збір результатів
    ResultCollection(pMatrix, pProcRows, Size, RowNum, sendCounts, displs);

    Finish = MPI_Wtime();
    Duration = Finish - Start;

    if (ProcRank == 0) {
        printf("\n--- Results ---\n");
        printf("Iterations: %d\n", Iterations);
        printf("Execution Time: %f seconds\n", Duration);
        
        // Вивід для малих матриць
        if (Size <= 15) {
            printf("Result Matrix:\n");
            PrintMatrix(pMatrix, Size, Size);
        }

        // 4. Верифікація (Task 10)
        printf("\n--- Verifying Logic ---");
        TestResult(pMatrix, pMatrixSerial, Size, Eps);
        
        // Очищення пам'яті на Root
        delete[] pMatrix;
        delete[] pMatrixSerial;
        delete[] sendCounts;
        delete[] displs;
    }

    // Очищення локальної пам'яті
    delete[] pProcRows;

    MPI_Finalize();
    return 0;
}