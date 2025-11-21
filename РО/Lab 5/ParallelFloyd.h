#ifndef PARALLELFLOYDSORT_H_
#define PARALLELFLOYDSORT_H_

void ProcessInitialization(int *&pMatrix, int *&pProcRows, int& Size,
int& RowNum);

bool CompareMatrices(int* matrix1, int* matrix2, int size);

void ProcessTermination(int *pMatrix, int *pProcRows);

void DummyDataInitialization(int *pMatrix, int Size);

void RandomDataInitialization(int *pMatrix, int Size);

void DataDistribution(int *pMatrix, int *pProcRows, int Size, int RowNum);

void ResultCollection(int *pMatrix, int *pProcRows, int Size, int RowNum);

void ParallelFloyd(int *pProcRows, int Size, int RowNum);

void RowDistribution(int *pProcRows, int Size, int RowNum, int k, int
*pRow);

void ParallelPrintMatrix(int *pProcRows, int Size, int RowNum);

void TestDistribution(int *pMatrix, int *pProcRows, int Size, int RowNum);

void TestResult(int *pMatrix, int *pSerialMatrix, int Size);

#endif