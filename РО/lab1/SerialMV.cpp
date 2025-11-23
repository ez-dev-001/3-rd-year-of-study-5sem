#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void DummyDataInitialization(double* pMatrix, double* pVector, int Size) {
    for (int i = 0; i < Size; i++) {
        pVector[i] = 1;
        for (int j = 0; j < Size; j++)
            pMatrix[i * Size + j] = i;
    }
}

// ініціалізуємо генератор випадкових чисел
void RandomDataInitialization(double* pMatrix, double* pVector, int Size) {
    srand(unsigned(clock()));
    for (int i = 0; i < Size; i++) {
        pVector[i] = rand() / double(1000);
        for (int j = 0; j < Size; j++)
            pMatrix[i * Size + j] = rand() / double(1000);
    }
}

void ProcessInitialization(double*& pMatrix, double*& pVector, double*& pResult, int& Size) {
    do {
        printf("\nEnter the size of the initial objects: ");
        scanf("%d", &Size);
        printf("\nChosen objects size = %d\n", Size);
        if (Size <= 0)
            printf("\nSize of objects must be greater than 0!\n");
    } while (Size <= 0);

    pMatrix = new double[Size * Size];
    pVector = new double[Size];
    pResult = new double[Size];

    RandomDataInitialization(pMatrix, pVector, Size);
}

void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    for (int i = 0; i < RowCount; i++) {
        for (int j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * ColCount + j]);
        printf("\n");
    }
}

void PrintVector(double* pVector, int Size) {
    for (int i = 0; i < Size; i++)
        printf("%7.4f ", pVector[i]);
}

void ResultCalculation(double* pMatrix, double* pVector, double* pResult, int Size) {
    for (int i = 0; i < Size; i++) {
        pResult[i] = 0;
        for (int j = 0; j < Size; j++)
            pResult[i] += pMatrix[i * Size + j] * pVector[j];
    }
}

void ProcessTermination(double* pMatrix, double* pVector, double* pResult) {
    delete[] pMatrix;
    delete[] pVector;
    delete[] pResult;
}

int main() {
    double* pMatrix;
    double* pVector;
    double* pResult;
    int Size;
    clock_t start, finish;
    double duration;

    printf("Serial matrix-vector multiplication program\n");
    ProcessInitialization(pMatrix, pVector, pResult, Size);

  // printf("Initial Matrix \n");
  // PrintMatrix(pMatrix, Size, Size);
  // printf("Initial Vector \n");
  // PrintVector(pVector, Size);

    start = clock();
    ResultCalculation(pMatrix, pVector, pResult, Size);
    finish = clock();
    duration = (finish - start) / double(CLOCKS_PER_SEC);

// printf("\n Result Vector: \n");
// PrintVector(pResult, Size);
    printf("\n Time of execution: %f\n", duration);

    ProcessTermination(pMatrix, pVector, pResult);
    return 0;
}
