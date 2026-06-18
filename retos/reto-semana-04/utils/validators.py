def validar_sku(sku):
    return bool(str(sku).strip())

def validar_precio(precio):
    try:
        return float(precio) >= 0
    except:
        return False

def validar_stock(stock):
    try:
        return int(stock) >= 0
    except:
        return False

def validar_producto(datos):

    return (
        validar_sku(datos["sku"])
        and validar_precio(datos["precio"])
        and validar_stock(datos["stock"])
        and validar_stock(datos["stock_minimo"])
    )