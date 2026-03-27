#!/usr/bin/env python3
"""
Generador de Examen Parcial 1 - Programación para Ciencia de Datos
IPN Febrero-Julio 2026 | Semanas 1-4

Genera exámenes únicos por matrícula con 12 variantes de dominio,
datos personalizados y umbrales perturbados.

Uso:
    python generar_examen.py <matricula>
    python generar_examen.py --lote matriculas.txt
    python generar_examen.py --lote matriculas.txt --fecha-limite 2026-04-10
"""

import hashlib
import random
import os
import sys
from pathlib import Path


# ================================================================
# UTILIDADES
# ================================================================

def matricula_to_seed(matricula):
    """Convierte matrícula en semilla numérica determinista."""
    h = hashlib.sha256(matricula.strip().upper().encode()).hexdigest()
    return int(h[:8], 16)


def convertir(valor, offset, factor):
    """Conversión lineal: resultado = (valor + offset) * factor."""
    return (valor + offset) * factor


def calcular_hash_datos(contenido):
    """Calcula SHA-256 del contenido de los datos de entrada."""
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def clasificar(valor, clases):
    """Clasifica un valor según rangos [(nombre, min_inc, max_exc), ...]."""
    for nombre, vmin, vmax in clases:
        if vmin is None and valor < vmax:
            return nombre
        if vmax is None and valor >= vmin:
            return nombre
        if vmin is not None and vmax is not None and vmin <= valor < vmax:
            return nombre
    return clases[-1][0]


def perturbar_umbrales(clases_base, rng, magnitud):
    """Perturba umbrales internos manteniendo orden y continuidad."""
    # Extraer umbrales internos (los que no son None)
    internos = []
    for i, (_, _, vmax) in enumerate(clases_base):
        if vmax is not None and i < len(clases_base) - 1:
            internos.append(vmax)

    # Perturbar cada umbral
    perturbados = [round(u + rng.uniform(-magnitud, magnitud), 2)
                   for u in internos]
    perturbados.sort()

    # Reconstruir clases con umbrales perturbados
    nuevas = []
    for i, (nombre, _, _) in enumerate(clases_base):
        if i == 0:
            nuevas.append((nombre, None, perturbados[0]))
        elif i == len(clases_base) - 1:
            nuevas.append((nombre, perturbados[-1], None))
        else:
            nuevas.append((nombre, perturbados[i - 1], perturbados[i]))
    return nuevas


def formato_rango(vmin, vmax, dec):
    """Formatea un rango para mostrar en el enunciado."""
    if vmin is None:
        return f"< {vmax:.{dec}f}"
    if vmax is None:
        return f">= {vmin:.{dec}f}"
    return f"{vmin:.{dec}f} - {vmax:.{dec}f}"


# ================================================================
# DATOS COMPARTIDOS
# ================================================================

PERSONAS = [
    "Ana García", "Luis Torres", "María López", "Carlos Hernández",
    "Sofía Martínez", "Diego Rodríguez", "Valentina Flores", "Andrés Morales",
    "Isabella Ramírez", "Miguel Sánchez", "Camila Díaz", "Javier Cruz",
    "Lucía Reyes", "Fernando Ortiz", "Paula Vargas", "Ricardo Mendoza",
    "Daniela Castillo", "Alejandro Ruiz", "Gabriela Peña", "Roberto Jiménez",
    "Natalia Guerrero", "Eduardo Silva", "Mariana Rosas", "Héctor Aguilar",
    "Valeria Ibarra", "Óscar Delgado", "Regina Navarro", "Emilio Fuentes",
    "Renata Campos", "Sergio Vega", "Andrea Ríos", "Pablo Contreras",
    "Jimena Herrera", "Manuel Estrada", "Fernanda Lara", "Tomás Medina",
    "Catalina Guzmán", "Raúl Domínguez", "Elena Salazar", "Iván Molina",
    "Adriana Pacheco", "Jorge Montes", "Mónica Espinoza", "Felipe Sandoval",
    "Lorena Cervantes", "Arturo Rangel", "Diana Vázquez", "Ernesto Rojas",
]

PRODUCTOS_ELECTRONICOS = [
    "Samsung Galaxy S24", "iPhone 15 Pro", "MacBook Air M3", "Dell XPS 15",
    "Sony WH-1000XM5", "iPad Pro 12.9", "Nintendo Switch OLED", "LG OLED C3",
    "Bose QC45", "Canon EOS R6", "Lenovo ThinkPad X1", "HP Spectre x360",
    "Apple Watch Ultra", "Sony PS5", "Xbox Series X", "AirPods Pro 2",
    "Samsung Tab S9", "Google Pixel 8", "Asus ROG Phone", "Huawei MateBook",
    "JBL Flip 6", "Razer Blade 16", "Microsoft Surface Pro", "Fitbit Sense 2",
    "GoPro Hero 12", "Kindle Paperwhite", "DJI Mini 3 Pro", "Garmin Fenix 7",
]

RUTAS_VIAJE = [
    "CDMX-Cancún", "Guadalajara-Miami", "Monterrey-Madrid", "Puebla-NY",
    "Tijuana-Tokyo", "Mérida-París", "Oaxaca-Roma", "León-Londres",
    "Querétaro-Berlín", "Chihuahua-Toronto", "Veracruz-La Habana",
    "Acapulco-Lima", "SLP-Buenos Aires", "Toluca-Bogotá", "Morelia-Santiago",
    "Durango-São Paulo", "Aguascalientes-Chicago", "Hermosillo-Vancouver",
    "Mazatlán-Sydney", "Villahermosa-Amsterdam", "Tuxtla-Seúl",
    "Campeche-Bangkok", "Tepic-Dubái", "Colima-Mumbai",
]

PROPIEDADES = [
    "Depto Roma Norte", "Casa Coyoacán", "Loft Condesa", "Depto Polanco",
    "Casa Satélite", "Depto Santa Fe", "Casa Del Valle", "Penthouse Reforma",
    "Depto Nápoles", "Casa Tlalpan", "Depto Juárez", "Casa Pedregal",
    "Loft San Ángel", "Depto Escandón", "Casa Xochimilco", "Depto Anzures",
    "Casa Lindavista", "Depto Insurgentes", "Casa Coapa", "Loft Centro",
    "Depto Mixcoac", "Casa Azcapotzalco", "Depto Tabacalera", "Casa Iztacalco",
]

PRODUCTOS_PAN = [
    "Concha Chocolate", "Cuerno Mantequilla", "Polvorón Rosa", "Oreja Grande",
    "Beso Fresa", "Dona Glaseada", "Churro Relleno", "Cochinito Piloncillo",
    "Empanada Piña", "Garibaldi Azúcar", "Moño Canela", "Piedra Nuez",
    "Campechana", "Bigote Chocolate", "Banderilla Vainilla", "Volcán Cajeta",
    "Rebanada Naranja", "Cuernito Jamón", "Trenza Azúcar", "Hongo Chocolate",
    "Corbata Glas", "Novia Mermelada", "Reja Canela", "Panqué Pasas",
]

