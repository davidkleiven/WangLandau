#include "khachaturyan.hpp"
#include "use_numpy.hpp"
#include "additional_tools.hpp"

using namespace std;
Khachaturyan::Khachaturyan(PyObject *ft_shape_func, PyObject *elastic_tensor, PyObject *misfit_strain){
    elastic.from_numpy(elastic_tensor);
    convertMisfit(misfit_strain);
    convertShapeFunc(ft_shape_func);
}

void Khachaturyan::convertMisfit(PyObject *pymisfit){
    PyObject *npy = PyArray_FROM_OTF(pymisfit, NPY_DOUBLE, NPY_IN_ARRAY);

    for (unsigned int i=0;i<3;i++)
    for (unsigned int j=0;j<3;j++){
        double *val = static_cast<double*>(PyArray_GETPTR2(npy, i, j));
        misfit[i][j] = *val;
    }
}

void Khachaturyan::convertShapeFunc(PyObject *ft_shp){
    PyObject *npy = PyArray_FROM_OTF(ft_shp, NPY_DOUBLE, NPY_IN_ARRAY);

    npy_intp* dims = PyArray_DIMS(npy);

    for (unsigned int i=0;i<dims[0];i++)
    {
        vector< vector<double> > vec_outer;
        for (unsigned int j=0;j<dims[1];j++){
            vector<double> vec_inner;
            for (unsigned int k=0;k<dims[2];k++){
                double *val = static_cast<double*>(PyArray_GETPTR3(npy, i, j, k));
                vec_inner.push_back(*val);
            }
            vec_outer.push_back(vec_inner);
        }
        ft_shape_func.push_back(vec_outer);
    } 
}

void Khachaturyan::green_function(mat3x3 &G, double direction[3]) const{
    mat3x3 Q;
    for (unsigned int i=0;i<3;i++)
    for (unsigned int p=0;p<3;p++)
    {
        Q[i][p] = 0.0;
        for (unsigned int j=0;j<3;j++)
        for (unsigned int l=0;l<3;l++){
            Q[i][p] += elastic(i, j, l, p)*direction[j]*direction[l];
        }
    }
    inverse3x3(Q, G);
}

PyObject* Khachaturyan::green_function(PyObject *direction) const{
    mat3x3 G;
    PyObject *npy_in = PyArray_FROM_OTF(direction, NPY_DOUBLE, NPY_IN_ARRAY);
    double *dir = static_cast<double*>(PyArray_GETPTR1(npy_in, 0));
    green_function(G, dir);
    Py_DECREF(npy_in);

    npy_intp dims[2] = {3, 3};
    PyObject *npy_out = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
    for (unsigned int i=0;i<3;i++)
    for (unsigned int j=0;j<3;j++){
        double *val = static_cast<double*>(PyArray_GETPTR2(npy_out, i, j));
        *val = G[i][j];
    }
    return npy_out;
}

void Khachaturyan::effective_stress(mat3x3 &eff_stress) const{
    for (unsigned int i=0;i<3;i++)
    for (unsigned int j=0;j<3;j++){
        eff_stress[i][j] = 0.0;
        for (unsigned int k=0;k<3;k++)
        for (unsigned int l=0;l<3;l++){
            eff_stress[i][j] += elastic(i, j, k, l)*misfit[k][l];
        }
    }
}

void Khachaturyan::wave_vector(unsigned int indx[3], double vec[3]) const{
    // Return the frequency follow Numpy conventions
    int sizes[3];
    sizes[0] = ft_shape_func.size();
    sizes[1] = ft_shape_func[0].size();
    sizes[2] = ft_shape_func[0][0].size();

    for(int i=0;i<3;i++){
        if (indx[i] < sizes[i]/2){
            vec[i] = static_cast<double>(indx[i])/sizes[i];
        }
        else{
            vec[i] = -1.0 + static_cast<double>(indx[i])/sizes[i];
        }
    }
}