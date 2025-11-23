#include <stdio.h>
#include <stdlib.h>
// #include <conio.h>
#include <time.h>
#include <math.h>

int* pSerialPivotPos;  // Number of pivot rows selected at the iterations
int* pSerialPivotIter; // Iterations, at which the rows were pivots

// Function for simple initialization of the matrix and the vector elements
void DummyDataInitialization (double* pMatrix, double* pVector, int Size) {
    int i, j; // Loop variables
    for (i = 0; i < Size; i++) {
        pVector[i] = i + 1;
        for (j = 0; j < Size; j++) {
            if (j <= i)
                pMatrix[i*Size + j] = 1;
            else
                pMatrix[i*Size + j] = 0;
        }
    }
}

// Function for random initialization of the matrix and the vector elements
void RandomDataInitialization(double* pMatrix, double* pVector, int Size) {
    int i, j; // Loop variables
    srand(unsigned(clock()));
    for (i = 0; i < Size; i++) {
        pVector[i] = rand() / double(1000);
        for (j = 0; j < Size; j++) {
            if (j <= i)
                pMatrix[i*Size + j] = rand() / double(1000);
            else
                pMatrix[i*Size + j] = 0;
        }
    }
}

// Function for memory allocation and data initialization
void ProcessInitialization (double* &pMatrix, double* &pVector,
                           double* &pResult, int &Size) {
    printf("\nEnter the size of the matrix and the vector: ");
    if (scanf("%d", &Size) != 1) {
    printf("Input error!\n");
    return;
}

    pMatrix = new double [Size * Size];
    pVector = new double [Size];
    pResult = new double [Size];

    pSerialPivotPos = new int [Size];
    pSerialPivotIter = new int [Size];

    // Simple initialization of the matrix and the vector elements
    // DummyDataInitialization(pMatrix, pVector, Size);
    RandomDataInitialization(pMatrix, pVector, Size);

    for (int i=0; i<Size; i++) {
        pSerialPivotIter[i] = -1;
    }
}

// Function for matrix and vector output
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    int i, j;
    for (i=0; i<RowCount; i++) {
        for (j=0; j<ColCount; j++)
            printf("%7.4f ", pMatrix[i*ColCount + j]);
        printf("\n");
    }
}

void PrintVector(double* pVector, int Size) {
    for (int i=0; i<Size; i++)
        printf("%7.4f ", pVector[i]);
    printf("\n");
}

// Function for searching the pivot row
int SerialFindPivotRow(double* pMatrix, int Size,
                       int Iter, int* pPivotPos) {
    int PivotRow = -1;
    double MaxValue = 0;
    for (int i = Iter; i < Size; i++) {
        if (fabs(pMatrix[i*Size + Iter]) > MaxValue) {
            MaxValue = fabs(pMatrix[i*Size + Iter]);
            PivotRow = i;
        }
    }
    pPivotPos[Iter] = PivotRow;
    return PivotRow;
}

// Function for performing the Gaussian elimination
void SerialGaussianElimination(double* pMatrix, double* pVector, int Size) {
    int i, j, k;
    int PivotRow;
    double PivotValue, Mult;

    for (i = 0; i < Size - 1; i++) {
        PivotRow = SerialFindPivotRow(pMatrix, Size, i, pSerialPivotPos);
        if (PivotRow != i) {
            for (j = 0; j < Size; j++) {
                double Temp = pMatrix[i*Size + j];
                pMatrix[i*Size + j] = pMatrix[PivotRow*Size + j];
                pMatrix[PivotRow*Size + j] = Temp;
            }
            double Temp = pVector[i];
            pVector[i] = pVector[PivotRow];
            pVector[PivotRow] = Temp;
        }

        pSerialPivotIter[i] = i;

        for (k = i + 1; k < Size; k++) {
            Mult = pMatrix[k*Size + i] / pMatrix[i*Size + i];
            for (j = i; j < Size; j++)
                pMatrix[k*Size + j] -= Mult * pMatrix[i*Size + j];
            pVector[k] -= Mult * pVector[i];
        }
    }
    pSerialPivotIter[Size-1] = Size-1;
}

// Function for performing the back substitution
void SerialBackSubstitution(double* pMatrix, double* pVector,
                            double* pResult, int Size) {
    int i, j;

    for (i = Size-1; i >= 0; i--) {
        pResult[i] = pVector[i];
        for (j = i+1; j < Size; j++)
            pResult[i] -= pMatrix[i*Size + j] * pResult[j];
        pResult[i] /= pMatrix[i*Size + i];
    }
}

// Function for the execution of Gauss algorithm
void SerialResultCalculation(double* pMatrix, double* pVector,
                             double* pResult, int Size) {
    SerialGaussianElimination(pMatrix, pVector, Size);
    SerialBackSubstitution(pMatrix, pVector, pResult, Size);
}

// Function for computational process termination
void ProcessTermination(double* pMatrix, double* pVector, double* pResult) {
    delete [] pMatrix;
    delete [] pVector;
    delete [] pResult;
}

int main() {
    double* pMatrix;   // Matrix of the linear system
    double* pVector;   // Right parts of the linear system
    double* pResult;   // Result vector
    int Size;          // Size of matrix and vector
    time_t start, finish;
    double duration;

    printf("Serial Gauss algorithm for solving linear systems\n");

    ProcessInitialization(pMatrix, pVector, pResult, Size);

    //printf("Initial Matrix \n");
    //PrintMatrix(pMatrix, Size, Size);
    //printf("Initial Vector \n");
    //PrintVector(pVector, Size);

    start = clock();
    SerialResultCalculation(pMatrix, pVector, pResult, Size);
    finish = clock();

    duration = (finish - start) / double(CLOCKS_PER_SEC);

    //printf("\n Result Vector: \n");
    //PrintVector(pResult, Size);

    printf("\n Time of execution: %f\n", duration);

    ProcessTermination(pMatrix, pVector, pResult);
    return 0;
}
