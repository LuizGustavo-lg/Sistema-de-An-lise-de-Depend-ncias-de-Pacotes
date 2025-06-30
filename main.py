import sys
from collections import defaultdict

def carregar_arquivo(arquivo_path='./entrada.txt'):
    """
    Carrega as dependências de um arquivo de texto e as representa como um grafo.

    Cada linha do arquivo deve ter o formato "pacote dependencia1 dependencia2 ...".
    O primeiro item é o pacote (nó de origem) e os seguintes são suas dependências
    (nós de destino).

    Args:
        arquivo_path (str): O caminho para o arquivo de entrada. O padrão é 'entrada.txt'.

    Returns:
        dict: Um dicionário que representa o grafo no formato de lista de adjacências.
              As chaves são os pacotes e os valores são listas de suas dependências.
    """
    grafo = defaultdict(list)
    with open(arquivo_path, 'r') as arquivo:
        for linha in arquivo:
            # Remove espaços extras e divide a linha em uma lista de pacotes
            linha = linha.strip().split(' ')
            # O primeiro pacote é a origem, o resto são suas dependências
            for depend in linha[1::]:
                grafo[linha[0]].append(depend)
                grafo[depend]

    return dict(grafo)


def tem_ciclo(grafo):
    """
    Verifica se existe um ciclo de dependências no grafo.

    Utiliza uma busca em profundidade (DFS). Um ciclo é detectado se, durante a
    travessia, um nó que já está na pilha de recursão atual é visitado novamente.

    Args:
        grafo (dict): O grafo de dependências.

    Returns:
        bool: True se um ciclo for encontrado, False caso contrário.
    """
    visitado = set()  # Nós que já foram visitados em qualquer travessia DFS
    recursao = set()  # Nós que estão na pilha da travessia DFS atual

    def dfs(no):
        visitado.add(no)
        recursao.add(no)

        # Para cada dependência (vizinho) do nó atual
        for vizinho in grafo.get(no, []):
            if vizinho not in visitado:
                # Se o vizinho ainda não foi visitado, continua a busca a partir dele
                if dfs(vizinho):
                    return True
            # Se o vizinho já foi visitado E está na pilha de recursão atual, um ciclo foi encontrado
            elif vizinho in recursao:
                return True

        recursao.remove(no)  # Remove o nó da pilha de recursão ao retroceder
        return False

    # Itera sobre todos os nós do grafo para garantir que componentes desconexos sejam verificados
    for no in grafo:
        if no not in visitado:
            if dfs(no):
                return True
            
    return False


def encontrar_cfc(grafo):
    """
    Encontra todos os Componentes Fortemente Conectados (CFCs) no grafo usando o algoritmo de Tarjan.

    Um CFC é um subgrafo onde cada nó é alcançável a partir de qualquer outro nó no mesmo subgrafo.
    CFCs com mais de um membro indicam a presença de ciclos.

    Args:
        grafo (dict): O grafo de dependências.

    Returns:
        list: Uma lista de listas, onde cada lista interna representa um CFC com mais de um membro.
    """
    index = 0
    indices = {}    # Armazena o tempo de descoberta (índice) de cada nó
    lowlinks = {}   # Armazena o low-link de cada nó (o menor índice alcançável)
    pilha = []
    na_pilha = set() # Nós que estão atualmente na pilha do algoritmo
    cfc = []

    def dfs(no):
        nonlocal index
        indices[no] = index
        lowlinks[no] = index
        index += 1
        pilha.append(no)
        na_pilha.add(no)

        for vizinho in grafo.get(no, []):
            if vizinho not in indices:
                # Se o vizinho não foi visitado, chama a DFS recursivamente
                dfs(vizinho)
                # Atualiza o low-link do nó atual com o low-link do vizinho
                lowlinks[no] = min(lowlinks[no], lowlinks[vizinho])
            elif vizinho in na_pilha:
                # Se o vizinho está na pilha, é uma aresta de retorno (back edge)
                lowlinks[no] = min(lowlinks[no], indices[vizinho])

        # Se o low-link de um nó é igual ao seu índice, ele é a raiz de um CFC
        if lowlinks[no] == indices[no]:
            componente = []
            while True:
                v = pilha.pop()
                na_pilha.remove(v)
                componente.append(v)
                if v == no:
                    break
            # Apenas componentes com mais de um nó são considerados ciclos relevantes
            if len(componente) > 1:
                cfc.append(componente)

    for no in grafo:
        if no not in indices:
            dfs(no)

    return cfc


