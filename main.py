import networkx as nx
import csv
from filtros import *

def main():
    print("O programa está iniciando...")
    
    try:
        year_input = input("Informe o ano a considerar (de 2002 a 2023): ")
        year = int(year_input)
        threshold = float(input("Informe o percentual mínimo de concordância (threshold) (ex. 0.9): "))
        parties = input("Informe os partidos a analisar, separados por espaço (ex. PT MDB PL): ").split()
        parties = [party.upper() for party in parties]
        
        print("Tentando ler o grafo")
        grafo = read_graph_file(year)
        print("Grafo lido")
        politicians = read_politicians_file(year)
        print("Políticos lidos")
        
        grafo_filtrado = apply_filters(grafo, politicians, parties)

        grafo_normalizado = normalize_weights(grafo_filtrado, politicians)
        grafo_final = apply_edge_threshold(grafo_normalizado, threshold)
        grafo_invertido = invert_edge_weights(grafo_final)

        betweenness_filename = f"betweenness_{year}_{'_'.join(parties)}.png"
        calculate_and_save_betweenness_plot(grafo_invertido, betweenness_filename, politicians)

        heatmap_filename = f"heatmap_{year}_{'_'.join(parties)}.png"
        generate_heatmap(grafo_normalizado, heatmap_filename, politicians)

        graph_plot_filename = f"graph_{year}_{'_'.join(parties)}.png"
        create_and_plot_graph(grafo_invertido, graph_plot_filename, politicians)
        
        print("Os plots foram salvos nos arquivos:")
        print(f"- {betweenness_filename}")
        print(f"- {heatmap_filename}")
        print(f"- {graph_plot_filename}")

    except ValueError:
        print("Ocorreu um erro ao ler os dados. Verifique se os dados estão formatados corretamente.")
    

if __name__ == "__main__":
    main()
