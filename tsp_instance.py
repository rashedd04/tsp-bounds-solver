import numpy as np
from typing import List, Tuple, Dict, Optional, Set
import os
import sys


class TSPInstance:
    """Instance TSP (STSP - Symmetric)"""

    def __init__(self, distances: np.ndarray, nodes: List[int], name: str = "TSP", positions: np.ndarray = None):
        self.distances = distances
        self.positions = positions
        self.nodes = nodes
        self.name = name

    @property
    def n(self) -> int:
        return len(self.nodes)

    def distance(self, i: int, j: int) -> float:
        return self.distances[i, j]

    @classmethod
    def from_matrix(cls, distances: List[List[float]], name: str = "TSP"):
        dist_array = np.array(distances, dtype=float)
        nodes = list(range(dist_array.shape[0]))
        return cls(dist_array, nodes, name)

    def __repr__(self):
        return f"TSPInstance(distances={self.distances}, nodes={self.nodes}, name='{self.name}')"

    @classmethod
    def from_tsplib(cls, instance_name: str):
        """Charge une instance TSPLIB depuis un fichier local."""
        if not os.path.exists(instance_name):
            print(f"Erreur: Fichier {instance_name} non trouvé")
            return None
        
        try:
            with open(instance_name, 'r') as f:
                content = f.read()
            name = os.path.splitext(os.path.basename(instance_name))[0]
            
            if instance_name.endswith('.atsp'):
                return cls._parse_atsp_file(instance_name)
            
            return cls._parse_tsplib_content(content, name)
            
        except Exception as e:
            print(f"Erreur lors du chargement de {instance_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @classmethod
    def _parse_atsp_file(cls, file_path: str):
        """Parse un fichier ATSP (Asymmetric TSP) manuellement."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        name = os.path.splitext(os.path.basename(file_path))[0]
        lines = content.strip().split('\n')
        
        dimension = 0
        edge_weight_section_idx = -1
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith("DIMENSION"):
                dimension = int(line_stripped.split(":")[1].strip())
            elif line_stripped.startswith("EDGE_WEIGHT_SECTION"):
                edge_weight_section_idx = i + 1
                break
        
        if dimension == 0 or edge_weight_section_idx < 0:
            print(f"Erreur: dimension ou EDGE_WEIGHT_SECTION non trouvée")
            return None
        
        values = []
        for i in range(edge_weight_section_idx, len(lines)):
            line_stripped = lines[i].strip()
            if line_stripped and not line_stripped.startswith("EOF"):
                parts = line_stripped.split()
                for part in parts:
                    try:
                        values.append(float(part))
                    except ValueError:
                        pass
        
        distances = np.zeros((dimension, dimension), dtype=float)
        idx = 0
        for i in range(dimension):
            for j in range(dimension):
                if idx < len(values):
                    distances[i, j] = values[idx]
                    idx += 1
                else:
                    distances[i, j] = float('inf')
        
        nodes = list(range(dimension))
        return cls(distances, nodes, name, positions=None)

    
    @classmethod
    def _parse_tsplib_content(cls, content: str, name: str):
        """Parse le contenu d'un fichier TSPLIB (.tsp ou .atsp)."""
        lines = content.strip().split('\n')
        
        dimension = 0
        coord_section_idx = -1
        display_section_idx = -1
        edge_weight_section_idx = -1
        edge_weight_type = "EUC_2D"
        edge_weight_format = "FULL_MATRIX"
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith("DIMENSION"):
                dimension = int(line_stripped.split(":")[1].strip())
            elif line_stripped.startswith("EDGE_WEIGHT_TYPE"):
                edge_weight_type = line_stripped.split(":")[1].strip()
            elif line_stripped.startswith("EDGE_WEIGHT_FORMAT"):
                edge_weight_format = line_stripped.split(":")[1].strip()
            elif line_stripped.startswith("NODE_COORD_SECTION"):
                coord_section_idx = i + 1
            elif line_stripped.startswith("DISPLAY_DATA_SECTION"):
                display_section_idx = i + 1
            elif line_stripped.startswith("EDGE_WEIGHT_SECTION"):
                edge_weight_section_idx = i + 1
        
        if dimension == 0:
            raise ValueError("Dimension non trouvée dans le fichier TSPLIB")
        
        if edge_weight_type == "EXPLICIT":
            distances = np.zeros((dimension, dimension), dtype=float)
            
            if edge_weight_section_idx > 0:
                values = []
                for i in range(edge_weight_section_idx, len(lines)):
                    line_stripped = lines[i].strip()
                    if not line_stripped or line_stripped.startswith("EOF"):
                        break
                    if not line_stripped.startswith("NODE_COORD") and not line_stripped.startswith("DISPLAY"):
                        parts = line_stripped.split()
                        try:
                            values.extend([float(x) for x in parts])
                        except ValueError:
                            continue
                
                if edge_weight_format == "LOWER_DIAG_ROW":
                    idx = 0
                    for i in range(dimension):
                        for j in range(i + 1):
                            if idx < len(values):
                                distances[i, j] = values[idx]
                                distances[j, i] = values[idx]
                            idx += 1
                
                else:
                    idx = 0
                    for i in range(dimension):
                        for j in range(dimension):
                            if idx < len(values):
                                distances[i, j] = values[idx]
                            idx += 1
            
            positions = None
            if coord_section_idx > 0:
                positions = np.zeros((dimension, 2), dtype=float)
                for i in range(coord_section_idx, min(coord_section_idx + dimension, len(lines))):
                    line_stripped = lines[i].strip()
                    if not line_stripped or line_stripped.startswith("EOF"):
                        break
                    parts = line_stripped.split()
                    if len(parts) >= 3:
                        node_id = int(parts[0]) - 1
                        positions[node_id] = [float(parts[1]), float(parts[2])]
            elif display_section_idx > 0:
                positions = np.zeros((dimension, 2), dtype=float)
                for i in range(display_section_idx, min(display_section_idx + dimension, len(lines))):
                    line_stripped = lines[i].strip()
                    if not line_stripped or line_stripped.startswith("EOF"):
                        break
                    parts = line_stripped.split()
                    if len(parts) >= 3:
                        node_id = int(parts[0]) - 1
                        positions[node_id] = [float(parts[1]), float(parts[2])]
            
            nodes = list(range(dimension))
            return cls(distances, nodes, name, positions)
        
        positions = np.zeros((dimension, 2), dtype=float)
        section_idx = coord_section_idx if coord_section_idx > 0 else display_section_idx
        
        if section_idx > 0:
            for i in range(section_idx, min(section_idx + dimension, len(lines))):
                line_stripped = lines[i].strip()
                if not line_stripped or line_stripped.startswith("EOF"):
                    break
                parts = line_stripped.split()
                if len(parts) >= 3:
                    node_id = int(parts[0]) - 1
                    positions[node_id] = [float(parts[1]), float(parts[2])]
        
        distances = np.zeros((dimension, dimension), dtype=float)
        for i in range(dimension):
            for j in range(dimension):
                if i != j:
                    if edge_weight_type == "EUC_2D":
                        distances[i, j] = np.sqrt(
                            (positions[i, 0] - positions[j, 0])**2 + 
                            (positions[i, 1] - positions[j, 1])**2
                        )
                    else:
                        distances[i, j] = float('inf')
        
        nodes = list(range(dimension))
        return cls(distances, nodes, name, positions)
