# Conversor de Bibliografías BibTeX <=> RIS
# Usa expresiones regulares para convertir entre ambos formatos
# By: Daniel Vega Miranda

import sys
import os
import csv
from pathlib import Path

from bibtex_to_ris import convert_bibtex_to_ris
from ris_to_bibtex import convert_ris_to_bibtex

def main():
    show_menu()
    
    # Cargamos equivalencias del CSV
    field_equivalences, entry_types = load_equivalences()
    
    while True:
        file_path = select_file()
        
        if not file_path:
            break
        
        # Verificamos que el archivo existe y es valido
        if not os.path.exists(file_path):
            print(f"Error: El archivo {file_path} no existe")
            continue
        
        # Leemos el archivo y lo guardamos en 'content'
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception:
            print("Error: No se pudo leer el archivo")
            continue
        
        # Convertimos segun el tipo de archivo
        if file_path.suffix.lower() == '.bib':
            print("Convirtiendo BibTeX => RIS.......")

            result = convert_bibtex_to_ris(content, field_equivalences, entry_types)
            new_extension = '.ris'

        elif file_path.suffix.lower() == '.ris':
            print("Convirtiendo RIS => BibTeX.......")

            result = convert_ris_to_bibtex(content, field_equivalences, entry_types)
            new_extension = '.bib'

        else:
            print("Error: Formato de archivo no valido")
            continue
        
        if result:
            original_path = Path(file_path)
            new_path = original_path.with_suffix(new_extension)
            
            try:
                with open(new_path, 'w', encoding='utf-8') as file:
                    file.write(result)
                
                print(f"Conversión terminada!!!")
                print(f"Archivo guardado como: {new_path}")
                
            except Exception:
                print(f"Error al guardar")
        else:
            print("Error durante la conversión")
        
        continue_choice = input("¿Desea convertir otro formato? (s/n)").lower().strip()
        if continue_choice != 's':
            break

def load_equivalences():
    # Estableciendo diccionarios para las equivalencias
    field_equivalences = {}  #Ej: author -> AU
    entry_types = {}        #Ej: @article -> JOUR
    
    try:
        with open("tag_equivalence.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Type'] == 'Field':
                    # Guardar equivalencia de campo
                    bibtex_field = row['BibTeX Field']
                    ris_tag = row['RIS Tag']
                    field_equivalences[bibtex_field] = ris_tag
                elif row['Type'] == 'Entry Type':
                    # Guardar equivalencia de tipo de entrada
                    bibtex_type = row['BibTeX Field']
                    ris_type = row['RIS Tag']
                    entry_types[bibtex_type] = ris_type
        
    except FileNotFoundError:
        print("Error: No se encontró tag_equivalence.csv")
        sys.exit(1)
    
    return field_equivalences, entry_types


def show_menu():
    print("<===========================================>")
    print("        CONVERSOR DE BIBLIOGRAFÍAS.          ")
    print("             BibTeX ===> RIS                 ")
    print("             RIS ===> BibTeX                 ")
    print("         by: Daniel Vega Miranda             ")
    print("<===========================================>")


def select_file():
    test_dir = Path("test")
    
    if test_dir.exists():
        # Buscar archivos disponibles
        bib_files = list(test_dir.glob("*.bib"))
        ris_files = list(test_dir.glob("*.ris"))
        
        if bib_files or ris_files:
            print("Elige un archivo para convertir:")
            
            all_files = []
            
            # Mostrar archivos .bib
            for file in bib_files:
                all_files.append(file)
                print(f"{file.name} (BibTeX)")
            
            # Mostrar archivos .ris
            for file in ris_files:
                all_files.append(file)
                print(f"{file.name} (RIS)")
            
            print(f"   {len(all_files) + 1}. Especificar archivo manualmente")
            print(f"   {len(all_files) + 2}. Salir")
            
            try:
                choice = int(input(f"\nSelecciona (1-{len(all_files) + 2}): "))
                
                if 1 <= choice <= len(all_files):
                    return str(all_files[choice - 1])
                elif choice == len(all_files) + 1:
                    return input("Ruta del archivo: ").strip()
                else:
                    return None
                    
            except ValueError:
                print("Opción inválida")
                return select_file()
    
    return input("Ruta del archivo: ").strip()


if __name__ == "__main__":
    main()

