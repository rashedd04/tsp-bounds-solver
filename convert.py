import os
from tsp_instance import TSPInstance

######## CE CODE EST GENERE PAR L'IA POUR CONVERTIR LES FICHIERS TSP ET ATSP EN FICHIERS DAT 
# POUR LES METTRE SUR CPLEX ET CALCULER LES RESULTATS OPTIMALES####


def generate_cplex_dat():
    # Repo packaging: read instances from ./instances and write the .dat files next to them
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances"))
    files_to_convert = [
        "instance_8nodes.tsp",
        "warehouse_5v_10p.tsp",
        "warehouse_10v_30p.tsp", 
        "warehouse_10v_50p.tsp",
        "dantzig42.tsp",
        "pr76.tsp",
        "bays29.tsp",
        "ftv33.atsp",
        "ftv70.atsp",
        "p43.atsp"
    ]

    for filename in files_to_convert:
        if not os.path.exists(filename):
            print(f"Fichier introuvable : {filename}")
            continue
            
        # 1. Charger l'instance avec ta classe
        instance = TSPInstance.from_tsplib(filename)
        n = instance.n
        distances = instance.distances
        
        # 2. Nom du nouveau fichier .dat
        dat_filename = filename.replace('.tsp', '.dat').replace('.atsp', '.dat')
        
        # 3. Écriture au format OPL (CPLEX)
        with open(dat_filename, 'w') as f:
            f.write(f"n = {n};\n\n")
            f.write("c = [\n")
            
            for i in range(n):
                f.write("  [")
                # Joindre les distances de la ligne avec des virgules
                row_str = ", ".join(str(int(distances[i, j])) for j in range(n))
                f.write(row_str)
                
                # Si ce n'est pas la dernière ligne, ajouter une virgule
                if i < n - 1:
                    f.write("],\n")
                else:
                    f.write("]\n")
                    
            f.write("];\n")
            
        print(f" Fichier créé : {dat_filename}")

if __name__ == "__main__":
    generate_cplex_dat()