PLANTAS = [
    "Rosa Roja", "Orquídea Blanca", "Lavanda", "Girasol", "Jazmín",
    "Bugambilia", "Helecho Boston", "Suculenta Echeveria", "Cactus San Pedro",
    "Menta", "Albahaca", "Romero", "Potus Dorado", "Monstera Deliciosa",
    "Ficus Benjamina", "Palma Areca", "Hortensia Azul", "Nochebuena",
    "Begonia Rex", "Calathea Ornata", "Pilea Peperomioides", "Dracaena",
    "Aloe Vera", "Bambú de la Suerte",
]

PRODUCTOS_BODEGA = [
    "Aceite Oliva", "Arroz Integral", "Harina Trigo", "Leche Entera",
    "Vinagre Manzana", "Miel Abeja", "Salsa Soya", "Jugo Naranja",
    "Agua Mineral", "Refresco Cola", "Cerveza Artesanal", "Vino Tinto",
    "Detergente Líquido", "Suavizante Ropa", "Blanqueador", "Limpiador Multi",
    "Shampoo Natural", "Jabón Líquido", "Gel Antibacterial", "Pintura Vinílica",
    "Aceite Motor", "Anticongelante", "Lubricante Industrial", "Solvente",
]

TELAS = [
    "Algodón Egipcio", "Seda Natural", "Lino Belga", "Mezclilla Índigo",
    "Terciopelo Rojo", "Organza Blanca", "Satén Dorado", "Encaje Francés",
    "Franela Escocesa", "Popelina Azul", "Tul Ilusión", "Chiffon Rosa",
    "Piqué Blanco", "Gabardina Beige", "Crepé Negro", "Oxford Gris",
    "Manta Cruda", "Lona Industrial", "Nylon Reforzado", "Polar Fleece",
    "Jersey Algodón", "Tencel Verde", "Bambú Natural", "Modal Suave",
]

VEHICULOS = [
    "Toyota Corolla 2023", "Honda Civic 2022", "Nissan Sentra 2024",
    "VW Jetta 2023", "Mazda 3 2024", "Chevrolet Aveo 2022",
    "Ford Escape 2023", "Hyundai Tucson 2024", "KIA Sportage 2023",
    "Jeep Wrangler 2022", "Toyota RAV4 2024", "Honda CR-V 2023",
    "BMW Serie 3 2024", "Mercedes C300 2023", "Audi A4 2024",
    "Nissan Frontier 2023", "Toyota Hilux 2024", "Ford Ranger 2023",
    "Chevrolet Silverado 2024", "RAM 1500 2023", "VW Tiguan 2024",
    "Mazda CX-5 2023", "Subaru Outback 2024", "Suzuki Vitara 2023",
]


# ================================================================
# DEFINICIÓN DE VARIANTES (12)
# ================================================================

