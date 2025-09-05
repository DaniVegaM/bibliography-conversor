"""
Módulo para manejar las equivalencias entre formatos BibTeX y RIS
Este archivo se encarga de cargar y organizar la información del archivo CSV
"""

import csv
import sys


def load_tag_equivalences(csv_file="tag_equivalence.csv"):
    """
    Carga las equivalencias de tags desde el archivo CSV
    
    Args:
        csv_file (str): Ruta al archivo CSV con las equivalencias
        
    Returns:
        tuple: (equivalencias_campos, tipos_entrada)
            - equivalencias_campos: diccionario {campo_bibtex: tag_ris}
            - tipos_entrada: diccionario {tipo_bibtex: tipo_ris}
    """
    # Diccionarios para almacenar las conversiones
    equivalencias_campos = {}  # Para campos individuales como title -> TI
    tipos_entrada = {}         # Para tipos de entrada como @article -> JOUR
    
    try:
        # Abrir el archivo CSV y leerlo línea por línea
        with open(csv_file, 'r', encoding='utf-8') as file:
            # csv.DictReader convierte cada fila en un diccionario
            # usando la primera fila como nombres de columnas
            reader = csv.DictReader(file)
            
            for row in reader:
                # Procesar filas que definen campos (como title, author, etc.)
                if row['Type'] == 'Field':
                    bibtex_field = row['BibTeX Field']  # ej: "title"
                    ris_tag = row['RIS Tag']            # ej: "TI"
                    # Guardar la equivalencia en el diccionario
                    equivalencias_campos[bibtex_field] = ris_tag
                
                # Procesar filas que definen tipos de entrada (como @article, @inproceedings)
                elif row['Type'] == 'Entry Type':
                    bibtex_type = row['BibTeX Field']   # ej: "@article"
                    ris_type = row['RIS Tag']           # ej: "JOUR"
                    # Guardar la equivalencia en el diccionario
                    tipos_entrada[bibtex_type] = ris_type
                    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {csv_file}")
        print("Asegúrate de que el archivo tag_equivalence.csv esté en el directorio actual")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)
    
    return equivalencias_campos, tipos_entrada


def get_bibtex_to_ris_field(bibtex_field, equivalencias):
    """
    Convierte un campo de BibTeX a su equivalente en RIS
    
    Args:
        bibtex_field (str): Nombre del campo en BibTeX (ej: "title")
        equivalencias (dict): Diccionario de equivalencias
        
    Returns:
        str: Tag correspondiente en RIS (ej: "TI") o None si no existe
    """
    return equivalencias.get(bibtex_field)


def get_ris_to_bibtex_field(ris_tag, equivalencias):
    """
    Convierte un tag de RIS a su equivalente en BibTeX
    
    Args:
        ris_tag (str): Tag en RIS (ej: "TI")
        equivalencias (dict): Diccionario de equivalencias
        
    Returns:
        str: Campo correspondiente en BibTeX (ej: "title") o None si no existe
    """
    # Como el diccionario está en dirección bibtex->ris, 
    # necesitamos buscar en los valores
    for bibtex_field, ris_field in equivalencias.items():
        if ris_field == ris_tag:
            return bibtex_field
    return None


def print_equivalences_summary(equivalencias, tipos_entrada):
    """
    Imprime un resumen de las equivalencias cargadas
    """
    print(f"📋 Equivalencias cargadas:")
    print(f"   - Campos: {len(equivalencias)} equivalencias")
    print(f"   - Tipos de entrada: {len(tipos_entrada)} equivalencias")
    
    print("\n🔄 Tipos de entrada disponibles:")
    for bibtex_type, ris_type in tipos_entrada.items():
        print(f"   {bibtex_type} ↔ {ris_type}")
