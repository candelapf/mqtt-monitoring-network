import json




def read_report(file_path, LAST_LINE, num_lines):
    """
    Read the next num_lines from a file.

lines <class 'str'> 0,0,94,21,97,36.2,Normal
    :param file_path: path to the file
    :param LAST_LINE: last line read
    :param num_lines: number of lines to read

    :returns: a list of read lines
    """
    
    with open(file_path, 'r') as fichero:
    	
    	lineas= fichero.readlines() 
    	
    	lineas_aleer = lineas[LAST_LINE: LAST_LINE + num_lines]


    return lineas_aleer
    

def line_to_json(line):
    # 1. Quitamos espacios al principio y final
    line = line.strip()
    
    # 2. Separamos por comas
    campos = line.split(',')
    
    # 3. Creamos un diccionario con las claves que queremos
    dic = {
        "Idx": campos[0],
        "Time": campos[1],
        "HR": campos[2],
        "RESP": campos[3],
        "SpO2": campos[4],
        "TEMP": campos[5],
        "OUTPUT": campos[6]
    }
    
    # 4. Convertimos el diccionario a JSON
    return json.dumps(dic)




def line_to_dict(fpath, line):
    # disponer de un diccionario que almacena el valor asociado a cada medida de metrica biometrica (oxıgeno, frecuencia cardiaca)
    
    with open(fpath, 'r') as fichero:
        
        lineas= fichero.readlines()
        if line > len(lineas):
            return None  # fuera de rango (quieres leer una línea que no existe)
        linea_aleer = lineas[line] #aqui en linea_aleer tendría el contenido de la linea
        linea = linea_aleer.strip()
        if not linea_aleer:  # línea vacía
            return None
        campos = linea.split(',')

        try:
            dic2 = {
            "idx": int(campos[0]),
            "time": int(campos[1]),
            "hr": int(campos[2]),
            "resp": int(campos[3]),
            "SpO2": int(campos[4]),
            "temp": float(campos[5]),
            "output": campos[6]
            }
        except ValueError as e:
            print(f"Error convirtiendo línea {line}: {e}")
            return None
        return dic2


if __name__ == "__main__":
    read_report(file_path, LAST_LINE, num_lines)
    line_to_json(line)
    line_to_dict(fpath, line)