def ordem_instalacao(grafo):
    """
    Determina uma ordem de instalação válida para os pacotes usando ordenação topológica.

    A ordenação topológica é uma ordenação linear dos nós de um grafo tal que para toda
    aresta direcionada (u, v), o nó u vem antes do nó v na ordenação. A implementação
    usa DFS. A ordem correta é o reverso da ordem de finalização da DFS.

    Args:
        grafo (dict): O grafo de dependências (deve ser um DAG para um resultado válido).

    Returns:
        list: Uma lista de pacotes na ordem em que devem ser instalados.
    """
    ordem = list()
    visitado = set()

    def dfs(no):
        visitado.add(no)
        for vizinho in grafo.get(no, []):
            if vizinho not in visitado:
                dfs(vizinho)
        
        # Adiciona o nó à lista após visitar todos os seus descendentes
        ordem.append(no)
    
    for no in grafo:
        if no not in visitado:
            dfs(no)

    # A ordem topológica é o inverso da ordem de finalização da DFS
    return ordem[::-1]


def encontrar_pacotes_criticos(grafo):
    """
    Identifica os pacotes mais críticos do sistema, baseando-se no número de dependentes.

    Um pacote é considerado crítico se ele for uma dependência para um grande número de
    outros pacotes (alto grau de entrada).

    Args:
        grafo (dict): O grafo de dependências.

    Returns:
        tuple: Uma tupla contendo:
               - list: A lista de pacotes mais críticos.
               - int: O número máximo de dependentes (maior grau de entrada).
               - dict: Um dicionário com o grau de entrada de cada pacote.
    """
    in_degree = defaultdict(int)

    # Inicializa o grau de entrada de todos os nós conhecidos como 0
    for no in grafo:
        in_degree[no] = in_degree.get(no, 0)
        for destino in grafo[no]:
             in_degree[destino] = in_degree.get(destino, 0)


    # Calcula o grau de entrada para cada pacote
    for origem in grafo:
        for destino in grafo[origem]:
            in_degree[destino] += 1

    if not in_degree:
        return [], 0, {}

    # Encontra o maior grau de entrada
    max_dependentes = max(in_degree.values())
    
    # Retorna todos os pacotes que têm o maior número de dependentes
    pacotes_criticos = [pacote for pacote, grau in in_degree.items() if grau == max_dependentes]

    return pacotes_criticos, max_dependentes, dict(in_degree)



def consultar_dependencias(grafo, pacote):
    """
    Encontra todas as dependências diretas e indiretas de um pacote específico.

    Realiza uma busca em profundidade (DFS) a partir do pacote especificado para
    encontrar todos os nós alcançáveis (suas dependências transitivas).

    Args:
        grafo (dict): O grafo de dependências.
        pacote (str): O nome do pacote a ser consultado.

    Returns:
        set: Um conjunto com todas as dependências do pacote.
    """
    visitado = set()

    def dfs(no):
        for vizinho in grafo.get(no, []):
            if vizinho not in visitado:
                visitado.add(vizinho)
                dfs(vizinho)

    dfs(pacote)
    return visitado


