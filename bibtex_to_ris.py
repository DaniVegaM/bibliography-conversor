# Conversor de BibTeX a RIS usando expresiones regulares
# By: Daniel Vega Miranda

import re


def convert_bibtex_to_ris(bibtex_content, field_equivalences, entry_types):
    """
    Convierte contenido BibTeX completo a formato RIS usando expresiones regulares
    
    Args:
        bibtex_content (str): Contenido completo del archivo BibTeX
        field_equivalences (dict): Equivalencias de campos (ej: 'title' -> 'TI')
        entry_types (dict): Equivalencias de tipos (ej: '@article' -> 'JOUR')
    
    Returns:
        str: Contenido en formato RIS
    """
    print("🔄 Iniciando conversión BibTeX → RIS...")
    
    # Dividir el contenido en entradas individuales usando regex
    entries = split_bibtex_entries(bibtex_content)
    
    if not entries:
        print("❌ No se encontraron entradas válidas")
        return ""
    
    print(f"📊 Encontradas {len(entries)} entradas")
    
    # Convertir cada entrada
    ris_entries = []
    for i, entry in enumerate(entries, 1):
        print(f"   Procesando entrada {i}/{len(entries)}")
        ris_entry = convert_single_bibtex_entry(entry, field_equivalences, entry_types)
        if ris_entry:
            ris_entries.append(ris_entry)
    
    print("✅ Conversión completada")
    return '\n'.join(ris_entries)


def split_bibtex_entries(content):
    """
    Divide el contenido BibTeX en entradas individuales usando regex
    
    Args:
        content (str): Contenido completo del archivo BibTeX
    
    Returns:
        list: Lista de entradas BibTeX individuales
    """
    # Patrón para encontrar entradas BibTeX: @tipo{clave, contenido}
    # Busca desde @ hasta el } que cierra la entrada, manejando {} anidados
    pattern = r'@\w+\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
    
    entries = []
    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        entry_text = match.group().strip()
        if entry_text:
            entries.append(entry_text)
    
    return entries


def convert_single_bibtex_entry(entry_text, field_equivalences, entry_types):
    """
    Convierte una sola entrada BibTeX a formato RIS
    
    Args:
        entry_text (str): Texto de una entrada BibTeX
        field_equivalences (dict): Equivalencias de campos
        entry_types (dict): Equivalencias de tipos
    
    Returns:
        str: Entrada en formato RIS
    """
    # Extraer información básica de la entrada
    entry_info = parse_bibtex_entry(entry_text)
    
    if not entry_info:
        return ""
    
    ris_lines = []
    
    # 1. Agregar tipo de entrada (TY)
    bibtex_type = f"@{entry_info['type']}"
    ris_type = entry_types.get(bibtex_type, 'GEN')  # GEN por defecto
    ris_lines.append(f"TY  - {ris_type}")
    
    # 2. Agregar ID (identificador de la entrada)
    if entry_info.get('key'):
        ris_lines.append(f"ID  - {entry_info['key']}")
    
    # 3. Convertir todos los campos
    fields = entry_info.get('fields', {})
    for field_name, field_value in fields.items():
        ris_tag = field_equivalences.get(field_name)
        
        if ris_tag and field_value.strip():
            # Limpiar el valor del campo
            clean_value = clean_field_value(field_value)
            
            # Casos especiales que necesitan procesamiento diferente
            if field_name == 'author' or field_name == 'editor':
                # Autores/editores: cada uno en una línea separada
                authors = split_authors(clean_value)
                for author in authors:
                    if author.strip():
                        ris_lines.append(f"{ris_tag}  - {author.strip()}")
            
            elif field_name == 'pages':
                # Páginas: separar inicio (SP) y fin (EP)
                start_page, end_page = extract_page_range(clean_value)
                if start_page:
                    ris_lines.append(f"SP  - {start_page}")
                if end_page and end_page != start_page:
                    ris_lines.append(f"EP  - {end_page}")
            
            elif field_name == 'keywords':
                # Palabras clave: cada una en línea separada
                keywords = [kw.strip() for kw in clean_value.split(',')]
                for keyword in keywords:
                    if keyword:
                        ris_lines.append(f"{ris_tag}  - {keyword}")
            
            else:
                # Campo normal
                ris_lines.append(f"{ris_tag}  - {clean_value}")
    
    # 4. Agregar línea de fin de entrada
    ris_lines.append("ER  - ")
    ris_lines.append("")  # Línea vacía entre entradas
    
    return '\n'.join(ris_lines)