VARIANTES = [
    # ---- 0: Hospital ----
    {
        "id": "hospital",
        "titulo": "Sistema de Monitoreo Hospitalario",
        "contexto": (
            "El Hospital Central de la Ciudad de México te ha contratado para "
            "desarrollar un sistema que procese los registros de temperatura de "
            "sus pacientes. El hospital recibe datos de múltiples áreas, algunos "
            "en Fahrenheit (equipos importados) y otros en Celsius. Necesitan "
            "unificar mediciones, clasificar pacientes según estado térmico y "
            "generar reportes por área hospitalaria."
        ),
        "entidad": "Paciente",
        "prefijo_id": "PAC-",
        "archivo": "registros_pacientes.csv",
        "cols": ["id_paciente", "nombre", "temperatura", "unidad", "area"],
        "cols_desc": [
            "Identificador único", "Nombre completo",
            "Valor de temperatura", "Unidad (F o C)", "Área hospitalaria",
        ],
        "col_valor_out": "temperatura_celsius",
        "col_clase_out": "estado_termico",
        "ua": "F", "ub": "C",
        "nombre_ua": "Fahrenheit", "nombre_ub": "Celsius",
        "formula_txt": "C = (F - 32) × 5 / 9",
        "formula_py": "celsius = (fahrenheit - 32) * 5 / 9",
        "offset": -32, "factor": 5 / 9,
        "items": None,
        "grupos": ["Urgencias", "Pediatría", "Cardiología",
                   "Medicina Interna", "Cirugía", "Traumatología",
                   "Neurología", "Oncología"],
        "rango_a": (95.0, 107.0), "rango_b": (35.0, 42.0),
        "clases_base": [
            ("Hipotermia", None, 35.0),
            ("Normal", 35.0, 37.5),
            ("Febrícula", 37.5, 38.0),
            ("Fiebre", 38.0, 39.5),
            ("Fiebre alta", 39.5, None),
        ],
        "decimales": 1, "perturb_mag": 0.3,
    },
    # ---- 1: Tienda de electrónica ----
    {
        "id": "electronica",
        "titulo": "Sistema de Inventario de Electrónica",
        "contexto": (
            "Una cadena de tiendas de electrónica importa productos de EE.UU. "
            "y necesita un sistema para convertir precios de dólares a pesos "
            "mexicanos, clasificar productos por rango de precio y generar "
            "reportes por categoría. Los datos llegan mezclados: algunos precios "
            "ya están en MXN y otros en USD."
        ),
        "entidad": "Producto",
        "prefijo_id": "PROD-",
        "archivo": "inventario_productos.csv",
        "cols": ["sku", "nombre", "precio", "moneda", "categoria"],
        "cols_desc": [
            "Código de producto", "Nombre del producto",
            "Precio", "Moneda (USD o MXN)", "Categoría",
        ],
        "col_valor_out": "precio_mxn",
        "col_clase_out": "rango_precio",
        "ua": "USD", "ub": "MXN",
        "nombre_ua": "Dólares (USD)", "nombre_ub": "Pesos (MXN)",
        "formula_txt": "MXN = USD × 17.50",
        "formula_py": "mxn = usd * 17.50",
        "offset": 0, "factor": 17.50,
        "items": PRODUCTOS_ELECTRONICOS,
        "grupos": ["Audio", "Video", "Cómputo", "Telefonía",
                   "Gaming", "Fotografía", "Wearables", "Accesorios"],
        "rango_a": (15.0, 2500.0), "rango_b": (200.0, 45000.0),
        "clases_base": [
            ("Económico", None, 1000.0),
            ("Accesible", 1000.0, 5000.0),
            ("Medio", 5000.0, 15000.0),
            ("Premium", 15000.0, 30000.0),
            ("Lujo", 30000.0, None),
        ],
        "decimales": 2, "perturb_mag": 500.0,
    },
    # ---- 2: Gimnasio ----
    {
        "id": "gimnasio",
        "titulo": "Sistema de Registro de Gimnasio",
        "contexto": (
            "Un gimnasio con sede en la frontera norte recibe atletas de "
            "México y EE.UU. Los registros de peso llegan mezclados en libras "
            "y kilogramos. Necesitan un sistema que unifique a kg, clasifique "
            "por rango de peso y genere reportes por disciplina deportiva."
        ),
        "entidad": "Atleta",
        "prefijo_id": "ATL-",
        "archivo": "registros_atletas.csv",
        "cols": ["id_atleta", "nombre", "peso", "unidad", "deporte"],
        "cols_desc": [
            "Identificador del atleta", "Nombre completo",
            "Peso corporal", "Unidad (lb o kg)", "Disciplina deportiva",
        ],
        "col_valor_out": "peso_kg",
        "col_clase_out": "categoria_peso",
        "ua": "lb", "ub": "kg",
        "nombre_ua": "Libras (lb)", "nombre_ub": "Kilogramos (kg)",
        "formula_txt": "kg = lb × 0.4536",
        "formula_py": "kg = lb * 0.4536",
        "offset": 0, "factor": 0.4536,
        "items": None,
        "grupos": ["Natación", "Box", "Pesas", "CrossFit",
                   "Artes Marciales", "Atletismo", "Ciclismo", "Yoga"],
        "rango_a": (100.0, 280.0), "rango_b": (45.0, 130.0),
        "clases_base": [
            ("Ligero", None, 55.0),
            ("Medio", 55.0, 75.0),
            ("Pesado", 75.0, 95.0),
            ("Superpesado", 95.0, 115.0),
            ("Ultra", 115.0, None),
        ],
        "decimales": 1, "perturb_mag": 3.0,
    },
    # ---- 3: Agencia de viajes ----
    {
        "id": "viajes",
        "titulo": "Sistema de Análisis de Rutas de Viaje",
        "contexto": (
            "Una agencia de viajes internacional maneja rutas cuyas distancias "
            "están registradas en millas (proveedores americanos) y kilómetros "
            "(proveedores europeos). Necesitan unificar a km, clasificar rutas "
            "por distancia y generar reportes por región de destino."
        ),
        "entidad": "Ruta",
        "prefijo_id": "RUT-",
        "archivo": "rutas_viaje.csv",
        "cols": ["id_ruta", "nombre", "distancia", "unidad", "region"],
        "cols_desc": [
            "Código de ruta", "Origen-Destino",
            "Distancia", "Unidad (mi o km)", "Región de destino",
        ],
        "col_valor_out": "distancia_km",
        "col_clase_out": "tipo_ruta",
        "ua": "mi", "ub": "km",
        "nombre_ua": "Millas (mi)", "nombre_ub": "Kilómetros (km)",
        "formula_txt": "km = mi × 1.6093",
        "formula_py": "km = mi * 1.6093",
        "offset": 0, "factor": 1.6093,
        "items": RUTAS_VIAJE,
        "grupos": ["Norteamérica", "Europa", "Sudamérica", "Asia",
                   "Caribe", "Centroamérica", "Oceanía", "África"],
        "rango_a": (100.0, 8000.0), "rango_b": (150.0, 13000.0),
        "clases_base": [
            ("Corta", None, 500.0),
            ("Media", 500.0, 2000.0),
            ("Larga", 2000.0, 5000.0),
            ("Muy larga", 5000.0, 10000.0),
            ("Intercontinental", 10000.0, None),
        ],
        "decimales": 1, "perturb_mag": 200.0,
    },
    # ---- 4: Laboratorio ----
    {
        "id": "laboratorio",
        "titulo": "Sistema de Control de Muestras de Laboratorio",
        "contexto": (
            "Un laboratorio de análisis clínicos recibe muestras con volúmenes "
            "registrados en onzas líquidas (equipos importados) y mililitros "
            "(equipos nacionales). Necesitan unificar a ml, clasificar muestras "
            "por tamaño y generar reportes por tipo de análisis."
        ),
        "entidad": "Muestra",
        "prefijo_id": "MX-",
        "archivo": "muestras_lab.csv",
        "cols": ["id_muestra", "paciente", "volumen", "unidad", "tipo_analisis"],
        "cols_desc": [
            "Código de muestra", "Nombre del paciente",
            "Volumen de la muestra", "Unidad (fl_oz o ml)", "Tipo de análisis",
        ],
        "col_valor_out": "volumen_ml",
        "col_clase_out": "tamano_muestra",
        "ua": "fl_oz", "ub": "ml",
        "nombre_ua": "Onzas líquidas (fl_oz)", "nombre_ub": "Mililitros (ml)",
        "formula_txt": "ml = fl_oz × 29.5735",
        "formula_py": "ml = fl_oz * 29.5735",
        "offset": 0, "factor": 29.5735,
        "items": None,
        "grupos": ["Hematología", "Química Sanguínea", "Uroanálisis",
                   "Microbiología", "Inmunología", "Hormonas",
                   "Coagulación", "Serología"],
        "rango_a": (0.1, 20.0), "rango_b": (3.0, 600.0),
        "clases_base": [
            ("Micro", None, 10.0),
            ("Pequeña", 10.0, 50.0),
            ("Mediana", 50.0, 150.0),
            ("Grande", 150.0, 350.0),
            ("Extra grande", 350.0, None),
        ],
        "decimales": 1, "perturb_mag": 5.0,
    },
    # ---- 5: Inmobiliaria ----
    {
        "id": "inmobiliaria",
        "titulo": "Sistema de Catálogo Inmobiliario",
        "contexto": (
            "Una inmobiliaria internacional maneja propiedades con áreas en "
            "pies cuadrados (listados de EE.UU.) y metros cuadrados (listados "
            "nacionales). Necesitan unificar a m², clasificar propiedades por "
            "tamaño y generar reportes por zona de la ciudad."
        ),
        "entidad": "Propiedad",
        "prefijo_id": "INM-",
        "archivo": "catalogo_propiedades.csv",
        "cols": ["id_propiedad", "nombre", "area", "unidad", "zona"],
        "cols_desc": [
            "Código de propiedad", "Nombre/descripción",
            "Área", "Unidad (ft2 o m2)", "Zona de la ciudad",
        ],
        "col_valor_out": "area_m2",
        "col_clase_out": "tipo_propiedad",
        "ua": "ft2", "ub": "m2",
        "nombre_ua": "Pies cuadrados (ft²)", "nombre_ub": "Metros cuadrados (m²)",
        "formula_txt": "m² = ft² × 0.0929",
        "formula_py": "m2 = ft2 * 0.0929",
        "offset": 0, "factor": 0.0929,
        "items": PROPIEDADES,
        "grupos": ["Norte", "Sur", "Centro", "Oriente",
                   "Poniente", "Periférico", "Suburbio", "Centro Histórico"],
        "rango_a": (300.0, 5000.0), "rango_b": (28.0, 465.0),
        "clases_base": [
            ("Compacto", None, 50.0),
            ("Estándar", 50.0, 100.0),
            ("Amplio", 100.0, 180.0),
            ("Premium", 180.0, 300.0),
            ("Mansión", 300.0, None),
        ],
        "decimales": 1, "perturb_mag": 10.0,
    },
    # ---- 6: Panadería ----
    {
        "id": "panaderia",
        "titulo": "Sistema de Control de Panadería",
        "contexto": (
            "Una panadería artesanal exporta a EE.UU. y maneja pesos en onzas "
            "(para clientes americanos) y gramos (producción local). Necesitan "
            "unificar a gramos, clasificar productos por tamaño y generar "
            "reportes por tipo de pan."
        ),
        "entidad": "PanProducto",
        "prefijo_id": "PAN-",
        "archivo": "produccion_panaderia.csv",
        "cols": ["id_producto", "nombre", "peso", "unidad", "tipo"],
        "cols_desc": [
            "Código de producto", "Nombre del pan",
            "Peso", "Unidad (oz o g)", "Tipo de pan",
        ],
        "col_valor_out": "peso_gramos",
        "col_clase_out": "tamano",
        "ua": "oz", "ub": "g",
        "nombre_ua": "Onzas (oz)", "nombre_ub": "Gramos (g)",
        "formula_txt": "g = oz × 28.3495",
        "formula_py": "gramos = oz * 28.3495",
        "offset": 0, "factor": 28.3495,
        "items": PRODUCTOS_PAN,
        "grupos": ["Pan dulce", "Pan salado", "Repostería",
                   "Galletas", "Pasteles", "Hojaldres",
                   "Pan integral", "Especialidades"],
        "rango_a": (1.0, 32.0), "rango_b": (25.0, 900.0),
        "clases_base": [
            ("Miniatura", None, 50.0),
            ("Chico", 50.0, 150.0),
            ("Mediano", 150.0, 350.0),
            ("Grande", 350.0, 600.0),
            ("Jumbo", 600.0, None),
        ],
        "decimales": 1, "perturb_mag": 15.0,
    },
    # ---- 7: Vivero ----
    {
        "id": "vivero",
        "titulo": "Sistema de Inventario de Vivero",
        "contexto": (
            "Un vivero que importa plantas de EE.UU. recibe fichas con alturas "
            "en pulgadas y en centímetros. Necesitan unificar a cm, clasificar "
            "plantas por etapa de crecimiento y generar reportes por tipo de "
            "planta."
        ),
        "entidad": "Planta",
        "prefijo_id": "PLT-",
        "archivo": "inventario_plantas.csv",
        "cols": ["id_planta", "nombre", "altura", "unidad", "tipo"],
        "cols_desc": [
            "Código de planta", "Nombre de la especie",
            "Altura", "Unidad (in o cm)", "Tipo de planta",
        ],
        "col_valor_out": "altura_cm",
        "col_clase_out": "etapa_crecimiento",
        "ua": "in", "ub": "cm",
        "nombre_ua": "Pulgadas (in)", "nombre_ub": "Centímetros (cm)",
        "formula_txt": "cm = in × 2.54",
        "formula_py": "cm = pulgadas * 2.54",
        "offset": 0, "factor": 2.54,
        "items": PLANTAS,
        "grupos": ["Frutal", "Ornamental", "Medicinal", "Cactácea",
                   "Tropical", "Aromática", "Suculenta", "Trepadora"],
        "rango_a": (2.0, 80.0), "rango_b": (5.0, 200.0),
        "clases_base": [
            ("Brote", None, 15.0),
            ("Pequeña", 15.0, 40.0),
            ("Mediana", 40.0, 80.0),
            ("Alta", 80.0, 150.0),
            ("Gigante", 150.0, None),
        ],
        "decimales": 1, "perturb_mag": 5.0,
    },
    # ---- 8: Estación meteorológica ----
    {
        "id": "meteorologia",
        "titulo": "Sistema de Monitoreo Meteorológico",
        "contexto": (
            "Una red de estaciones meteorológicas en la frontera usa sensores "
            "que reportan presión atmosférica en pulgadas de mercurio (inHg) y "
            "hectopascales (hPa). Necesitan unificar a hPa, clasificar lecturas "
            "por nivel de presión y generar reportes por estación del año."
        ),
        "entidad": "Lectura",
        "prefijo_id": "LEC-",
        "archivo": "lecturas_presion.csv",
        "cols": ["id_lectura", "estacion", "presion", "unidad", "temporada"],
        "cols_desc": [
            "Código de lectura", "Nombre de la estación",
            "Presión atmosférica", "Unidad (inHg o hPa)", "Temporada del año",
        ],
        "col_valor_out": "presion_hpa",
        "col_clase_out": "nivel_presion",
        "ua": "inHg", "ub": "hPa",
        "nombre_ua": "Pulgadas de mercurio (inHg)",
        "nombre_ub": "Hectopascales (hPa)",
        "formula_txt": "hPa = inHg × 33.8639",
        "formula_py": "hpa = inhg * 33.8639",
        "offset": 0, "factor": 33.8639,
        "items": [
            "Est. Norte", "Est. Sur", "Est. Centro", "Est. Oriente",
            "Est. Poniente", "Est. Altiplano", "Est. Costa", "Est. Sierra",
            "Est. Valle", "Est. Desierto", "Est. Laguna", "Est. Río",
            "Est. Montaña", "Est. Planicie", "Est. Bosque", "Est. Pradera",
            "Est. Cañón", "Est. Meseta", "Est. Volcán", "Est. Bahía",
            "Est. Istmo", "Est. Península", "Est. Selva", "Est. Manglar",
        ],
        "grupos": ["Primavera", "Verano", "Otoño", "Invierno",
                   "Transición Primavera-Verano", "Transición Otoño-Invierno",
                   "Canícula", "Temporada de lluvias"],
        "rango_a": (28.5, 31.0), "rango_b": (965.0, 1050.0),
        "clases_base": [
            ("Muy baja", None, 1000.0),
            ("Baja", 1000.0, 1010.0),
            ("Normal", 1010.0, 1020.0),
            ("Alta", 1020.0, 1030.0),
            ("Muy alta", 1030.0, None),
        ],
        "decimales": 1, "perturb_mag": 3.0,
    },
    # ---- 9: Bodega de líquidos ----
    {
        "id": "bodega",
        "titulo": "Sistema de Control de Bodega de Líquidos",
        "contexto": (
            "Una bodega de distribución maneja contenedores con capacidades en "
            "galones (proveedores de EE.UU.) y litros (proveedores nacionales). "
            "Necesitan unificar a litros, clasificar contenedores por capacidad "
            "y generar reportes por tipo de producto."
        ),
        "entidad": "Contenedor",
        "prefijo_id": "CON-",
        "archivo": "inventario_bodega.csv",
        "cols": ["id_contenedor", "producto", "capacidad", "unidad", "tipo_producto"],
        "cols_desc": [
            "Código del contenedor", "Nombre del producto",
            "Capacidad", "Unidad (gal o L)", "Tipo de producto",
        ],
        "col_valor_out": "capacidad_litros",
        "col_clase_out": "tamano_contenedor",
        "ua": "gal", "ub": "L",
        "nombre_ua": "Galones (gal)", "nombre_ub": "Litros (L)",
        "formula_txt": "L = gal × 3.7854",
        "formula_py": "litros = gal * 3.7854",
        "offset": 0, "factor": 3.7854,
        "items": PRODUCTOS_BODEGA,
        "grupos": ["Alimentos", "Bebidas", "Limpieza", "Químicos",
                   "Cosméticos", "Pinturas", "Automotriz", "Industrial"],
        "rango_a": (0.25, 55.0), "rango_b": (1.0, 210.0),
        "clases_base": [
            ("Mini", None, 5.0),
            ("Pequeño", 5.0, 20.0),
            ("Mediano", 20.0, 60.0),
            ("Grande", 60.0, 150.0),
            ("Industrial", 150.0, None),
        ],
        "decimales": 1, "perturb_mag": 3.0,
    },
    # ---- 10: Taller textil ----
    {
        "id": "textil",
        "titulo": "Sistema de Inventario Textil",
        "contexto": (
            "Un taller textil importa telas de EE.UU. con longitudes en yardas "
            "y también compra telas nacionales medidas en metros. Necesitan "
            "unificar a metros, clasificar cortes por tamaño y generar reportes "
            "por tipo de tela."
        ),
        "entidad": "CorteTela",
        "prefijo_id": "TEL-",
        "archivo": "inventario_telas.csv",
        "cols": ["id_corte", "nombre", "longitud", "unidad", "tipo_tela"],
        "cols_desc": [
            "Código de corte", "Nombre de la tela",
            "Longitud", "Unidad (yd o m)", "Tipo de tela",
        ],
        "col_valor_out": "longitud_metros",
        "col_clase_out": "tipo_corte",
        "ua": "yd", "ub": "m",
        "nombre_ua": "Yardas (yd)", "nombre_ub": "Metros (m)",
        "formula_txt": "m = yd × 0.9144",
        "formula_py": "metros = yd * 0.9144",
        "offset": 0, "factor": 0.9144,
        "items": TELAS,
        "grupos": ["Confección", "Tapicería", "Industrial", "Moda",
                   "Deportiva", "Decoración", "Uniformes", "Lencería"],
        "rango_a": (0.5, 60.0), "rango_b": (0.5, 55.0),
        "clases_base": [
            ("Retazo", None, 1.0),
            ("Corte", 1.0, 5.0),
            ("Pieza", 5.0, 15.0),
            ("Rollo", 15.0, 40.0),
            ("Bulto", 40.0, None),
        ],
        "decimales": 2, "perturb_mag": 0.5,
    },
    # ---- 11: Taller mecánico ----
    {
        "id": "mecanico",
        "titulo": "Sistema de Servicio de Taller Mecánico",
        "contexto": (
            "Un taller mecánico en zona fronteriza revisa neumáticos de "
            "vehículos mexicanos y americanos. Las presiones se registran en "
            "PSI (sistema americano) y bar (sistema métrico). Necesitan "
            "unificar a bar, clasificar el estado de presión y generar "
            "reportes por tipo de vehículo."
        ),
        "entidad": "Revision",
        "prefijo_id": "REV-",
        "archivo": "revisiones_neumaticos.csv",
        "cols": ["id_revision", "vehiculo", "presion", "unidad", "tipo_vehiculo"],
        "cols_desc": [
            "Código de revisión", "Vehículo",
            "Presión del neumático", "Unidad (PSI o bar)",
            "Tipo de vehículo",
        ],
        "col_valor_out": "presion_bar",
        "col_clase_out": "estado_presion",
        "ua": "PSI", "ub": "bar",
        "nombre_ua": "PSI", "nombre_ub": "Bar",
        "formula_txt": "bar = PSI × 0.0689",
        "formula_py": "bar_val = psi * 0.0689",
        "offset": 0, "factor": 0.0689,
        "items": VEHICULOS,
        "grupos": ["Sedán", "SUV", "Pickup", "Deportivo",
                   "Camioneta", "Compacto", "Minivan", "Lujo"],
        "rango_a": (18.0, 55.0), "rango_b": (1.2, 3.8),
        "clases_base": [
            ("Muy baja", None, 1.5),
            ("Baja", 1.5, 2.0),
            ("Normal", 2.0, 2.8),
            ("Alta", 2.8, 3.5),
            ("Peligrosa", 3.5, None),
        ],
        "decimales": 2, "perturb_mag": 0.15,
    },
]


