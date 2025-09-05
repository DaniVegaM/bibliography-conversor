# Conversor de RIS a BibTeX usando expresiones regulares
# By: Daniel Vega Miranda

import re


def convert_ris_to_bibtex(ris_content, field_equivalences, entry_types):
    """
    Convierte contenido RIS completo a formato BibTeX usando expresiones regulares
    
    Args:
        ris_content (str): Contenido completo del archivo RIS
        field_equivalences (dict): Equivalencias de campos (ej: 'title' -> 'TI')
        entry_types (dict): Equivalencias de tipos (ej: '@article' -> 'JOUR')
    
    Returns:
        str: Contenido en formato BibTeX
    """
    print("🔄 Iniciando conversión RIS → BibTeX...")
    
    # Dividir el contenido en entradas individuales
    entries = split_ris_entries(ris_content)
    
    if not entries:
        print("❌ No se encontraron entradas válidas")
        return ""
    
    print(f"📊 Encontradas {len(entries)} entradas")
    
    # Crear diccionario inverso para convertir de RIS a BibTeX
    # Invertir field_equivalences: 'TI' -> 'title'
    ris_to_bibtex_fields = {v: k for k, v in field_equivalences.items()}
    
    # Invertir entry_types: 'JOUR' -> '@article'
    ris_to_bibtex_types = {v: k for k, v in entry_types.items()}
    
    # Convertir cada entrada
    bibtex_entries = []
    for i, entry in enumerate(entries, 1):
        print(f"   Procesando entrada {i}/{len(entries)}")
        bibtex_entry = convert_single_ris_entry(entry, ris_to_bibtex_fields, ris_to_bibtex_types)
        if bibtex_entry:
            bibtex_entries.append(bibtex_entry)
    
    print("✅ Conversión completada")
    return '\n\n'.join(bibtex_entries)


def split_ris_entries(content):
    """
    Divide el contenido RIS en entradas individuales
    
    Args:
        content (str): Contenido completo del archivo RIS
    
    Returns:
        list: Lista de entradas RIS individuales
    """
    entries = []
    current_entry = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Si la línea empieza con TY, es una nueva entrada
        if line.startswith('TY  -'):
            # Si ya tenemos una entrada en progreso, la guardamos
            if current_entry:
                entries.append('\n'.join(current_entry))
            # Empezamos una nueva entrada
            current_entry = [line]
        
        # Si la línea es ER  -, terminamos la entrada
        elif line.startswith('ER  -'):
            current_entry.append(line)
            entries.append('\n'.join(current_entry))
            current_entry = []
        
        # Cualquier otra línea va a la entrada actual
        elif current_entry and line:
            current_entry.append(line)
    
    # Agregar la última entrada si no terminó con ER
    if current_entry:
        entries.append('\n'.join(current_entry))
    
    return entries


