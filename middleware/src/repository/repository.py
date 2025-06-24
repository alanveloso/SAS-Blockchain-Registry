# Exemplo de repositório simples em memória

class CBSDRepository:
    def __init__(self):
        self.cbsds = {}

    def add(self, cbsd_id, data):
        self.cbsds[cbsd_id] = data

    def get(self, cbsd_id):
        return self.cbsds.get(cbsd_id)

    def all(self):
        return self.cbsds.values() 