# ================================================================
# GENERACIÓN DE DATOS
# ================================================================

def generar_datos(variante, rng, n=1000, pct_error=0.10):
    """Genera n filas de datos CSV con un porcentaje de errores."""
    cols = variante["cols"]
    items = variante.get("items") or PERSONAS
    grupos = variante["grupos"]
    prefijo = variante["prefijo_id"]
    rango_a = variante["rango_a"]
    rango_b = variante["rango_b"]
    ua = variante["ua"]
    ub = variante["ub"]

    header = ",".join(cols)
    lineas = [header]

    for i in range(n):
        id_val = f"{prefijo}{i + 1:04d}"
        nombre = rng.choice(items)

        # Decidir unidad (50/50)
        if rng.random() < 0.5:
            valor = round(rng.uniform(*rango_a), 2)
            unidad = ua
        else:
            valor = round(rng.uniform(*rango_b), 2)
            unidad = ub

        grupo = rng.choice(grupos)
        fila = [id_val, nombre, str(valor), unidad, grupo]

        # Introducir error con probabilidad pct_error
        if rng.random() < pct_error:
            tipo_error = rng.choice([
                "valor_invalido", "unidad_invalida",
                "columnas_faltantes", "columnas_extra", "linea_vacia",
            ])
            if tipo_error == "valor_invalido":
                fila[2] = rng.choice(["N/A", "error", "--", "null", "", "#REF!"])
            elif tipo_error == "unidad_invalida":
                fila[3] = rng.choice(["X", "?", "K", "", "ZZ"])
            elif tipo_error == "columnas_faltantes":
                fila = fila[:rng.randint(2, len(fila) - 1)]
            elif tipo_error == "columnas_extra":
                fila.append("dato_extra")
                fila.append(str(rng.randint(1, 99)))
            elif tipo_error == "linea_vacia":
                lineas.append("")
                continue

        lineas.append(",".join(fila))

    return lineas


