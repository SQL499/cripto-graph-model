import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from community import community_louvain  # Para detección de comunidades Louvain
import matplotlib.patches as mpatches

# Cargar dataset
df = pd.read_csv("dataset_cripto_completo.csv")

# Preprocesar categorías: convertir string a lista
def parse_categories(cat_str):
    if pd.isna(cat_str) or cat_str.strip() == "":
        return []
    return [c.strip() for c in cat_str.split(",")]

df['categorias_list'] = df['categoría'].apply(parse_categories)

# Preprocesar contratos: convertir string a set de contratos para similitud
def parse_contracts(contracts_str):
    if pd.isna(contracts_str) or contracts_str.strip() == "":
        return set()
    # Separar por comas y extraer solo la dirección (después de ':')
    parts = contracts_str.split(",")
    contracts = set()
    for p in parts:
        if ':' in p:
            contracts.add(p.split(":")[1].strip())
        else:
            contracts.add(p.strip())
    return contracts

df['contratos_set'] = df['contratos'].apply(parse_contracts)

# Crear grafo
G = nx.Graph()

# Añadir nodos con atributos
for idx, row in df.iterrows():
    G.add_node(row['id'], 
               nombre=row['nombre'],
               simbolo=row['símbolo'],
               categoria=row['categoría'],
               precio_usd=row['precio_usd'],
               capitalizacion_usd=row['capitalización_usd'],
               volumen_24h_usd=row['volumen_24h_usd'],
               ranking=row['ranking'],
               actividad_comunitaria=row['actividad_comunitaria'],
               listado_cex=row['listado_cex'],
               contratos_set=row['contratos_set'],
               categorias_list=row['categorias_list']
              )

# Funciones de similitud
def categoria_similitud(cat_list1, cat_list2):
    return len(set(cat_list1).intersection(set(cat_list2)))

def contratos_similitud(set1, set2):
    if not set1 or not set2:
        return 0
    return len(set1.intersection(set2)) / len(set1.union(set2))

# Añadir aristas ponderadas con métrica compuesta
nodes = list(G.nodes(data=True))
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        id1, attr1 = nodes[i]
        id2, attr2 = nodes[j]

        cat_sim = categoria_similitud(attr1['categorias_list'], attr2['categorias_list'])
        if cat_sim == 0:
            continue

        # Similitud contratos
        cont_sim = contratos_similitud(attr1['contratos_set'], attr2['contratos_set'])

        # Diferencia relativa capitalización
        cap1 = attr1['capitalizacion_usd']
        cap2 = attr2['capitalizacion_usd']
        cap_diff = abs(cap1 - cap2) / max(cap1, cap2) if max(cap1, cap2) > 0 else 0

        # Diferencia relativa volumen
        vol1 = attr1['volumen_24h_usd']
        vol2 = attr2['volumen_24h_usd']
        vol_diff = abs(vol1 - vol2) / max(vol1, vol2) if max(vol1, vol2) > 0 else 0

        # Diferencia relativa actividad comunitaria
        act1 = attr1['actividad_comunitaria']
        act2 = attr2['actividad_comunitaria']
        act_diff = abs(act1 - act2) / max(act1, act2) if max(act1, act2) > 0 else 0

        # Combinación ponderada (puedes ajustar pesos)
        weight = (cat_sim * 2) + (cont_sim * 3) + (1 - cap_diff) + (1 - vol_diff) + (1 - act_diff)
        if weight > 0:
            G.add_edge(id1, id2, weight=weight)

# Detección de comunidades con Louvain
partition = community_louvain.best_partition(G)

# Asignar color a cada comunidad
comunidades = set(partition.values())
colores_comunidades = plt.cm.tab20(np.linspace(0, 1, len(comunidades)))
color_map_comunidades = {com: colores_comunidades[i] for i, com in enumerate(comunidades)}
node_colors = [color_map_comunidades[partition[node]] for node in G.nodes()]

# Visualización
plt.figure(figsize=(14, 11))
pos = nx.spring_layout(G, seed=42)

# Tamaño nodos proporcional a capitalización (normalizado)
caps = np.array([attr['capitalizacion_usd'] for _, attr in G.nodes(data=True)])
caps_norm = 1000 * (caps - caps.min()) / (caps.max() - caps.min() + 1e-6) + 100

# Dibujar nodos y aristas
nx.draw_networkx_nodes(G, pos, node_size=caps_norm, node_color=node_colors, alpha=0.9)
edges = G.edges(data=True)
weights = [edata['weight']*0.5 for _, _, edata in edges]  # Ajustar grosor
nx.draw_networkx_edges(G, pos, width=weights, alpha=0.4)

# Etiquetas con símbolo, tamaño ajustado según cantidad de nodos
font_size = 12 if len(G.nodes) < 30 else 6
labels = {node: attr['simbolo'] for node, attr in G.nodes(data=True)}
nx.draw_networkx_labels(G, pos, labels, font_size=font_size)

plt.title("Grafo de proyectos criptomonedas - Comunidades y Métricas Compuestas")
plt.axis('off')

# Leyenda de comunidades
patches = [mpatches.Patch(color=color_map_comunidades[com], label=f'Comunidad {com}') for com in comunidades]
plt.legend(handles=patches, loc='best', fontsize='small')

plt.show()