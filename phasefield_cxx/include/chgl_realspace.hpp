#ifndef CHGL_REALSPACE_H
#define CHGL_REALSPACE_H
#include "chgl.hpp"
#include "sparse_matrix.hpp"
#include <array>

template<int dim>
class CHGLRealSpace: public CHGL<dim>{
public:
    CHGLRealSpace(int L, const std::string &prefix, unsigned int num_gl_fields, \
         double M, double alpha, double dt, double gl_damping, 
         const interface_vec_t &interface);

    /** Build the matrix for CHGL equations */
    void build2D();

    /** Implement the update function */
    virtual void update(int nsteps) override;

    /** Calculate the energy of the system */
    virtual double energy() const override; 
private:
    unsigned int implicitDir{0};
    std::array<SparseMatrix, dim+1> matrices;
    bool did_build_matrices{false};

    MMSP::vector<int> & wrap(MMSP::vector<int> &pos) const;

    unsigned int node_index(MMSP::vector<int> &pos) const;

    void add_cook_noise_to_fd_scheme(std::vector<double> &rhs, int field) const;

    /** Return the prefactor for the central stencil of the laplacian */
    double laplacian_central_stencil() const;

    /** Check if the timestep should be lowered */
    bool should_lower_timestep(double energy) const;
};

#endif