# ================================================================
# PROCESAMIENTO (CÁLCULO DE SALIDA ESPERADA)
# ================================================================

def procesar_detalle(variante, lineas, clases):
    """Procesa las líneas CSV y retorna registros válidos procesados."""
    cols = variante["cols"]
    n_cols = len(cols)
    offset = variante["offset"]
    factor = variante["factor"]
    ua = variante["ua"]
    ub = variante["ub"]
    dec = variante["decimales"]

    registros = []
    for linea in lineas[1:]:  # saltar header
        linea = linea.strip()
        if not linea:
            continue
        partes = linea.split(",")
        if len(partes) != n_cols:
            continue

        id_val = partes[0].strip()
        nombre = partes[1].strip()
        valor_str = partes[2].strip()
        unidad = partes[3].strip()
        grupo = partes[4].strip()

        # Validar unidad
        if unidad not in (ua, ub):
            continue

        # Validar numérico
        try:
            valor = float(valor_str)
        except ValueError:
            continue

        # Convertir si es necesario
        if unidad == ua:
            valor_conv = convertir(valor, offset, factor)
        else:
            valor_conv = valor

        valor_conv = round(valor_conv, dec)
        clase = clasificar(valor_conv, clases)

        registros.append({
            "id": id_val,
            "nombre": nombre,
            "valor": valor_conv,
            "clase": clase,
            "grupo": grupo,
        })

    # Ordenar por ID
    registros.sort(key=lambda r: r["id"])
    return registros


def generar_resumen(registros, variante):
    """Agrupa por grupo y calcula conteo, promedio, máximo."""
    dec = variante["decimales"]
    grupos = {}
    for r in registros:
        g = r["grupo"]
        if g not in grupos:
            grupos[g] = {"conteo": 0, "suma": 0.0, "maximo": float("-inf")}
        grupos[g]["conteo"] += 1
        grupos[g]["suma"] += r["valor"]
        if r["valor"] > grupos[g]["maximo"]:
            grupos[g]["maximo"] = r["valor"]

    resumen = []
    for g, m in grupos.items():
        promedio = round(m["suma"] / m["conteo"], dec)
        maximo = round(m["maximo"], dec)
        resumen.append({
            "grupo": g,
            "conteo": m["conteo"],
            "promedio": promedio,
            "maximo": maximo,
        })

    resumen.sort(key=lambda r: r["conteo"], reverse=True)
    return resumen


