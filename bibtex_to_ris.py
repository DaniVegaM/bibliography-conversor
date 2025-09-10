# Conversor de BibTeX a RIS usando expresiones regulares
# By: Daniel Vega Miranda

import re
import regex

from colorama import Fore, Style, init
init(autoreset=True)

def convert_bibtex_to_ris(bib_content):
    # print("Iniciando conversión de BibTeX a RIS...\n\n")
    
    # Dividimos por entradas
    bib_content = bib_content.strip()
    pattern = r"""
        @([a-zA-Z]+)                      # capturamos el type con group(1)
        \s*\{                             
        \s*([a-zA-Z0-9\-\.\/_]+)\s*,      # capturamos el ID con group(2)
        \s*                               #

        (                                 
            (?<entry>                     # grupo recursivo llamado "field"
                [a-zA-Z]+\s*=\s*          # capturamos el field y el "="
                (?<braces>                # grupo recursivo para llaves
                    \{                    # abre {
                    (?:                   # contenido:
                        [^{}]+            #  texto que no son llaves
                        |                 #  o
                        (?&braces)        #  otro bloque {...}
                    )*
                    \}                    # cierra }
                )
            )
            (?:\s*,\s*(?&entry))*         # puede haber varios campos separados por comas (excepto el ultimo campo que no tiene ",")
        )
        \s*\}                             #llave que cierra al final
    """

    entry_type = None
    id = None
    entries = None

    separated_entries_pattern = r"""
        (?<field>                     # grupo recursivo llamado "field"
            ([a-zA-Z]+)\s*=\s*        # capturamos el nombre del field con group(1)
            (?<braces>                # grupo recursivo para llaves
                \{(                    # abre {
                ((?:                  # group(2): contenido de las llaves
                    [^{}]+            #  texto que no son llaves
                    |                 #  o
                    (?&braces)        #  otro bloque {...} (recursión)
                )*))
                \}                    # cierra }
            )
        )
    """

    separated_entries = {}

    match = regex.search(pattern, bib_content, regex.VERBOSE)
    if match:
        entry_type = match.group(1).lower().strip()
        id = match.group(2).strip()
        entries = match.group(3)

        # print(f"Entries: {entries}\n\n")

        field_matches = regex.finditer(separated_entries_pattern, entries, regex.VERBOSE)
    
        for match in field_matches:
            field_name = match.group(2).strip()  # nombre del campo
            field_value = match.group(4).strip() # contenido entre llaves
            separated_entries[field_name] = field_value

        # print(f"Separated entries: {separated_entries}")
        
    else:
        print(f"{Fore.RED}No se encontraron entradas BibTeX válidas.")
        return
    
    bibtex_to_ris_type = {
        "author": "au",
        "title": "ti",
        "year": "py",
        "volume": "vl",
        "number": "is",
        "pages": "sp",
        "pages": "ep",
        "doi": "do",
        "url": "ur",
        "publisher": "pb",
        "journal": "jo",
        "booktitle": "bt",
        "editor": "ed",
        "edition": "et",
        "keywords": "kw",
        "issn": "sn",
        "address": "cy",
        "address": "pp",
        "abstract": "ab",
        "id": "id",
        "article": "jour", #entry_type
        "inproceedings": "conf", #entry_type
    }

    sp = ""
    ep = ""
    kw = []
    cy = ""
    pp = ""

    # Formateamos los campos que contienen más de un elemento
    if(entry_type == "inproceedings"):
        entry_type = "CONF"
    elif(entry_type == "article"):
        entry_type = "JOUR"

    for field, field_content in separated_entries.items():
        #pages
        if field == "pages":
            parts = re.split(r'-+', field_content)
            if len(parts) == 2:
                sp = parts[0].strip()
                ep = parts[1].strip()
            elif len(parts) == 1:
                sp = parts[0].strip()
        #keywords
        elif field == "keywords":
            keywords = re.sub(r'\s*,\s*', ', ', field_content)
            keywords = re.sub(r'\s*;\s*', '; ', keywords)
            keywords = re.sub(r'\s+and\s+', ', ', keywords)
            keywords = re.sub(r'\s+', ' ', keywords)
            keywords = keywords.strip()
            split_keywords = re.split(r',\s*|;\s*', keywords)

            kw = [f"KW  - {k.strip()}" for k in split_keywords if k.strip()]
        #address
        elif field == "address":
            parts = re.split(r'\s*;?,?\/?\s*', field_content)
            if len(parts) == 2:
                cy = parts[0].strip()
                pp = parts[1].strip()
            elif len(parts) == 1:
                cy = parts[0].strip()
        #authors
        elif field == "author":
            authors = re.split(r'\s+and\s+', field_content)
            authors = [a.strip() for a in authors if a.strip()]
            separated_entries[field] = " and ".join(authors)
        #editors
        elif field == "editor":
            editors = re.split(r'\s+and\s+', field_content)
            editors = [e.strip() for e in editors if e.strip()]
            separated_entries[field] = " and ".join(editors)

    # Construimos el archivo BibTeX
    ris_result = "TY  - " + entry_type + "\n"

    # Añadimos los campos formateados
    if id:
        ris_result += f"ID  - {id}\n"
    if sp and ep:
        ris_result += f"SP  - {sp}\n"
        ris_result += f"EP  - {ep}\n"
    if kw:
        ris_result += "\n".join(kw) + "\n"
    if cy:
        ris_result += f"CY  - {cy}\n"
    if pp:
        ris_result += f"PP  - {pp}\n"

    # Añadimos todos los demas campos
    for key, content in separated_entries.items():
        if key in bibtex_to_ris_type and key != "id" and key != "article" and key != "inproceedings" and key != "pages" and key != "keywords" and key != "address":
            ris_key = bibtex_to_ris_type[key]
            
            # Elimina saltos de línea y la coma final
            clean_content = content.replace('\n', ' ').replace('\r', ' ').strip()
            if clean_content.endswith(','):
                clean_content = clean_content[:-1].strip()
            ris_result += f"{ris_key.upper()}  - {clean_content}\n"

    ris_result += "ER  - \n"

    print(f"{Fore.GREEN}\n\nConversión completada. ============================== \n\n")

    return ris_result
            