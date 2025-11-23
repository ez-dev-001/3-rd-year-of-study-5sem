#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>

int ProcNum = 0;   //загальна кількість процесів у MPI_COMM_WORLD
int ProcRank = 0;  //індекс поточного процесу від 0 до ProcNum-1


void DummyDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j;
    for (i=0; i<Size; i++) {
        pVector[i] = 1;
        for (j=0; j<Size; j++)
            pMatrix[i*Size+j] = i;
    }
}

void RandomDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j;
    srand(unsigned(clock()));
    for (i=0; i<Size; i++) {
        pVector[i] = rand()/double(1000);
        for (j=0; j<Size; j++)
            pMatrix[i*Size+j] = rand()/double(1000);
    }
}



void ProcessInitialization(double* &pMatrix, double* &pVector,
                           double* &pResult, double* &pProcRows, double* &pProcResult,
                           int &Size, int &RowNum) {
    int RestRows; // к-сть рядків, що ще не розподілені між процесами
    int i;
    setvbuf(stdout, 0, _IONBF, 0);

    if (ProcRank == 0) {
        do {
            printf("\nEnter the size of the matrix and vector: ");
            scanf("%d", &Size);
            if (Size < ProcNum) {
                printf("Size of the objects must be greater than number of processes! \n");
            }
        }
        while (Size < ProcNum);
    }

    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);  //розсилаємо Size усім процесам

    //обчислення RowNum для поточного процесу при нерівному поділі
    RestRows = Size;
    for (i=0; i<ProcRank; i++)
        RestRows = RestRows-RestRows/(ProcNum-i);
    RowNum = RestRows/(ProcNum-ProcRank);

    pVector = new double[Size];
    pResult = new double[Size];
    pProcRows = new double[RowNum*Size];
    pProcResult = new double[RowNum];

    if (ProcRank == 0) {
        pMatrix = new double[Size*Size];
        RandomDataInitialization(pMatrix, pVector, Size);
    }
}



void DataDistribution(double* pMatrix, double* pProcRows, double* pVector,
                      int Size, int RowNum) {
    int *pSendNum;
    int *pSendInd;
    int RestRows=Size;

    MPI_Bcast(pVector, Size, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    //тимчасові таблиці розрізання матриці
    pSendInd = new int[ProcNum];
    pSendNum = new int[ProcNum];
    
    //ідея: послідовно "відрізаємо" частки від решти рядків так, щоб кожен наступний процес отримував залишок процесів
    RowNum = (Size/ProcNum);
    pSendNum[0] = RowNum*Size;
    pSendInd[0] = 0;
    for (int i=1; i<ProcNum; i++) {
        RestRows -= RowNum;
        RowNum = RestRows/(ProcNum-i);
        pSendNum[i] = RowNum*Size;
        pSendInd[i] = pSendInd[i-1]+pSendNum[i-1];
    }

    MPI_Scatterv(pMatrix, pSendNum, pSendInd, MPI_DOUBLE, pProcRows,
                 pSendNum[ProcRank], MPI_DOUBLE, 0, MPI_COMM_WORLD);

    delete[] pSendNum;
    delete[] pSendInd;
}

void ResultReplication(double* pProcResult, double* pResult, int Size, int RowNum) {
    int *pReceiveNum;
    int *pReceiveInd;
    int RestRows=Size;
    int i;

    pReceiveNum = new int[ProcNum];
    pReceiveInd = new int[ProcNum];

    pReceiveInd[0] = 0;
    pReceiveNum[0] = Size/ProcNum;
    for (i=1; i<ProcNum; i++) {
        RestRows -= pReceiveNum[i-1];
        pReceiveNum[i] = RestRows/(ProcNum-i);
        pReceiveInd[i] = pReceiveInd[i-1]+pReceiveNum[i-1];
    }

    MPI_Allgatherv(pProcResult, pReceiveNum[ProcRank], MPI_DOUBLE, pResult,
                   pReceiveNum, pReceiveInd, MPI_DOUBLE, MPI_COMM_WORLD);

    delete[] pReceiveNum;
    delete[] pReceiveInd;
}

void SerialResultCalculation(double* pMatrix, double* pVector, double* pResult, int Size) {
    int i, j;
    for (i=0; i<Size; i++) {
        pResult[i] = 0;
        for (j=0; j<Size; j++)
            pResult[i] += pMatrix[i*Size+j]*pVector[j];
    }
}

void ParallelResultCalculation(double* pProcRows, double* pVector,
                               double* pProcResult, int Size, int RowNum) {
    int i, j;
    for (i=0; i<RowNum; i++) {
        pProcResult[i] = 0;
        for (j=0; j<Size; j++)
            pProcResult[i] += pProcRows[i*Size+j]*pVector[j];
    }
}

void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j;
    for (i=0; i<RowCount; i++) {
        for (j=0; j<ColCount; j++)
            printf("%7.4f ", pMatrix[i*ColCount+j]);
        printf("\n");
    }
}

void PrintVector(double* pVector, int Size) {
    int i;
    for (i=0; i<Size; i++)
        printf("%7.4f ", pVector[i]);
    printf("\n");
}

//перевірка, чи паралельний результат збігається з послідовним
void TestResult(double* pMatrix, double* pVector, double* pResult, int Size) {
    double* pSerialResult;
    int equal = 0;
    int i;

    if (ProcRank == 0) {
        pSerialResult = new double[Size];
        SerialResultCalculation(pMatrix, pVector, pSerialResult, Size);
        for (i=0; i<Size; i++) {
            if (pResult[i] != pSerialResult[i])
                equal = 1;
        }
        if (equal == 1)
            printf("Results are NOT identical. Check your code.\n");
        else
            printf("Results are identical.\n");
        delete[] pSerialResult;
    }
}

//звільняємо пам’ять
void ProcessTermination(double* pMatrix, double* pVector, double* pResult,
                        double* pProcRows, double* pProcResult) {
    if (ProcRank == 0)
        delete[] pMatrix;
    delete[] pVector;
    delete[] pResult;
    delete[] pProcRows;
    delete[] pProcResult;
}

int main(int argc, char* argv[]) {
    double *pMatrix = NULL;
    double *pVector = NULL;
    double *pResult = NULL;
    double *pProcRows = NULL;
    double *pProcResult = NULL;
    int Size;
    int RowNum;
    double Start, Finish, Duration;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    if (ProcRank == 0) {
        printf("Parallel matrix-vector multiplication program\n");
    }

    // ВСІ процеси виконують це
    ProcessInitialization(pMatrix, pVector, pResult, pProcRows, pProcResult, Size, RowNum);

    Start = MPI_Wtime();

    DataDistribution(pMatrix, pProcRows, pVector, Size, RowNum);
    ParallelResultCalculation(pProcRows, pVector, pProcResult, Size, RowNum);
    ResultReplication(pProcResult, pResult, Size, RowNum);

    Finish = MPI_Wtime();
    Duration = Finish - Start;

    TestResult(pMatrix, pVector, pResult, Size);

    if (ProcRank == 0) {
        printf("Time of execution = %f seconds\n", Duration);
    }

    ProcessTermination(pMatrix, pVector, pResult, pProcRows, pProcResult);

    MPI_Finalize();
    return 0;
}