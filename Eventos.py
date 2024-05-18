class Evento:
    def __init__(self, nombre):
        self.nombre = nombre
        self.clientes = set()
        self.id_clientes = [] # Se usa una lista, ya que un set no se puede formatear via JSON
    def agregar_cliente(self, id_cliente):
        self.clientes.add(id_cliente)
    def eliminar_cliente(self, id_cliente):
        if(id_cliente in self.id_clientes):
            self.id_clientes.remove(id_cliente)
            return True
        return False
    def mostrar_clientes():
        print("Clientes: ")
        for c in clientes:
            print(f"{c}, ")
    def get_id_clientes(self):
        return self.id_clientes
