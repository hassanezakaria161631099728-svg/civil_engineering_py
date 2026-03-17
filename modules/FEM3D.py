import numpy as np
from typing import List, Tuple, Dict, Any
import matplotlib.pyplot as plt

class FEM2DSolver:
    """
    2D Frame Finite Element Method Solver
    3 DOF per node: ux, uy, rotz
    """
    
    def __init__(self):
        self.nodes = None
        self.elements = None
        self.loads = None
        self.boundary_conditions = None
        self.K_global = None
        self.displacements = None
        self.reactions = None
        self.element_forces = None
        
    def solve(self, nodes: List[Tuple[float, float]], 
              elements: List[Dict[str, Any]],
              loads: Dict[int, List[float]],
              boundary_conditions: Dict[int, List[bool]]):
        """
        Main solver function
        
        Parameters:
        -----------
        nodes : List of (x, y) coordinates for each node
        elements : List of dictionaries with:
            - 'nodes': [i, j] node indices
            - 'E': Young's modulus
            - 'A': Cross-sectional area
            - 'I': Moment of inertia
            - 'section_type': optional section properties
        loads : Dictionary with node index as key and [Fx, Fy, Mz] as value
        boundary_conditions : Dictionary with node index as key and [fixed_x, fixed_y, fixed_rot] as boolean list
        
        Returns:
        --------
        Dictionary with results
        """
        self.nodes = np.array(nodes)
        self.elements = elements
        self.loads = loads
        self.boundary_conditions = boundary_conditions
        
        # Step 1: Assemble global stiffness matrix
        self._assemble_global_stiffness()
        
        # Step 2: Assemble load vector
        F_global = self._assemble_load_vector()
        
        # Step 3: Apply boundary conditions
        K_reduced, F_reduced, free_dofs, fixed_dofs = self._apply_boundary_conditions(F_global)
        
        # Step 4: Solve for displacements
        U_reduced = np.linalg.solve(K_reduced, F_reduced)
        
        # Step 5: Reconstruct full displacement vector
        self.displacements = self._reconstruct_displacements(U_reduced, free_dofs, fixed_dofs)
        
        # Step 6: Calculate reactions
        self.reactions = self._calculate_reactions()
        
        # Step 7: Calculate element forces
        self.element_forces = self._calculate_element_forces()
        
        return self._compile_results()
    
    def _get_element_length_and_angle(self, node_i: np.ndarray, node_j: np.ndarray) -> Tuple[float, float]:
        """Calculate element length and angle with x-axis"""
        dx = node_j[0] - node_i[0]
        dy = node_j[1] - node_i[1]
        L = np.sqrt(dx**2 + dy**2)
        cos = dx / L
        sin = dy / L
        return L, cos, sin
    
    def _get_element_stiffness_matrix(self, element: Dict[str, Any]) -> np.ndarray:
        """Calculate element stiffness matrix in local coordinates"""
        E = element['E']
        A = element['A']
        I = element['I']
        nodes = element['nodes']
        
        node_i = self.nodes[nodes[0]]
        node_j = self.nodes[nodes[1]]
        L, cos, sin = self._get_element_length_and_angle(node_i, node_j)
        
        # Local stiffness matrix for 2D frame element (6x6)
        k_local = np.zeros((6, 6))
        
        # Axial stiffness
        EA_L = E * A / L
        k_local[0, 0] = EA_L
        k_local[0, 3] = -EA_L
        k_local[3, 0] = -EA_L
        k_local[3, 3] = EA_L
        
        # Bending stiffness terms
        EI_L = E * I / L
        EI_L2 = E * I / (L**2)
        EI_L3 = E * I / (L**3)
        
        # Bending terms (DOF: v1, θ1, v2, θ2)
        k_local[1, 1] = 12 * EI_L3
        k_local[1, 2] = 6 * EI_L2
        k_local[1, 4] = -12 * EI_L3
        k_local[1, 5] = 6 * EI_L2
        
        k_local[2, 1] = 6 * EI_L2
        k_local[2, 2] = 4 * EI_L
        k_local[2, 4] = -6 * EI_L2
        k_local[2, 5] = 2 * EI_L
        
        k_local[4, 1] = -12 * EI_L3
        k_local[4, 2] = -6 * EI_L2
        k_local[4, 4] = 12 * EI_L3
        k_local[4, 5] = -6 * EI_L2
        
        k_local[5, 1] = 6 * EI_L2
        k_local[5, 2] = 2 * EI_L
        k_local[5, 4] = -6 * EI_L2
        k_local[5, 5] = 4 * EI_L
        
        # Transformation matrix
        T = np.array([
            [cos, sin, 0, 0,    0,   0],
            [-sin, cos, 0, 0,    0,   0],
            [0,    0,   1, 0,    0,   0],
            [0,    0,   0, cos, sin, 0],
            [0,    0,   0, -sin, cos, 0],
            [0,    0,   0, 0,    0,   1]
        ])
        
        # Transform to global coordinates
        k_global = T.T @ k_local @ T
        
        return k_global
    
    def _assemble_global_stiffness(self):
        """Assemble global stiffness matrix"""
        n_nodes = len(self.nodes)
        n_dof = n_nodes * 3
        self.K_global = np.zeros((n_dof, n_dof))
        
        for idx, element in enumerate(self.elements):
            k_element = self._get_element_stiffness_matrix(element)
            nodes = element['nodes']
            
            # Create DOF mapping
            dof_i = [nodes[0]*3, nodes[0]*3 + 1, nodes[0]*3 + 2]
            dof_j = [nodes[1]*3, nodes[1]*3 + 1, nodes[1]*3 + 2]
            element_dofs = dof_i + dof_j
            
            # Add to global stiffness matrix
            for i, dof_i in enumerate(element_dofs):
                for j, dof_j in enumerate(element_dofs):
                    self.K_global[dof_i, dof_j] += k_element[i, j]
    
    def _assemble_load_vector(self) -> np.ndarray:
        """Assemble global load vector"""
        n_nodes = len(self.nodes)
        F_global = np.zeros(n_nodes * 3)
        
        for node_idx, load in self.loads.items():
            dof_start = node_idx * 3
            F_global[dof_start:dof_start + 3] = load
        
        return F_global
    
    def _apply_boundary_conditions(self, F_global: np.ndarray) -> Tuple[np.ndarray, np.ndarray, List[int], List[int]]:
        """Apply boundary conditions and reduce system"""
        n_dof = len(F_global)
        
        # Identify free and fixed DOFs
        free_dofs = []
        fixed_dofs = []
        
        for i in range(n_dof // 3):
            node_idx = i
            if node_idx in self.boundary_conditions:
                bc = self.boundary_conditions[node_idx]
                for j in range(3):
                    dof_idx = i * 3 + j
                    if bc[j]:  # Fixed DOF
                        fixed_dofs.append(dof_idx)
                    else:
                        free_dofs.append(dof_idx)
            else:
                # No boundary conditions specified, all DOFs are free
                for j in range(3):
                    free_dofs.append(i * 3 + j)
        
        # Reduce stiffness matrix and load vector
        K_reduced = self.K_global[np.ix_(free_dofs, free_dofs)]
        F_reduced = F_global[free_dofs]
        
        return K_reduced, F_reduced, free_dofs, fixed_dofs
    
    def _reconstruct_displacements(self, U_reduced: np.ndarray, free_dofs: List[int], fixed_dofs: List[int]) -> np.ndarray:
        """Reconstruct full displacement vector"""
        n_dof = len(free_dofs) + len(fixed_dofs)
        U_full = np.zeros(n_dof)
        
        # Set displacements for free DOFs
        for i, dof in enumerate(free_dofs):
            U_full[dof] = U_reduced[i]
        
        # Fixed DOFs remain zero (or could be prescribed displacements)
        return U_full
    
    def _calculate_reactions(self) -> Dict[int, List[float]]:
        """Calculate reactions at constrained DOFs"""
        if self.displacements is None:
            raise ValueError("Displacements not calculated yet")
        
        # R = K * U
        reactions_full = self.K_global @ self.displacements
        
        # Extract reactions only at constrained DOFs
        reactions = {}
        for node_idx, bc in self.boundary_conditions.items():
            dof_start = node_idx * 3
            node_reactions = []
            for j in range(3):
                if bc[j]:  # This DOF is constrained
                    node_reactions.append(reactions_full[dof_start + j])
                else:
                    node_reactions.append(0.0)
            reactions[node_idx] = node_reactions
        
        return reactions
    
    def _calculate_element_forces(self) -> List[Dict[str, Any]]:
        """Calculate internal forces for each element"""
        element_forces = []
        
        for element in self.elements:
            nodes = element['nodes']
            E = element['E']
            A = element['A']
            I = element['I']
            
            # Get element displacements in global coordinates
            dof_i = [nodes[0]*3, nodes[0]*3 + 1, nodes[0]*3 + 2]
            dof_j = [nodes[1]*3, nodes[1]*3 + 1, nodes[1]*3 + 2]
            element_dofs = dof_i + dof_j
            U_element_global = self.displacements[element_dofs]
            
            # Get transformation matrix
            node_i = self.nodes[nodes[0]]
            node_j = self.nodes[nodes[1]]
            L, cos, sin = self._get_element_length_and_angle(node_i, node_j)
            
            T = np.array([
                [cos, sin, 0, 0,    0,   0],
                [-sin, cos, 0, 0,    0,   0],
                [0,    0,   1, 0,    0,   0],
                [0,    0,   0, cos, sin, 0],
                [0,    0,   0, -sin, cos, 0],
                [0,    0,   0, 0,    0,   1]
            ])
            
            # Transform to local coordinates
            U_element_local = T @ U_element_global
            
            # Local stiffness matrix
            k_local = self._get_element_stiffness_matrix(element)
            
            # Calculate forces in local coordinates
            forces_local = k_local @ U_element_local
            
            # Extract axial, shear, and moment
            axial_force_i = forces_local[0]
            shear_force_i = forces_local[1]
            moment_i = forces_local[2]
            axial_force_j = forces_local[3]
            shear_force_j = forces_local[4]
            moment_j = forces_local[5]
            
            element_forces.append({
                'element_id': len(element_forces),
                'axial_forces': (axial_force_i, axial_force_j),
                'shear_forces': (shear_force_i, shear_force_j),
                'bending_moments': (moment_i, moment_j),
                'nodes': nodes
            })
        
        return element_forces
    
    def _compile_results(self) -> Dict[str, Any]:
        """Compile all results into a dictionary"""
        # Format displacements by node
        nodal_displacements = {}
        for i in range(len(self.nodes)):
            dof_start = i * 3
            nodal_displacements[i] = {
                'ux': self.displacements[dof_start],
                'uy': self.displacements[dof_start + 1],
                'rotz': self.displacements[dof_start + 2]
            }
        
        return {
            'nodal_displacements': nodal_displacements,
            'reactions': self.reactions,
            'element_forces': self.element_forces,
            'global_stiffness_matrix': self.K_global,
            'displacement_vector': self.displacements
        }
    
    def plot_structure(self, show_displacements=False, scale_factor=10.0):
        """Plot the structure with optional deformed shape"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot undeformed structure
        for element in self.elements:
            nodes = element['nodes']
            x = [self.nodes[nodes[0]][0], self.nodes[nodes[1]][0]]
            y = [self.nodes[nodes[0]][1], self.nodes[nodes[1]][1]]
            ax.plot(x, y, 'b-', linewidth=2, alpha=0.6)
        
        # Plot nodes
        ax.scatter(self.nodes[:, 0], self.nodes[:, 1], c='r', s=50, zorder=5)
        
        # Plot boundary conditions
        for node_idx, bc in self.boundary_conditions.items():
            x, y = self.nodes[node_idx]
            if bc[0]:  # Fixed in x
                ax.plot(x, y, '>', color='g', markersize=10)
            if bc[1]:  # Fixed in y
                ax.plot(x, y, '^', color='g', markersize=10)
            if bc[2]:  # Fixed rotation
                ax.plot(x, y, 'o', color='g', markersize=8, fillstyle='none')
        
        if show_displacements and self.displacements is not None:
            # Plot deformed structure
            deformed_nodes = self.nodes.copy()
            for i in range(len(self.nodes)):
                deformed_nodes[i, 0] += self.displacements[i*3] * scale_factor
                deformed_nodes[i, 1] += self.displacements[i*3 + 1] * scale_factor
            
            for element in self.elements:
                nodes = element['nodes']
                x = [deformed_nodes[nodes[0]][0], deformed_nodes[nodes[1]][0]]
                y = [deformed_nodes[nodes[0]][1], deformed_nodes[nodes[1]][1]]
                ax.plot(x, y, 'r--', linewidth=1.5, alpha=0.8)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.set_title('2D Frame Structure')
        
        if show_displacements:
            ax.legend(['Undeformed', 'Deformed'], loc='upper right')
        
        plt.tight_layout()
        return fig, ax


def example_usage():
    """Example usage of the FEM2D solver"""
    # Define nodes (x, y coordinates)
    nodes = [
        (0, 0),    # Node 0
        (5, 0),    # Node 1
        (5, 3),    # Node 2
        (0, 3)     # Node 3
    ]
    
    # Define elements (connectivity and properties)
    elements = [
        {'nodes': [0, 1], 'E': 210e9, 'A': 0.01, 'I': 3.92e-5},  # Element 0
        {'nodes': [1, 2], 'E': 210e9, 'A': 0.01, 'I': 3.92e-5},  # Element 1
        {'nodes': [2, 3], 'E': 210e9, 'A': 0.01, 'I': 3.92e-5},  # Element 2
        {'nodes': [3, 0], 'E': 210e9, 'A': 0.01, 'I': 3.92e-5}   # Element 3
    ]
    
    # Define loads (node index: [Fx, Fy, Mz])
    loads = {
        1: [1000, -500, 0],   # 10kN horizontal, 5kN vertical down at node 1
        2: [0, -1000, 200]    # 10kN vertical down, 2kNm moment at node 2
    }
    
    # Define boundary conditions (node index: [fixed_x, fixed_y, fixed_rot])
    boundary_conditions = {
        0: [True, True, True],   # Fixed in x, y, and rotation
        3: [True, True, False]   # Fixed in x and y, free rotation
    }
    
    # Create solver and solve
    solver = FEM2DSolver()
    results = solver.solve(nodes, elements, loads, boundary_conditions)
    
    # Print results
    print("="*60)
    print("2D FRAME FEM SOLVER RESULTS")
    print("="*60)
    
    print("\nNODAL DISPLACEMENTS:")
    print("-"*40)
    for node_id, disp in results['nodal_displacements'].items():
        print(f"Node {node_id}: ux = {disp['ux']:.6e} m, uy = {disp['uy']:.6e} m, rotz = {disp['rotz']:.6e} rad")
    
    print("\nREACTIONS:")
    print("-"*40)
    for node_id, react in results['reactions'].items():
        print(f"Node {node_id}: Rx = {react[0]:.2f} N, Ry = {react[1]:.2f} N, Mz = {react[2]:.2f} Nm")
    
    print("\nELEMENT FORCES:")
    print("-"*40)
    for elem in results['element_forces']:
        print(f"Element {elem['element_id']} (nodes {elem['nodes']}):")
        print(f"  Axial forces: N1 = {elem['axial_forces'][0]:.2f} N, N2 = {elem['axial_forces'][1]:.2f} N")
        print(f"  Shear forces: V1 = {elem['shear_forces'][0]:.2f} N, V2 = {elem['shear_forces'][1]:.2f} N")
        print(f"  Bending moments: M1 = {elem['bending_moments'][0]:.2f} Nm, M2 = {elem['bending_moments'][1]:.2f} Nm")    
    # Plot results
    fig1, ax1 = solver.plot_structure(show_displacements=False)
    fig1.suptitle("Undeformed Structure")    
    fig2, ax2 = solver.plot_structure(show_displacements=True, scale_factor=100)
    fig2.suptitle("Deformed Structure (scaled)")
    plt.show()    
    return results


if __name__ == "__main__":
    # Run example
    example_usage()