def convert_single_ris_entry(entry_text, ris_to_bibtex_fields, ris_to_bibtex_types):
    """
    Convierte una sola entrada RIS a formato BibTeX
    
    Args:
        entry_text (str): Texto de una entrada RIS
        ris_to_bibtex_fields (dict): Equivalencias de campos RIS → BibTeX
        ris_to_bibtex_types (dict): Equivalencias de tipos RIS → BibTeX
    
    Returns:
        str: Entrada en formato BibTeX
    """
    # Parsear la entrada RIS
    entry_info = parse_ris_entry(entry_text)
    
    if not entry_info:
        return ""
    
    # Determinar el tipo BibTeX
    ris_type = entry_info.get('type', 'GEN')
    bibtex_type = ris_to_bibtex_types.get(ris_type, '@misc')  # @misc por defecto
    
    # Generar clave única si no existe
    entry_key = entry_info.get('id', generate_entry_key(entry_info))
    
    # Comenzar a construir la entrada BibTeX
    bibtex_lines = [f"{bibtex_type}{{{entry_key},"]
    
    # Convertir campos
    fields = entry_info.get('fields', {})
    
    # Campos especiales que necesitan procesamiento
    processed_fields = {}
    
    # Procesar autores y editores (pueden tener múltiples líneas)
    if 'AU' in fields:
        authors = ' and '.join(fields['AU'])
        processed_fields['author'] = authors
    
    if 'ED' in fields:
        editors = ' and '.join(fields['ED'])
        processed_fields['editor'] = editors
    
    # Procesar palabras clave (pueden tener múltiples líneas)
    if 'KW' in fields:
        keywords = ', '.join(fields['KW'])
        processed_fields['keywords'] = keywords
    
    # Procesar páginas (SP y EP se combinan)
    if 'SP' in fields or 'EP' in fields:
        start_page = fields.get('SP', [''])[0]
        end_page = fields.get('EP', [''])[0]
        
        if start_page and end_page and start_page != end_page:
            processed_fields['pages'] = f"{start_page}--{end_page}"
        elif start_page:
            processed_fields['pages'] = start_page
    
    # Procesar otros campos normales
    for ris_tag, values in fields.items():
        # Saltar campos ya procesados
        if ris_tag in ['AU', 'ED', 'KW', 'SP', 'EP']:
            continue
        
        # Buscar equivalencia en BibTeX
        bibtex_field = ris_to_bibtex_fields.get(ris_tag)
        
        if bibtex_field and values:
            # Tomar el primer valor si hay múltiples
            value = values[0] if isinstance(values, list) else values
            processed_fields[bibtex_field] = value
    
    # Formatear campos en BibTeX
    field_lines = []
    for field_name, field_value in processed_fields.items():
        if field_value and field_value.strip():
            # Escapar caracteres especiales si es necesario
            clean_value = clean_bibtex_value(field_value)
            field_lines.append(f"  {field_name} = {{{clean_value}}}")
    
    # Agregar campos a la entrada
    bibtex_lines.extend(field_lines)
    bibtex_lines.append("}")
    
    return '\n'.join(bibtex_lines)


def parse_ris_entry(entry_text):
    """
    Parsea una entrada RIS y extrae su información
    
    Args:
        entry_text (str): Texto de la entrada RIS
    
    Returns:
        dict: Información extraída de la entrada
    """
    entry_info = {'fields': {}}
    
    lines = entry_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line == 'ER  -':
            continue
        
        # Patrón para líneas RIS: TAG  - valor
        match = re.match(r'^([A-Z0-9]{1,2})\s*-\s*(.*)$', line)
        
        if match:
            tag = match.group(1)
            value = match.group(2).strip()
            
            if tag == 'TY':
                entry_info['type'] = value
            elif tag == 'ID':
                entry_info['id'] = value
            else:
                # Para campos que pueden tener múltiples valores (como AU, KW)
                if tag not in entry_info['fields']:
                    entry_info['fields'][tag] = []
                entry_info['fields'][tag].append(value)
    
    # Convertir campos con un solo valor de lista a string
    for tag, values in entry_info['fields'].items():
        if len(values) == 1 and tag not in ['AU', 'ED', 'KW']:  # Mantener como lista los que pueden tener múltiples valores
            entry_info['fields'][tag] = values[0]
    
    return entry_info


def generate_entry_key(entry_info):
    """
    Genera una clave única para la entrada BibTeX si no existe ID
    
    Args:
        entry_info (dict): Información de la entrada
    
    Returns:
        str: Clave generada
    """
    # Intentar usar autor y año
    fields = entry_info.get('fields', {})
    
    # Obtener primer autor
    authors = fields.get('AU', [])
    if authors:
        first_author = authors[0]
        # Extraer apellido (parte antes de la coma)
        author_parts = first_author.split(',')
        if author_parts:
            author_key = author_parts[0].strip().replace(' ', '').lower()
        else:
            author_key = first_author.replace(' ', '').lower()
    else:
        author_key = "unknown"
    
    # Obtener año
    year = fields.get('PY', [''])[0] if isinstance(fields.get('PY'), list) else fields.get('PY', '')
    if isinstance(year, str) and year:
        year_match = re.search(r'\d{4}', year)
        year_key = year_match.group() if year_match else "0000"
    else:
        year_key = "0000"
    
    return f"{author_key}{year_key}"


def clean_bibtex_value(value):
    """
    Limpia un valor para usarlo en BibTeX
    
    Args:
        value (str): Valor original
    
    Returns:
        str: Valor limpio para BibTeX
    """
    # Remover espacios extra
    clean_value = re.sub(r'\s+', ' ', value.strip())
    
    # Escapar caracteres especiales si es necesario
    # (Por simplicidad, solo limpiamos espacios por ahora)
    
    return clean_value
