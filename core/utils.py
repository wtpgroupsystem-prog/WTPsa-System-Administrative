from datetime import datetime

def obtener_mes_actual():
    return datetime.now().strftime('%B')

def formatear_fecha(fecha):
    return fecha.strftime('%d/%m/%Y')
