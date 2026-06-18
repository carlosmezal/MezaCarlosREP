class Producto:

    def __init__(self, sku, nombre, categoria, precio, stock, stock_minimo):
        self.sku = sku
        self.nombre = nombre
        self.categoria = categoria
        self.precio = float(precio)
        self.stock = int(stock)
        self.stock_minimo = int(stock_minimo)

    def necesita_reorden(self):
        return self.stock < self.stock_minimo

    def unidades_faltantes(self):
        if self.necesita_reorden():
            return self.stock_minimo - self.stock
        return 0

    def valor_inventario(self):
        return self.precio * self.stock

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

    def __repr__(self):
        return f"Producto({self.sku}, {self.nombre})"