# ================================================================
# GENERACIÓN DEL ENUNCIADO
# ================================================================

def generar_enunciado(variante, matricula, clases, ejemplo_in,
                      ejemplo_det, ejemplo_res, fecha_limite, hash_datos):
    """Genera el enunciado del examen en Markdown."""
    v = variante
    dec = v["decimales"]
    col_grupo = v["cols"][4]

    # Tabla de columnas de entrada
    tabla_cols = ""
    for c, d in zip(v["cols"], v["cols_desc"]):
        tabla_cols += f"| `{c}` | {d} |\n"

    # Tabla de clasificación detallada (con regla explícita)
    tabla_clases_detallada = ""
    for i, (nombre, vmin, vmax) in enumerate(clases):
        rango = formato_rango(vmin, vmax, dec)
        if vmin is None:
            regla = f"`valor < {vmax:.{dec}f}`"
        elif vmax is None:
            regla = f"`valor >= {vmin:.{dec}f}`"
        else:
            regla = f"`{vmin:.{dec}f} <= valor < {vmax:.{dec}f}`"
        tabla_clases_detallada += f"| {nombre} | {rango} | {regla} |\n"

    # Ejemplo de valor formateado
    ejemplo_valor = f"37.5" if dec == 1 else f"37.50"

    # Ejemplo entrada (primeras 5 filas)
    ej_in = "\n".join(ejemplo_in[:6])  # header + 5 filas
    ej_det = "\n".join(ejemplo_det[:6])
    ej_res = "\n".join(ejemplo_res[:6])

    enunciado = f"""# Examen Parcial 1 - Programación para Ciencia de Datos

## {v['titulo']}

**Matrícula:** `{matricula}`
**Fecha límite de entrega:** {fecha_limite}
**Valor:** 100 puntos

---

## Contexto

{v['contexto']}

---

## Datos de Entrada

El archivo `datos/{v['archivo']}` contiene registros con las siguientes columnas:

| Columna | Tipo esperado | Descripción |
|---------|---------------|-------------|
| `{v['cols'][0]}` | texto | {v['cols_desc'][0]} |
| `{v['cols'][1]}` | texto | {v['cols_desc'][1]} |
| `{v['cols'][2]}` | numérico (decimal) | {v['cols_desc'][2]} |
| `{v['cols'][3]}` | texto (`{v['ua']}` o `{v['ub']}`) | {v['cols_desc'][3]} |
| `{v['cols'][4]}` | texto | {v['cols_desc'][4]} |

**Unidades posibles:** `{v['ua']}` ({v['nombre_ua']}) y `{v['ub']}` ({v['nombre_ub']})

**Importante:** El archivo contiene aproximadamente 1000 registros. Algunos registros
contienen errores intencionales (valores no numéricos, unidades inválidas, columnas
faltantes o sobrantes, líneas vacías). Tu programa debe manejar estos casos sin
detenerse.

### Huella de integridad de los datos

El archivo de datos proporcionado tiene el siguiente hash SHA-256:

```
{hash_datos}
```

**No modifiques el archivo de datos.** Este hash se verificará automáticamente al
calificar tu examen. Si el hash no coincide, se considerará que los datos fueron
alterados y se penalizará la calificación.

> Para verificar el hash de tu archivo puedes usar:
> ```python
> import hashlib
> with open("datos/{v['archivo']}", "r", encoding="utf-8") as f:
>     print(hashlib.sha256(f.read().encode("utf-8")).hexdigest())
> ```

---

## Reglas de Procesamiento

### 1. Lectura del archivo
Lee el archivo CSV desde `datos/{v['archivo']}`. El archivo usa comas (`,`) como
separador. La primera línea es el encabezado con los nombres de las columnas.

**¿Cómo leerlo?** Abre el archivo con `open()`, lee todas las líneas, separa la
primera línea (header) del resto. Para cada línea de datos, usa `.split(",")` para
obtener los valores individuales.

### 2. Validación de cada fila
Para cada fila del archivo (después del header), verifica que sea válida. Una fila
es **inválida** y debe ignorarse si cumple cualquiera de estas condiciones:

- **Línea vacía:** la línea no contiene texto (o solo espacios en blanco)
- **Número incorrecto de columnas:** al separar por coma, no resultan exactamente
  {len(v['cols'])} valores
- **Valor no numérico:** el campo `{v['cols'][2]}` no se puede convertir a `float`
  (usa `try/except ValueError`)
- **Unidad no reconocida:** el campo `{v['cols'][3]}` no es ni `{v['ua']}` ni `{v['ub']}`
  (la comparación es sensible a mayúsculas/minúsculas)

**Importante:** Tu programa no debe detenerse ni mostrar errores cuando encuentre
filas inválidas; simplemente las ignora y continúa con la siguiente.

### 3. Conversión de unidades
Para los registros válidos, convierte los valores que están en `{v['ua']}` a `{v['ub']}`
usando la fórmula:

```
{v['formula_txt']}
```

En Python:
```python
{v['formula_py']}
```

Los valores que **ya están en `{v['ub']}`** se mantienen sin cambio alguno.

Después de la conversión, redondea el resultado a **{dec} decimal{'es' if dec > 1 else ''}**
usando la función `round()`.

### 4. Clasificación
Clasifica cada registro según el valor **ya convertido** a `{v['ub']}`:

| Categoría | Rango ({v['ub']}) | Regla |
|-----------|------|-------|
{tabla_clases_detallada}

> **Convención de límites:** Los límites inferiores son **inclusivos** (`>=`) y los
> superiores son **exclusivos** (`<`), excepto en la última categoría donde solo hay
> límite inferior inclusivo.

### 5. Generación de archivos de salida

Tu programa debe generar **dos archivos CSV** en la carpeta `salidas/`. A continuación
se describe cada uno en detalle.

---

## Archivo de Salida 1: `salidas/reporte_detalle.csv`

Este archivo contiene **un registro por cada fila válida** del archivo de entrada,
con el valor ya convertido y su clasificación.

### Columnas del archivo

| # | Columna | Tipo | Descripción | Ejemplo |
|---|---------|------|-------------|---------|
| 1 | `{v['cols'][0]}` | texto | ID original, copiado tal cual de la entrada | `{v['prefijo_id']}0001` |
| 2 | `{v['cols'][1]}` | texto | Nombre original, copiado tal cual de la entrada | (varía) |
| 3 | `{col_grupo}` | texto | Grupo/categoría original | (varía) |
| 4 | `{v['col_valor_out']}` | decimal | Valor convertido a {v['ub']}, con {dec} decimal{'es' if dec > 1 else ''} | `{ejemplo_valor}` |
| 5 | `{v['col_clase_out']}` | texto | Clasificación asignada según los umbrales | (varía) |

### Reglas del archivo
- **Primera línea (header):** `{v['cols'][0]},{v['cols'][1]},{col_grupo},{v['col_valor_out']},{v['col_clase_out']}`
- **Ordenamiento:** ascendente por `{v['cols'][0]}` (orden alfabético/numérico del ID)
- **Separador:** coma (`,`), sin espacios alrededor
- **Decimales:** los valores en `{v['col_valor_out']}` deben tener exactamente
  {dec} decimal{'es' if dec > 1 else ''} (usa f-string: `f"{{valor:.{dec}f}}"`)
- **Sin filas inválidas:** solo aparecen registros que pasaron la validación

### Cómo generarlo paso a paso
1. Filtra solo los registros válidos (los que pasaron la validación del paso 2)
2. Para cada registro: convierte el valor (paso 3), clasifícalo (paso 4)
3. Almacena los resultados en una lista
4. Ordena la lista por ID ascendente
5. Escribe el header seguido de cada registro, una línea por registro

---

## Archivo de Salida 2: `salidas/reporte_resumen.csv`

Este archivo contiene **una fila por cada grupo** (`{col_grupo}`), con métricas
agregadas calculadas a partir de los registros válidos.

### Columnas del archivo

| # | Columna | Tipo | Descripción | Cómo calcularlo |
|---|---------|------|-------------|-----------------|
| 1 | `{col_grupo}` | texto | Nombre del grupo | La clave del diccionario de agrupación |
| 2 | `conteo` | entero | Cantidad de registros válidos en ese grupo | Contar cuántos registros pertenecen al grupo |
| 3 | `promedio` | decimal | Promedio del valor convertido, {dec} decimal{'es' if dec > 1 else ''} | Suma de valores / conteo |
| 4 | `maximo` | decimal | Valor máximo convertido, {dec} decimal{'es' if dec > 1 else ''} | El mayor valor del grupo |

### Reglas del archivo
- **Primera línea (header):** `{col_grupo},conteo,promedio,maximo`
- **Ordenamiento principal:** descendente por `conteo` (el grupo con más registros primero)
- **Desempate:** si dos grupos tienen el mismo conteo, orden alfabético por `{col_grupo}`
- **Decimales:** `promedio` y `maximo` con exactamente {dec} decimal{'es' if dec > 1 else ''}
- **`conteo`** es un entero (sin decimales)

### Cómo generarlo paso a paso
1. Usa un **diccionario** para agrupar: la clave es el valor de `{col_grupo}`, el valor
   es otro diccionario con `conteo`, `suma` y `maximo`
2. Recorre todos los registros válidos (ya procesados en el detalle):
   - Si el grupo no existe en el diccionario, créalo con conteo=0, suma=0.0, maximo=-infinito
   - Incrementa el conteo, suma el valor convertido, actualiza el máximo si corresponde
3. Calcula el promedio: `promedio = suma / conteo`
4. Ordena por conteo descendente (y alfabético en caso de empate)
5. Escribe el header seguido de cada grupo

---

## Estructura del Proyecto Requerida

```
examen_{matricula}/
├── main.py                    # Punto de entrada: orquesta todo el proceso
├── models/
│   ├── __init__.py            # Puede estar vacío o exportar la clase
│   └── {v['entidad'].lower()}.py        # Definición de la clase {v['entidad']}
├── utils/
│   ├── __init__.py            # Puede estar vacío o exportar funciones
│   ├── io_helpers.py          # Funciones para leer CSV y escribir reportes
│   └── validators.py          # Funciones para validar filas del CSV
├── datos/
│   └── {v['archivo']}      # Archivo de entrada (proporcionado, NO modificar)
└── salidas/
    ├── reporte_detalle.csv    # Generado por tu programa
    └── reporte_resumen.csv    # Generado por tu programa
```

### Descripción de cada archivo

**`main.py`** — Punto de entrada. Al ejecutar `python main.py` desde la raíz del
proyecto, debe:
1. Leer el archivo de datos usando funciones de `utils/io_helpers.py`
2. Validar cada fila usando funciones de `utils/validators.py`
3. Crear objetos `{v['entidad']}` para cada registro válido
4. Generar el reporte de detalle y escribirlo en `salidas/reporte_detalle.csv`
5. Generar el reporte de resumen y escribirlo en `salidas/reporte_resumen.csv`

**`models/{v['entidad'].lower()}.py`** — Contiene la clase `{v['entidad']}` (ver sección siguiente).

**`utils/io_helpers.py`** — Contiene al menos:
- Una función para **leer** el archivo CSV y retornar las filas como lista de listas o diccionarios
- Una función para **escribir** un archivo CSV a partir de una lista de datos

**`utils/validators.py`** — Contiene al menos:
- Una función para **validar** si una fila del CSV es válida (número correcto de
  columnas, valor numérico, unidad reconocida)
- Debe retornar `True`/`False` o una tupla `(es_valido, mensaje_error)`

---

## Clase Requerida: `{v['entidad']}`

La clase `{v['entidad']}` en `models/{v['entidad'].lower()}.py` debe incluir:

- **`__init__(self, ...)`**: Recibe y almacena como atributos: `{v['cols'][0]}`,
  `{v['cols'][1]}`, el valor ya convertido a {v['ub']}, y `{col_grupo}`
- **`clasificar(self)`**: Método que retorna un string con la clasificación según
  los umbrales definidos (ej: `"{clases[0][0]}"`, `"{clases[1][0]}"`, etc.)
- **`__str__(self)`**: Retorna una representación legible para el usuario
  (ej: `"{v['prefijo_id']}0001 - NombreEjemplo ({col_grupo}: GrupoEjemplo) - 37.5 {v['ub']}"`)
- **`__repr__(self)`**: Retorna una representación técnica para depuración
  (ej: `"{v['entidad']}(id='{v['prefijo_id']}0001', valor=37.5, clase='Normal')"`)

---

## Ejemplo

### Entrada (primeras filas de `datos/{v['archivo']}`):
```csv
{ej_in}
```

### Salida detalle esperada (`salidas/reporte_detalle.csv`):
```csv
{ej_det}
```

### Salida resumen esperada (`salidas/reporte_resumen.csv`):
```csv
{ej_res}
```

---

## Criterios de Evaluación

| Criterio | Puntos | Detalle |
|----------|--------|---------|
| Estructura del proyecto | 15 | Carpetas, archivos, `__init__.py`, imports correctos |
| Clase `{v['entidad']}` | 20 | `__init__`, `clasificar()`, `__str__`, `__repr__` |
| Validación de datos | 10 | Manejo correcto de filas inválidas |
| Conversión de unidades | 15 | Fórmula correcta, precisión decimal |
| Clasificación | 10 | Umbrales correctos, categorías asignadas |
| Agrupación y métricas | 15 | Conteo, promedio, máximo por grupo |
| Formato de salida | 10 | CSVs con columnas, orden y formato correctos |
| Git | 5 | Mínimo 5 commits descriptivos, `.gitignore` |
| **Total** | **100** | |

> **Nota:** Se verificará automáticamente que el hash SHA-256 del archivo de datos
> coincida con `{hash_datos}`. Si el archivo fue modificado, se aplicará una
> penalización.

---

## Instrucciones de Entrega

1. Crea un repositorio en GitHub llamado `examen1_pcd`
2. Desarrolla tu solución siguiendo la estructura indicada
3. Asegúrate de que tu programa funciona ejecutando: `python main.py`
4. Tu programa debe leer de `datos/{v['archivo']}` y escribir en `salidas/`
5. Haz **mínimo 5 commits** con mensajes descriptivos
6. Incluye un `.gitignore` apropiado
7. **NO modifiques** el archivo `datos/{v['archivo']}` (se verificará su integridad)
8. Entrega el enlace a tu repositorio antes de la fecha límite

## Restricciones

- **NO** uses pandas, numpy ni librerías externas (solo biblioteca estándar de Python)
- **NO** copies código de otros compañeros (cada examen tiene datos y umbrales únicos)
- **NO** modifiques el archivo de datos proporcionado
- Tu código debe funcionar con **cualquier** archivo que siga el formato descrito,
  no solo con los datos proporcionados
"""
    return enunciado


