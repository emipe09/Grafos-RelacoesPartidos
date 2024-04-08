import networkx as nx
import csv
import matplotlib.pyplot as plt
import numpy as np
import random

def read_graph_file(year):
    G = nx.Graph()

    with open(f"graph{year}.txt", 'r', encoding='utf-8') as file:
        for row in file:
            row_content = row.strip().split(";")
            politician1 = row_content[0]
            politician2 = row_content[1]
            agreement_votes = int(row_content[2])
            G.add_node(politician1)
            G.add_node(politician2)
            G.add_weighted_edges_from([(politician1, politician2, agreement_votes)])
    return G


def read_politicians_file(year):
    politicians = {}

    with open(f"politicians{year}.txt", 'r', encoding='utf-8') as file:
        for row in file:
            row_content = row.strip().split(";")
            politician = row_content[0]
            party = row_content[1]
            votes = int(row_content[2])
            politicians[politician] = {"Partido": party, "Votos": votes}

    return politicians

def apply_filters(graph, politicians, parties):
    filtered_graph = graph.copy()

    if len(parties) > 0:
        nodes_to_remove = [node for node in graph.nodes if politicians.get(node, {}).get("Partido") not in parties]
        filtered_graph.remove_nodes_from(nodes_to_remove)

    return filtered_graph


def normalize_weights(graph, politicians):
    normalized_graph = graph.copy()

    for edge in normalized_graph.edges(data=True):
        source, target, data = edge
        weight = data['weight']
        normalized_weight = weight / min(politicians[source]["Votos"], politicians[target]["Votos"])
        normalized_graph[source][target]["weight"] = normalized_weight

    return normalized_graph


def apply_edge_threshold(graph, threshold):
    filtered_graph = graph.copy()

    edges_to_remove = [(node1, node2) for node1, node2, data in filtered_graph.edges(data=True) if data["weight"] < threshold]
    filtered_graph.remove_edges_from(edges_to_remove)

    return filtered_graph

def invert_edge_weights(graph):
    inverted_graph = graph.copy()

    for edge in inverted_graph.edges(data=True):
        node1, node2, data = edge
        weight = data['weight']
        inverted_weight = 1 - weight
        inverted_graph[node1][node2]["weight"] = inverted_weight

    return inverted_graph

def calculate_and_save_betweenness_plot(graph, filename, politicians):
    betweenness = nx.betweenness_centrality(graph)

    politicians_ordered = sorted(betweenness.keys(), key=lambda x: betweenness[x])
    
    plt.figure(figsize=(10, 6)) 
    custom_labels = [f'{dep} ({politicians[dep]["Partido"]})' for dep in politicians_ordered]
    
    plt.bar(custom_labels, [betweenness[dep] for dep in politicians_ordered], color='blue')
    plt.xlabel('Deputados (Partido)')
    plt.ylabel('Betweenness')
    plt.title('Medida de Centralidade')
    plt.xticks(rotation='vertical', fontsize=5)
    plt.tight_layout()
    plt.savefig(filename)
    #plt.show()
    plt.close()

def generate_heatmap(graph, filename, politicians):
    politicians_list = list(graph.nodes)
    politicians_list.sort(key=lambda x: politicians[x]['Partido'])
    correlation_matrix = np.zeros((len(graph.nodes), len(graph.nodes)))
    

    for i, dep1 in enumerate(politicians_list):
        for j, dep2 in enumerate(politicians_list):
            if i == j:
                correlation_matrix[i, j] = 0
            elif graph.has_edge(dep1, dep2):
                correlation_matrix[i, j] = graph[dep1][dep2]['weight']

    plt.figure(figsize=(10, 10), dpi=300) 
    heatmap = plt.imshow(correlation_matrix, cmap='hot', interpolation='antialiased', aspect='auto')
    plt.colorbar(heatmap, label='Correlação')

    politicians_ordered = sorted(politicians_list)
    custom_labels = [f'{dep} ({politicians[dep]["Partido"]})' for dep in politicians_ordered]
    
    plt.title('Mapa de Calor - Correlação entre Deputados', fontsize=14)
    plt.xticks(range(len(politicians_list)), custom_labels, rotation=45, ha='right', fontsize=5)
    plt.yticks(range(len(politicians_list)), custom_labels, fontsize=5)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300) 
    #plt.show()
    plt.close()

def create_and_plot_graph(graph, filename, politicians):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph)
    subgraph = graph.subgraph([node for node in graph.nodes if graph.degree(node) > 0])

    unique_parties = set(politicians[node]["Partido"] for node in subgraph.nodes)
    legend_labels = []
    for party in unique_parties:
        color = get_party_color(party)
        legend_labels.append(plt.Line2D([0], [0], marker='o', color='w', label=f'{party}', markersize=10, markerfacecolor=color))

    plt.legend(handles=legend_labels, title="Partidos", loc='upper left', bbox_to_anchor=(1, 1))

    nx.draw(subgraph, pos, with_labels=True, font_size=10, node_size=100, font_color='black', node_color=[get_party_color(politicians[node]['Partido']) for node in subgraph.nodes])
    plt.title("Grafo de Relações de Votos entre Deputados", fontsize=14)
    plt.tight_layout()
    plt.savefig(filename)
    #plt.show()
    plt.close()

color_mapping = {}

def get_party_color(party):
    if party not in color_mapping:
        color_mapping[party] = '#{:06x}'.format(random.randint(0, 256**3 - 1))

    return color_mapping[party]