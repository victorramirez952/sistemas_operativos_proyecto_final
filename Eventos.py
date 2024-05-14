class Evento:
    def __init__(self, nombre):
        self.nombre = nombre
        self.clientes = set()
        self.id_clientes = [] # Se usa una lista, ya que un set no se puede formatear via JSON
    def agregar_cliente(id_cliente):
        self.clientes.add(id_cliente)
    def eliminar_cliente(id_cliente):
        self.clientes.remove(id_cliente)
    def mostrar_clientes():
        print("Clientes: ")
        for c in clientes:
            print(f"{c}, ")
    def get_id_clientes(self):
        return self.id_clientes
