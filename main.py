# Conversor de Bibliografías BibTeX <=> RIS
# Usa expresiones regulares para convertir entre ambos formatos
# By: Daniel Vega Miranda

import sys
import os
import csv
from pathlib import Path
from colorama import Fore, Style, init
init(autoreset=True)

from bibtex_to_ris import convert_bibtex_to_ris
from ris_to_bibtex import convert_ris_to_bibtex

def main():
    show_menu()
    
    while True:
        file_path = select_file()
        
        if not file_path:
            break

        file_path = Path(file_path)
        
        # Verificamos que el archivo existe y es valido
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: El archivo {file_path} no existe")
            continue
        
        # Leemos el archivo y lo guardamos en 'content'
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception:
            print("{Fore.RED}Error: No se pudo leer el archivo")
            continue
        
        # Convertimos segun el tipo de archivo
        if file_path.suffix.lower() == '.bib':
            print(f"{Fore.GREEN}Convirtiendo BibTeX => RIS.......")

            result = convert_bibtex_to_ris(content)
            new_extension = '.ris'

        elif file_path.suffix.lower() == '.ris':
            print(f"{Fore.GREEN}Convirtiendo RIS => BibTeX.......")

            result = convert_ris_to_bibtex(content)
            new_extension = '.bib'

        else:
            print("{Fore.RED}Error: Formato de archivo no valido")
            continue
        
        if result:
            original_path = Path(file_path)
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)  # crea la carpeta si no existe
            new_path = results_dir / original_path.with_suffix(new_extension).name

            try:
                with open(new_path, 'w', encoding='utf-8') as file:
                    file.write(result)
                
                print(f"{Fore.GREEN}Conversión terminada!!!")
                print(f"{Fore.GREEN}Archivo guardado como: {new_path}")
                
            except Exception:
                print(f"{Fore.RED}Error al guardar")
        else:
            print(f"{Fore.RED}Error durante la conversión")
        
        continue_choice = input("¿Desea convertir otro formato? (s/n)").lower().strip()
        if continue_choice != 's':
            break


def show_menu():
    print(f"{Fore.GREEN}{Style.BRIGHT}<===========================================>")
    print(f"{Fore.GREEN}{Style.BRIGHT}        CONVERSOR DE BIBLIOGRAFÍAS.          ")
    print(f"{Fore.GREEN}{Style.BRIGHT}             BibTeX ===> RIS                 ")
    print(f"{Fore.GREEN}{Style.BRIGHT}             RIS ===> BibTeX                 ")
    print(f"{Fore.GREEN}{Style.BRIGHT}         by: Daniel Vega Miranda             ")
    print(f"{Fore.GREEN}{Style.BRIGHT}<===========================================>")


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
                print(f"{len(all_files)} {file.name} (BibTeX)")
            
            # Mostrar archivos .ris
            for file in ris_files:
                all_files.append(file)
                print(f"{len(all_files)} {file.name} (RIS)")
            
            print(f"{len(all_files) + 1}. Especificar archivo manualmente")
            print(f"{Fore.RED}{len(all_files) + 2}. Salir")
            
            try:
                choice = int(input(f"\nSelecciona (1-{len(all_files) + 2}): "))
                
                if 1 <= choice <= len(all_files):
                    return str(all_files[choice - 1])
                elif choice == len(all_files) + 1:
                    return input("Ruta del archivo: ").strip()
                else:
                    return None
                    
            except ValueError:
                print(f"{Fore.RED}Opción inválida")
                return select_file()
    
    return input("Ruta del archivo: ").strip()


if __name__ == "__main__":
    main()

