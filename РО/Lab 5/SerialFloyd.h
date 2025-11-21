#ifndef SERIALFLOYDSORT_H_
#define SERIALFLOYDSORT_H_

void ProcessInitialization(int *&pMatrix, int& Size);

void ProcessTermination(int *pMatrix);

void DummyDataInitialization(int *pMatrix, int Size);

void RandomDataInitialization(int *pMatrix, int Size);

void SerialFloyd(int *pMatrix, int Size);

#endif