def simular_remocao(grafo, pacote_removido):
    """
    Simula a remoção de um pacote e identifica todos os outros pacotes que seriam afetados.

    Para fazer isso, o grafo é invertido (arestas de B->A se tornam A->B) e uma DFS é
    executada a partir do pacote removido para encontrar todos os que dependem dele.

    Args:
        grafo (dict): O grafo de dependências original.
        pacote_removido (str): O nome do pacote a ser "removido".

    Returns:
        set: Um conjunto de pacotes que dependem direta ou indiretamente do pacote removido.
    """
    # Inverte o grafo: se A depende de B, a nova aresta será B -> A
    grafo_invertido = defaultdict(list)
    for origem in grafo:
        for destino in grafo[origem]:
            grafo_invertido[destino].append(origem)

    # Usa DFS no grafo invertido para encontrar todos os que dependem do pacote removido
    afetados = set()
    def dfs(no):
        # Para cada pacote que depende do nó atual ('no')
        for dependente in grafo_invertido.get(no, []):
            if dependente not in afetados:
                afetados.add(dependente)
                dfs(dependente)

    dfs(pacote_removido)
    return afetados


def menu(ciclo):
    """
    Exibe o menu de opções para o usuário, dependendo da existencia de ciclo.
    
    Args:
        ciclo (bool): Existencia de cilio do grafo.
    """
    print("\n=== Sistema de Gerenciamento de Dependências ===")
    print("1.", "Listar componentes fortemente conectados (CFCs)" if ciclo else "Exibir ordem de instalação dos pacotes")
    print("2. Mostrar pacotes críticos")
    print("3. Consultar dependências de um pacote")
    print("4. Simular remoção de um pacote")
    print("0. Sair")

def main():
    """
    Função principal que executa o programa.

    Carrega o grafo, exibe o menu e processa a escolha do usuário em um loop
    até que a opção de sair seja selecionada.
    """
    arquivo = input("Digite o caminho do arquivo (ou pressione Enter para usar 'entrada.txt'): ") or "entrada.txt"
    
    try:
        grafo = carregar_arquivo(arquivo)
    except FileNotFoundError:
        print("Arquivo não encontrado.")
        sys.exit(1)

    ciclo = tem_ciclo(grafo)
    print("\nCiclo detectado?" , "Sim" if ciclo else "Não")

    while True:
        menu(ciclo)
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            if ciclo:
                cfcs = encontrar_cfc(grafo)
                if cfcs:
                    print("\nComponentes fortemente conectados:")
                    for i, grupo in enumerate(cfcs, 1):
                        print(f" CFC {i}: {grupo}")
                else:
                    print("\nNenhum ciclo detectado (sem CFCs com mais de um nó).")

            else:
                ordem = ordem_instalacao(grafo)
                print("\nOrdem de instalação sugerida:")
                # Imprime a ordem correta para instalação (dependências primeiro)
                print(" → ".join(ordem))

        elif escolha == '2':
            criticos, grau, _ = encontrar_pacotes_criticos(grafo)
            print(f"\nPacotes com maior número de dependentes ({grau}): {criticos}")

        elif escolha == '3':
            pacote = input("Digite o nome do pacote para consultar dependências: ")
            if pacote not in grafo:
                print("Pacote não encontrado no grafo.")
                continue
            deps = consultar_dependencias(grafo, pacote)
            if deps:
                print("Dependências (diretas e indiretas):", deps)
            else:
                print("Esse pacote não possui dependências.")

        elif escolha == '4':
            pacote = input("Digite o nome do pacote a ser removido: ")
            # Verifica se o pacote existe em algum lugar no grafo (como chave ou valor)
            todos_os_pacotes = set(grafo.keys())
            for dependencias in grafo.values():
                todos_os_pacotes.update(dependencias)
            if pacote not in todos_os_pacotes:
                print("Pacote não encontrado no grafo.")
                continue
            afetados = simular_remocao(grafo, pacote)
            if afetados:
                print("Pacotes afetados pela remoção:", afetados)
            else:
                print("Nenhum pacote será afetado.")

        elif escolha == '0':
            print("Saindo...")
            break

        else:
            print("Opção inválida.")


if __name__ == '__main__':
    main()