#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <mpi.h>

int ProcNum = 0;      // Number of processes
int ProcRank = 0;     // Rank of current process
int GridSize;          // Size of processor grid
MPI_Comm GridComm;     // Grid communicator
MPI_Comm RowComm;      // Row communicator
MPI_Comm ColComm;      // Column communicator
int GridCoords[2];     // Process coordinates in grid

// Function for simple initialization of matrix elements
void DummyDataInitialization(double* pAMatrix, double* pBMatrix, int Size) {
    for (int i = 0; i < Size; i++)
        for (int j = 0; j < Size; j++) {
            pAMatrix[i * Size + j] = 1;
            pBMatrix[i * Size + j] = 1;
        }
}

// Function for formatted matrix output
void PrintMatrix(double* pMatrix, int RowCount, int ColCount) {
    for (int i = 0; i < RowCount; i++) {
        for (int j = 0; j < ColCount; j++)
            printf("%7.4f ", pMatrix[i * RowCount + j]);
        printf("\n");
    }
}

// Function for creating the 2D grid and sub-communicators
void CreateGridCommunicators() {
    int DimSize[2] = { GridSize, GridSize };
    int Periodic[2] = { 1, 1 };
    MPI_Cart_create(MPI_COMM_WORLD, 2, DimSize, Periodic, 1, &GridComm);
    MPI_Cart_coords(GridComm, ProcRank, 2, GridCoords);

    int Subdims[2];
    // Row communicator
    Subdims[0] = 0; Subdims[1] = 1;
    MPI_Cart_sub(GridComm, Subdims, &RowComm);
    // Column communicator
    Subdims[0] = 1; Subdims[1] = 0;
    MPI_Cart_sub(GridComm, Subdims, &ColComm);
}

// Function for memory allocation and data initialization
void ProcessInitialization(double*& pAMatrix, double*& pBMatrix,
    double*& pCMatrix, double*& pAblock, double*& pBblock,
    double*& pCblock, double*& pMatrixAblock, int& Size, int& BlockSize) {
    
    if (ProcRank == 0) {
        do {
            printf("\nEnter the size of matrices: ");
            scanf("%d", &Size);
            if (Size % GridSize != 0)
                printf("Size must be divisible by GridSize!\n");
        } while (Size % GridSize != 0);
    }
    MPI_Bcast(&Size, 1, MPI_INT, 0, MPI_COMM_WORLD);

    BlockSize = Size / GridSize;
    pAblock = new double[BlockSize * BlockSize];
    pBblock = new double[BlockSize * BlockSize];
    pCblock = new double[BlockSize * BlockSize];
    pMatrixAblock = new double[BlockSize * BlockSize];

    if (ProcRank == 0) {
        pAMatrix = new double[Size * Size];
        pBMatrix = new double[Size * Size];
        pCMatrix = new double[Size * Size];
        DummyDataInitialization(pAMatrix, pBMatrix, Size);
    }
    for (int i = 0; i < BlockSize * BlockSize; i++)
        pCblock[i] = 0;
}

// Function for checkerboard matrix decomposition
void CheckerboardMatrixScatter(double* pMatrix, double* pMatrixBlock, int Size, int BlockSize) {
    double* pMatrixRow = new double[BlockSize * Size];
    if (GridCoords[1] == 0)
        MPI_Scatter(pMatrix, BlockSize * Size, MPI_DOUBLE, pMatrixRow,
            BlockSize * Size, MPI_DOUBLE, 0, ColComm);

    for (int i = 0; i < BlockSize; i++)
        MPI_Scatter(&pMatrixRow[i * Size], BlockSize, MPI_DOUBLE,
            &(pMatrixBlock[i * BlockSize]), BlockSize, MPI_DOUBLE, 0, RowComm);
    delete[] pMatrixRow;
}

// Function for data distribution among processes
void DataDistribution(double* pAMatrix, double* pBMatrix,
    double* pMatrixAblock, double* pBblock, int Size, int BlockSize) {
    CheckerboardMatrixScatter(pAMatrix, pMatrixAblock, Size, BlockSize);
    CheckerboardMatrixScatter(pBMatrix, pBblock, Size, BlockSize);
}

