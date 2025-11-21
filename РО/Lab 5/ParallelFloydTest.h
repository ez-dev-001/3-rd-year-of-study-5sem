#ifndef PARALLELFLOYDTESTSORT_H_
#define PARALLELFLOYDTESTSORT_H_

void CopyMatrix(int *pMatrix, int Size, int *pMatrixCopy);

void SerialFloyd(int *pMatrix, int Size);

void PrintMatrix(int *pMatrix, int RowCount, int ColCount);

bool CompareMatrices(int* matrix1, int* matrix2, int size);

#endif