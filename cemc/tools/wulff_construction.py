import numpy as np

class WulffConstruction(object):
    def __init__(self, cluster=None, max_dist_in_element=None):
        self.cluster = cluster
        self.max_dist_in_element = max_dist_in_element
        self.mesh = self._mesh()
        self.surf_mesh = self._extract_surface_mesh(self.mesh)

    def _mesh(self):
        """Create mesh of all the atoms in the cluster.

        :return: Mesh
        :rtype: scipy.spatial.Delaunay
        """
        from scipy.spatial import Delaunay
        points = self.cluster.get_positions()
        delaunay = Delaunay(points)
        return delaunay

    def _filter_max_dist_in_element(self, simplices):
        """Filter out triangulations where the distance is too large."""
        if self.max_dist_in_element is None:
            return simplices

        filtered = []
        for tup in simplices:
            dists = []
            for root in tup:
                new_dist = self.cluster.get_distances(root, tup)
                dists += list(new_dist)

            if max(dists) < self.max_dist_in_element:
                filtered.append(tup)
        return filtered

    def show(self):
        """Show the triangulation in 3D."""
        from matplotlib import pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection="3d")
        pos = self.cluster.get_positions()
        from itertools import combinations
        for tri in self.mesh.simplices:
            for comb in combinations(tri, 2):
                x1 = pos[comb[0], 0]
                x2 = pos[comb[1], 0]
                y1 = pos[comb[0], 1]
                y2 = pos[comb[1], 1]
                z1 = pos[comb[0], 2]
                z2 = pos[comb[1], 2]
                ax.plot([x1, x2], [y1, y2], zs=[z1, z2], color="black")
        plt.show()

    def _extract_surface_mesh(self, volume_mesh):
        """Extract surface cells.

        :return: List of indices belonging to the surface
        :rtype: List of tuples
        """
        from itertools import combinations
        simplices = self._filter_max_dist_in_element(volume_mesh.simplices)
        statistics = {}
        for tri in simplices:
            for comb in combinations(tri, 3):
                key = tuple(sorted(comb))
                statistics[key] = statistics.get(key, 0) + 1

        # Trianges on surface enters only once. If they are in bulk
        # they always occures twice
        tri_surf = []
        for k, v in statistics.items():
            if v == 1:
                tri_surf.append(k)
        return tri_surf

    def _unique_surface_indices(self, surf_mesh):
        """Extract the unique positions of the atoms on the surface

        :return: List with indices of the atoms belonging to the surface
        :rtype: Atoms on the surface
        """
        flattened = []
        for tup in surf_mesh:
            flattened += list(tup)
        return list(set(flattened))

    @property
    def surface_atoms(self):
        """Return all the surface atoms."""
        indx = self._unique_surface_indices(self.surf_mesh)
        return self.cluster[indx]

    def normal_vector(self, facet):
        """Find the normal vector of the triangular facet.

        :param list facet: List with three integer describing the facet

        :return: The normal vector n = [n_x, n_y, n_z]
        :rtype: numpy 1D array of length 3
        """
        assert len(facet) == 3
        pos = self.cluster.get_positions()
        v1 = pos[facet[1], :] - pos[facet[0], :]
        v2 = pos[facet[2], :] - pos[facet[0], :]
        n = np.cross(v1, v2)
        length = np.sqrt(np.sum(n**2))
        return n / length

    @property
    def interface_energy(self):
        com = np.sum(self.cluster.get_positions(), axis=0) / len(self.cluster)

        data = []
        pos = self.cluster.get_positions()
        for facet in self.surf_mesh:
            n = self.normal_vector(facet)
            point_on_facet = pos[facet[0], :]
            vec = point_on_facet - com
            dist = vec.dot(n)

            if dist < 0.0:
                data.append((-n, -dist))
            else:
                data.append((n, dist))
        return data
