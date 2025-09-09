# Conversor de BibTeX a RIS usando expresiones regulares
# By: Daniel Vega Miranda

import re
import regex

def convert_bibtex_to_ris(bib_content):
    print("Iniciando conversión de BibTeX a RIS...\n\n")
    
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
                \{                    # abre {
                ((?:                  # group(2): contenido de las llaves
                    [^{}]+            #  texto que no son llaves
                    |                 #  o
                    (?&braces)        #  otro bloque {...} (recursión)
                )*)
                \}                    # cierra }
            )
        )
    """

    separated_entries = {}

    match = regex.search(pattern, bib_content, regex.VERBOSE)
    if match:
        entry_type = match.group(1)
        id = match.group(2)
        entries = match.group(3)

        print(f"Entries: {entries}\n\n")

        field_matches = regex.finditer(separated_entries_pattern, entries, regex.VERBOSE)
    
        for match in field_matches:
            field_name = match.group(2).strip()  # nombre del campo
            field_value = match.group(3).strip() # contenido entre llaves
            separated_entries[field_name] = field_value

        print(f"Separated entries: {separated_entries}")

        

    # print(f"Tipo de entrada: {entry_type}")
    # print(f"ID de la entrada: {id}")
    # print(f"Entradas detectadas: {entries}")

    return

    # Variables que utilizaremos para almacenar la información de cada entrada
    fields = {}
    type_found = False # Bandera para saber si ya hemos encontrado el entry_type

    for entry in entries:
        # print(f"Procesando entrada: {entry}")

        # Vemos si es entry_type o field
        if (not type_found):
            match = re.search(r"^(TY|ty|Ty|tY)\s*-\s*(.+)", entry)
            type = None
            if match:
                type = match.group(2).strip().lower()

            if type: # es un entry_type
                entry_type = type
                # print(f"Tipo de entrada detectado: {entry_type}")
                type_found = True
                continue
        else: # es un field
            match = re.search(r"([A-Z]{2}|[a-z]{2})\s*-\s*(.+)", entry)
            if match:
                field = match.group(1).strip().lower()
                field_content = match.group(2).strip()

                if field in fields:
                    fields[field] += " and " + field_content
                else:
                    fields[field] = field_content
    
    # print(f"\n\nCampos recopilados:\n\n{fields}")

    # Mapeo de tipos de entrada RIS a BibTeX
    
    ris_to_bibtex_type = {
        "au" : "author",
        "ti" : "title",
        "py" : "year",
        "vl" : "volume",
        "is" : "number",
        "sp" : "pages",
        "ep" : "pages",
        "do" : "doi",
        "ur" : "url",
        "pb" : "publisher",
        "jo" : "journal",
        "bt" : "booktitle",
        "ed" : "editor",
        "et" : "edition",
        "kw" : "keywords",
        "sn" : "issn",
        "cy" : "address",
        "pp" : "address",
        "ab" : "abstract",
        "id" : "id",
        "jour": "article", #entry_type
        "conf": "inproceedings", #entry_type
    }

    pages = "" #sp-ep
    keywords = "" #kw
    address = "" #cy, pp

    # Formateamos los campos que contienen más de un elemento
    for field, field_content in fields.items():
        #pages
        if field == "sp":
            pages += field_content
        elif field == "ep":
            pages += f"--{field_content}"
        #keywords
        elif field == "kw":
            if keywords:
                keywords += f", {field_content.replace(' and', ', ')}"
            else:
                keywords += field_content
        #address
        elif field == "cy" or field == "pp":
            if address:
                address += f", {field_content}"
            else:
                address += field_content

    # Construimos el archivo BibTeX
    cite_key = fields.get('id', '')
    if cite_key:
        cite_key += ','
    
    # NOTA: Asumimos que siempre habrá un entry_type válido
    bibtex_result = "@" + ris_to_bibtex_type.get(entry_type) + '{' + cite_key + "\n"

    # Añadimos los campos formateados
    if pages and re.search(r'\d+--\d+', pages): # Evitamos que solo se ponga pagina de inicio o de fin
        bibtex_result += f"pages = {{{pages}}},\n"
    if keywords:
        bibtex_result += f"keywords = {{{keywords}}},\n"
    if address:
        bibtex_result += f"address = {{{address}}},\n"

    # Añadimos todos los demas campos
    for key, content in fields.items():
        if key in ris_to_bibtex_type and key != "id" and key != "ty" and key != "sp" and key != "ep" and key != "kw" and key != "cy" and key != "pp":
            bibtex_key = ris_to_bibtex_type[key]
            bibtex_result += f"{bibtex_key} = {{{content}}},\n"

    bibtex_result += "}"

    print("\n\nConversión completada. ============================== \n\n")
    # print(bibtex_result)
    return bibtex_result
            