// Broadcast blocks of matrix A to rows
void ABlockCommunication(int iter, double* pAblock, double* pMatrixAblock, int BlockSize) {
    int Pivot = (GridCoords[0] + iter) % GridSize;
    if (GridCoords[1] == Pivot)
        for (int i = 0; i < BlockSize * BlockSize; i++)
            pAblock[i] = pMatrixAblock[i];
    MPI_Bcast(pAblock, BlockSize * BlockSize, MPI_DOUBLE, Pivot, RowComm);
}

// Cyclic shift of matrix B blocks along columns
void BblockCommunication(double* pBblock, int BlockSize, MPI_Comm ColComm) {
    int NextProc = (GridCoords[0] + GridSize - 1) % GridSize;
    int PrevProc = (GridCoords[0] + 1) % GridSize;
    MPI_Status status;
    MPI_Sendrecv_replace(pBblock, BlockSize * BlockSize, MPI_DOUBLE,
                         NextProc, 0, PrevProc, 0, ColComm, &status);
}

// Local block multiplication
void BlockMultiplication(double* pAblock, double* pBblock, double* pCblock, int BlockSize) {
    for (int i = 0; i < BlockSize; i++)
        for (int j = 0; j < BlockSize; j++)
            for (int k = 0; k < BlockSize; k++)
                pCblock[i * BlockSize + j] += pAblock[i * BlockSize + k] * pBblock[k * BlockSize + j];
}

// Parallel Fox algorithm
void ParallelResultCalculation(double* pAblock, double* pMatrixAblock,
    double* pBblock, double* pCblock, int BlockSize) {
    for (int iter = 0; iter < GridSize; iter++) {
        ABlockCommunication(iter, pAblock, pMatrixAblock, BlockSize);
        BlockMultiplication(pAblock, pBblock, pCblock, BlockSize);
        BblockCommunication(pBblock, BlockSize, ColComm);
    }
}

// Function for program termination
void ProcessTermination(double* pAMatrix, double* pBMatrix, double* pCMatrix,
    double* pAblock, double* pBblock, double* pCblock, double* pMatrixAblock) {
    if (ProcRank == 0) {
        delete[] pAMatrix;
        delete[] pBMatrix;
        delete[] pCMatrix;
    }
    delete[] pAblock;
    delete[] pBblock;
    delete[] pCblock;
    delete[] pMatrixAblock;
}

int main(int argc, char* argv[]) {
    double* pAMatrix;
    double* pBMatrix;
    double* pCMatrix;
    double* pAblock;
    double* pBblock;
    double* pCblock;
    double* pMatrixAblock;
    int Size, BlockSize;
    double Start, Finish, Duration;

    setvbuf(stdout, 0, _IONBF, 0);
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &ProcNum);
    MPI_Comm_rank(MPI_COMM_WORLD, &ProcRank);

    GridSize = sqrt((double)ProcNum);
    if (ProcNum != GridSize * GridSize) {
        if (ProcRank == 0)
            printf("Number of processes must be a perfect square!\n");
        MPI_Finalize();
        return 0;
    }

    if (ProcRank == 0)
        printf("Parallel matrix multiplication program (Fox algorithm)\n");

    CreateGridCommunicators();
    ProcessInitialization(pAMatrix, pBMatrix, pCMatrix, pAblock, pBblock,
        pCblock, pMatrixAblock, Size, BlockSize);

    DataDistribution(pAMatrix, pBMatrix, pMatrixAblock, pBblock, Size, BlockSize);

    MPI_Barrier(MPI_COMM_WORLD);
    Start = MPI_Wtime();
    ParallelResultCalculation(pAblock, pMatrixAblock, pBblock, pCblock, BlockSize);
    Finish = MPI_Wtime();
    Duration = Finish - Start;

    if (ProcRank == 0)
        printf("\nExecution time: %f seconds\n", Duration);

    ProcessTermination(pAMatrix, pBMatrix, pCMatrix, pAblock, pBblock,
        pCblock, pMatrixAblock);
    MPI_Finalize();
    return 0;
}