# ================================================================
# ESCRITURA DE ARCHIVOS
# ================================================================

def escribir_examen(matricula, variante, clases, lineas_entrada,
                    registros_detalle, resumen, enunciado, output_dir,
                    hash_datos=""):
    """Escribe todos los archivos del examen en disco."""
    v = variante
    dec = v["decimales"]
    base = Path(output_dir) / f"examen_{matricula}"

    # Crear carpetas
    (base / "datos").mkdir(parents=True, exist_ok=True)
    (base / "_esperado").mkdir(parents=True, exist_ok=True)

    # 1. Enunciado
    with open(base / "enunciado.md", "w", encoding="utf-8") as f:
        f.write(enunciado)

    # 2. Datos de entrada
    with open(base / "datos" / v["archivo"], "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_entrada) + "\n")

    # 3. Salida esperada - detalle
    col_grupo = v["cols"][4]
    header_det = f"{v['cols'][0]},{v['cols'][1]},{col_grupo},{v['col_valor_out']},{v['col_clase_out']}"
    lineas_det = [header_det]
    for r in registros_detalle:
        valor_fmt = f"{r['valor']:.{dec}f}"
        lineas_det.append(f"{r['id']},{r['nombre']},{r['grupo']},{valor_fmt},{r['clase']}")

    with open(base / "_esperado" / "reporte_detalle.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_det) + "\n")

    # 4. Salida esperada - resumen
    header_res = f"{col_grupo},conteo,promedio,maximo"
    lineas_res = [header_res]
    for r in resumen:
        prom_fmt = f"{r['promedio']:.{dec}f}"
        max_fmt = f"{r['maximo']:.{dec}f}"
        lineas_res.append(f"{r['grupo']},{r['conteo']},{prom_fmt},{max_fmt}")

    with open(base / "_esperado" / "reporte_resumen.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_res) + "\n")

    # 5. Guardar metadatos (variante, clases, hash, para verificación)
    meta = f"variante={v['id']}\n"
    meta += f"matricula={matricula}\n"
    meta += f"decimales={dec}\n"
    meta += f"n_registros_validos={len(registros_detalle)}\n"
    meta += f"n_grupos={len(resumen)}\n"
    meta += f"hash_datos={hash_datos}\n"
    meta += f"archivo_datos={v['archivo']}\n"
    for i, (nombre, vmin, vmax) in enumerate(clases):
        meta += f"clase_{i}={nombre},{vmin},{vmax}\n"

    with open(base / "_esperado" / "meta.txt", "w", encoding="utf-8") as f:
        f.write(meta)

    return base, lineas_det, lineas_res


# ================================================================
# ORQUESTACIÓN PRINCIPAL
# ================================================================

def generar_examen(matricula, output_dir="examenes", fecha_limite="(por definir)",
                   n_registros=50):
    """Genera un examen completo para una matrícula."""
    matricula = matricula.strip().upper()
    seed = matricula_to_seed(matricula)
    rng = random.Random(seed)

    # Seleccionar variante
    idx_variante = seed % len(VARIANTES)
    variante = VARIANTES[idx_variante]

    # Perturbar umbrales
    clases = perturbar_umbrales(
        variante["clases_base"], rng, variante["perturb_mag"]
    )

    # Generar datos
    lineas = generar_datos(variante, rng, n=n_registros)

    # Calcular hash de los datos de entrada
    contenido_datos = "\n".join(lineas) + "\n"
    hash_datos = calcular_hash_datos(contenido_datos)

    # Calcular salida esperada
    detalle = procesar_detalle(variante, lineas, clases)
    resumen = generar_resumen(detalle, variante)

    # Preparar líneas formateadas para ejemplo
    dec = variante["decimales"]
    col_grupo = variante["cols"][4]

    header_det = (f"{variante['cols'][0]},{variante['cols'][1]},"
                  f"{col_grupo},{variante['col_valor_out']},"
                  f"{variante['col_clase_out']}")
    ejemplo_det = [header_det]
    for r in detalle[:5]:
        v_fmt = f"{r['valor']:.{dec}f}"
        ejemplo_det.append(f"{r['id']},{r['nombre']},{r['grupo']},{v_fmt},{r['clase']}")

    header_res = f"{col_grupo},conteo,promedio,maximo"
    ejemplo_res = [header_res]
    for r in resumen[:5]:
        p_fmt = f"{r['promedio']:.{dec}f}"
        m_fmt = f"{r['maximo']:.{dec}f}"
        ejemplo_res.append(f"{r['grupo']},{r['conteo']},{p_fmt},{m_fmt}")

    # Generar enunciado (con hash incluido)
    enunciado = generar_enunciado(
        variante, matricula, clases,
        lineas, ejemplo_det, ejemplo_res, fecha_limite, hash_datos
    )

    # Escribir archivos
    ruta, _, _ = escribir_examen(
        matricula, variante, clases, lineas,
        detalle, resumen, enunciado, output_dir, hash_datos
    )

    return ruta, variante, len(detalle), len(resumen)


# ================================================================
# CLI
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generador de Examen Parcial 1 - PCD 2026-02"
    )
    parser.add_argument(
        "matricula", nargs="?",
        help="Matrícula del alumno"
    )
    parser.add_argument(
        "--lote", type=str,
        help="Archivo con lista de matrículas (una por línea)"
    )
    parser.add_argument(
        "--output-dir", type=str, default="examenes",
        help="Directorio de salida (default: examenes/)"
    )
    parser.add_argument(
        "--fecha-limite", type=str, default="(por definir)",
        help="Fecha límite de entrega (ej: 2026-04-10)"
    )
    parser.add_argument(
        "--registros", type=int, default=1000,
        help="Número de registros a generar (default: 1000)"
    )
    args = parser.parse_args()

    if not args.matricula and not args.lote:
        parser.error("Debes proporcionar una matrícula o --lote archivo.txt")

    matriculas = []
    if args.lote:
        with open(args.lote, "r", encoding="utf-8") as f:
            matriculas = [l.strip() for l in f if l.strip()]
    else:
        matriculas = [args.matricula]

    print(f"Generando {len(matriculas)} examen(es)...\n")

    for mat in matriculas:
        ruta, var, n_det, n_res = generar_examen(
            mat, args.output_dir, args.fecha_limite, args.registros
        )
        print(f"  [{mat}] Variante: {var['titulo']}")
        print(f"          Registros válidos: {n_det} | Grupos: {n_res}")
        print(f"          Carpeta: {ruta}\n")

    print("Listo. Los archivos en _esperado/ son para el profesor (no distribuir).")


if __name__ == "__main__":
    main()