def parse_bibtex_entry(entry_text):
    """
    Parsea una entrada BibTeX y extrae su información usando regex
    
    Args:
        entry_text (str): Texto de la entrada BibTeX
    
    Returns:
        dict: Información extraída de la entrada
    """
    entry_info = {'fields': {}}
    
    # Extraer tipo y clave de la entrada: @article{key,
    header_pattern = r'@(\w+)\s*\{\s*([^,\s}]+)\s*,'
    header_match = re.search(header_pattern, entry_text, re.IGNORECASE)
    
    if header_match:
        entry_info['type'] = header_match.group(1).lower()
        entry_info['key'] = header_match.group(2).strip()
    else:
        return None
    
    # Extraer todos los campos: nombre = {valor} o nombre = "valor"
    # Patrón que maneja valores entre {} o "" y puede tener {} anidados
    field_pattern = r'(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|(\w+)\s*=\s*"([^"]*)"'
    
    field_matches = re.finditer(field_pattern, entry_text, re.DOTALL)
    
    for match in field_matches:
        if match.group(1):  # Valor entre {}
            field_name = match.group(1).lower().strip()
            field_value = match.group(2).strip()
        else:  # Valor entre ""
            field_name = match.group(3).lower().strip()
            field_value = match.group(4).strip()
        
        if field_name and field_value:
            entry_info['fields'][field_name] = field_value
    
    return entry_info


def clean_field_value(value):
    """
    Limpia un valor de campo BibTeX removiendo caracteres especiales
    
    Args:
        value (str): Valor original del campo
    
    Returns:
        str: Valor limpio
    """
    # Remover saltos de línea extra y espacios
    clean_value = re.sub(r'\s+', ' ', value.strip())
    
    # Remover comandos LaTeX comunes
    clean_value = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', clean_value)
    clean_value = re.sub(r'\\[a-zA-Z]+', '', clean_value)
    
    # Remover {} extra
    clean_value = clean_value.replace('{', '').replace('}', '')
    
    return clean_value.strip()


def split_authors(authors_text):
    """
    Divide una cadena de autores BibTeX en autores individuales
    
    Args:
        authors_text (str): Texto con autores separados por 'and'
    
    Returns:
        list: Lista de autores individuales
    """
    # Los autores en BibTeX se separan con 'and'
    authors = re.split(r'\s+and\s+', authors_text, flags=re.IGNORECASE)
    return [author.strip() for author in authors if author.strip()]


def extract_page_range(pages_text):
    """
    Extrae el rango de páginas de un campo pages BibTeX
    
    Args:
        pages_text (str): Texto del campo pages (ej: "123--145" o "123-145")
    
    Returns:
        tuple: (página_inicio, página_fin)
    """
    # Buscar patrones como "123--145", "123-145", "123—145"
    page_pattern = r'(\d+)[-–—]+(\d+)'
    match = re.search(page_pattern, pages_text)
    
    if match:
        start_page = match.group(1)
        end_page = match.group(2)
        return start_page, end_page
    else:
        # Si no hay rango, buscar solo un número
        single_page_pattern = r'(\d+)'
        single_match = re.search(single_page_pattern, pages_text)
        if single_match:
            page = single_match.group(1)
            return page, page
    
    return None, None
