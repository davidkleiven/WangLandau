#ifndef FFTW_COMPLEX_PLACEHOLDER_H
#define FFTW_COMPLEX_PLACEHOLDER_H

#ifndef HAS_FFTW
#include <complex>
typedef complex_t fftw_complex;
typedef int fftw_direction;

const int FFTW_FORWARD = 1;
const int FFTW_BACKWARD = -1;
const int FFTW_ESTIMATE = 0x01;
const int FFTW_IN_PLACE = 0x02;

// Dummy value for an fftw ndplan
struct fftw_ndplan{};
#endif
#endif