#ifndef SERIALBUBBLESORT_H_
#define SERIALBUBBLESORT_H_

void ProcessInitialization(double *&Data, int& DataSize);

void ProcessTermination(double *Data);

void DummyDataInitialization(double*& Data, int& DataSize);

void RandomDataInitialization(double *&Data, int& DataSize);

void SerialBubble(double *Data, int DataSize);

#endif