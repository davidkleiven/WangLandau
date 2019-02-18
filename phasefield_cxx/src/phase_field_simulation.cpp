#include "phase_field_simulation.hpp"
#include <stdexcept>
#include <sstream>
#include "MMSP.grid.h"
#include "MMSP.vector.h"
#include <ctime>

using namespace std;

template<int dim>
PhaseFieldSimulation<dim>::PhaseFieldSimulation(int L, \
                     const std::string &prefix, unsigned int num_fields): \
                     L(L), prefix(prefix), num_fields(num_fields){
                         if (dim == 1){
                             grid_ptr = new MMSP::grid<dim, MMSP::vector<double> >(num_fields, 0, L);
                         }
                         else if (dim == 2){
                             grid_ptr = new MMSP::grid<dim, MMSP::vector<double> >(num_fields, 0, L, 0, L);
                         }
                         else if (dim == 3){
                             grid_ptr = new MMSP::grid<dim, MMSP::vector<double> >(num_fields, 0, L, 0, L, 0, L);
                         }
                         srand(time(0));
                     };

template<int dim>
PhaseFieldSimulation<dim>::~PhaseFieldSimulation(){
    delete grid_ptr;
}

template<int dim>
void PhaseFieldSimulation<dim>::random_initialization(unsigned int field_no, double lower, double upper){

    double range = upper - lower;
    for (int i=0;i<MMSP::nodes(*this->grid_ptr);i++){
        (*grid_ptr)(i)[field_no] = range*rand()/static_cast<double>(RAND_MAX) + lower;
    }

    // Save grid
    stringstream ss;
    ss << prefix << ".grid";
    grid_ptr->output(ss.str().c_str());
}

template<int dim>
void PhaseFieldSimulation<dim>::random_initialization(double lower, double upper){
    random_initialization(0, lower, upper);
}

template<int dim>
void PhaseFieldSimulation<dim>::run(unsigned int start, unsigned int nsteps, int increment){
    for (unsigned int iter=start;iter<nsteps+start; iter+=increment){
        this->update(increment);

        // Generate output filename
        stringstream ss;
        ss << prefix << get_digit_string(iter+increment) << ".grid";
        grid_ptr->output(ss.str().c_str());
    }
}

template<int dim>
void PhaseFieldSimulation<dim>::from_file(const std::string &fname){
    grid_ptr->input(fname.c_str(), 1, false);
}

template<int dim>
string PhaseFieldSimulation<dim>::get_digit_string(unsigned int iter) const{
    stringstream ss;
    int num_digits = log10(iter);
    if (num_digits < num_digits_in_file){
        for (unsigned int i=0;i<num_digits_in_file - num_digits;i++){
            ss << 0;
        }
    }
    ss << iter;
    return ss.str();
}

template<int dim>
void PhaseFieldSimulation<dim>::from_npy_array(PyObject *npy_arrays){
    int size = PyList_Size(npy_arrays);

    if (size != this->num_fields){
        stringstream ss;
        ss << "Length of the numpy arrays does not match the number of phase fields. ";
        ss << "Expected " << this->num_fields << " numpy arrays, ";
        ss << "got " << size;
        throw invalid_argument(ss.str());
    }

    // Loop through the arrays
    for (unsigned int i=0;i<size;i++){
        PyObject *npy_arr = PyList_GetItem(npy_arrays, i);
        init_field_from_npy_arr(i, npy_arr);
    }
}

template<int dim>
void PhaseFieldSimulation<dim>::init_field_from_npy_arr(unsigned int field, PyObject *np_arr){
    PyObject *arr = PyArray_FROM_OTF(np_arr, NPY_DOUBLE, NPY_IN_ARRAY);
    unsigned int num_nodes = MMSP::nodes(*grid_ptr);
    int num_dims = PyArray_NDIM(arr);

    if (num_dims != dim){
        stringstream ss;
        ss << "Dimension of Numpy array does not match the dimension ";
        ss << "of the simulation cell. ";
        ss << "Expected: " << dim;
        ss << " Got: " << num_dims;
        Py_DECREF(arr);
        throw invalid_argument(ss.str());
    }

    npy_intp* dims = PyArray_DIMS(arr);
    // Check that the number of elements in the array is correct
    int num_elements = 1;
    for (unsigned int i=0;i<num_dims;i++){
        num_elements *= dims[i];
    }

    if (num_elements != num_nodes){
        stringstream ss;
        ss << "Numpy array has the wrong number of elements ";
        ss << "Expected: " << num_nodes;
        ss << " Got: " << num_elements;
        Py_DECREF(arr);
        throw invalid_argument(ss.str());
    }

    // Populate current field
    if (dim == 1){
        for (unsigned int i=0;i<dims[0];i++){
            double *val = static_cast<double*>(PyArray_GETPTR1(arr, i));
            (*grid_ptr)(i)[field] = *val;
        }
    }
    else if (dim == 2){
        for (unsigned int i=0;i<dims[0];i++)
        for (unsigned int j=0;j<dims[1];j++){
            double *val = static_cast<double*>(PyArray_GETPTR2(arr, i, j));
            MMSP::vector<int> x(dim);
            x[0] = i;
            x[1] = j;
            (*grid_ptr)(x)[field] = *val;
        }
    }
    else if (dim == 3){
        for (unsigned int i=0;i<dims[0];i++)
        for (unsigned int j=0;j<dims[1];j++)
        for (unsigned int k=0;k<dims[2];k++){
            double *val = static_cast<double*>(PyArray_GETPTR3(arr, i, j, k));
            MMSP::vector<int> x(dim);
            x[0] = i;
            x[1] = j;
            x[2] = k;
            (*grid_ptr)(x) = *val;
        }
    }
    else{
        Py_DECREF(arr);
        stringstream ss;
        ss << "Initialization from Numpy array is only supported for ";
        ss << "1D, 2D and 3D problems";
        ss << "Dimension of current problem " << dim;
        throw runtime_error(ss.str());
    }
    Py_DECREF(arr);
}
// Explicit instatiations
template class PhaseFieldSimulation<1>;
template class PhaseFieldSimulation<2>;
template class PhaseFieldSimulation<3>;