class Processo:
    def __init__(self, nome, surto_cpu, tempo_es, tempo_total_cpu, ordem, prioridade):
        self.nome = nome
        self.surto_cpu = surto_cpu
        self.tempo_es = tempo_es
        self.tempo_total_cpu = tempo_total_cpu
        self.ordem = ordem
        self.prioridade = prioridade
        self.creditos = prioridade
        self.tempo_restante_cpu = tempo_total_cpu
        self.tempo_restante_es = 0
        self.estado = 'Ready'
        self.credito_inicial = prioridade
        self.surto_atual = 0  # Adiciona o controle do surto atual

    def __repr__(self):
        return f"Processo({self.nome}, Estado: {self.estado}, Créditos: {self.creditos})"


class Escalonador:
    def __init__(self, processos):
        self.processos = processos
        self.tempo = 0

    def escalonar(self):
        while any(p.estado != 'Exit' for p in self.processos):
            processo_pronto = self.get_proximo_processo()

            if processo_pronto:
                self.executar_processo(processo_pronto)
            else:
                # Verifica se há processos prontos com créditos zerados
                processos_prontos = [p for p in self.processos if p.estado == 'Ready']
                if processos_prontos and all(p.creditos == 0 for p in processos_prontos):
                    self.atualizar_creditos()
                else:
                    # Nenhum processo pronto; o tempo avança até que processos sejam desbloqueados
                    pass

            self.atualizar_estados_bloqueados()
            self.tempo += 1

        print("Todos os processos foram finalizados.")

    def get_proximo_processo(self):
        # Seleciona os processos prontos (estado 'Ready') com créditos > 0
        processos_prontos = [p for p in self.processos if p.estado == 'Ready' and p.creditos > 0]
        if processos_prontos:
            # Ordena por número de créditos (descendente) e ordem (ascendente para desempate)
            return max(processos_prontos, key=lambda p: (p.creditos, -p.ordem))
        return None

    def executar_processo(self, processo):
        print(f"Executando processo {processo.nome} no tempo {self.tempo}")
        processo.creditos -= 1
        processo.tempo_restante_cpu -= 1

        # Verifica se o tempo total de CPU chegou a zero
        if processo.tempo_restante_cpu == 0:
            processo.estado = 'Exit'
            print(f"Processo {processo.nome} finalizado")
            return  # Encerra a execução deste método

        if processo.surto_cpu:
            # Incrementa o surto atual
            processo.surto_atual += 1

            # Verifica se o surto de CPU foi totalmente utilizado
            if processo.surto_atual >= processo.surto_cpu:
                processo.estado = 'Blocked'
                processo.tempo_restante_es = processo.tempo_es
                processo.surto_atual = 0  # Reseta o surto atual
                print(f"Processo {processo.nome} bloqueado por E/S")

    def atualizar_estados_bloqueados(self):
        # Desbloqueia processos bloqueados após o tempo de E/S acabar
        for processo in self.processos:
            if processo.estado == 'Blocked':
                processo.tempo_restante_es -= 1
                if processo.tempo_restante_es == 0:
                    processo.estado = 'Ready'
                    print(f"Processo {processo.nome} desbloqueado e pronto para executar")

    def atualizar_creditos(self):
        # Atualiza os créditos de todos os processos que não foram finalizados
        processos_prontos = [p for p in self.processos if p.estado == 'Ready']
        if processos_prontos and all(p.creditos == 0 for p in processos_prontos):
            print("Recalculando créditos...")
            for processo in self.processos:
                if processo.estado != 'Exit':  # Não recalcular créditos de processos finalizados
                    processo.creditos = processo.creditos // 2 + processo.prioridade
                    print(f"Processo {processo.nome} recebeu {processo.creditos} créditos")


# Exemplo de uso:
processos = [
    Processo('A', surto_cpu=2, tempo_es=5, tempo_total_cpu=6, ordem=1, prioridade=3),
    Processo('B', surto_cpu=3, tempo_es=10, tempo_total_cpu=6, ordem=2, prioridade=3),
    Processo('C', surto_cpu=None, tempo_es=None, tempo_total_cpu=14, ordem=3, prioridade=3),
    Processo('D', surto_cpu=None, tempo_es=None, tempo_total_cpu=10, ordem=4, prioridade=3)
]

escalonador = Escalonador(processos)
escalonador.escalonar()
