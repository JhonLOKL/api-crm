import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
import re

from ..utils.credentials import credentials

def lead_crm(data):
    try:
        url_documento = config('CRM_URL')
        user_already_exists = False
        json_credenciales = credentials()
        
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc  = gspread.authorize(credenciales)
        
        documento_id = url_documento.split("/")[5]

        hoja = gc.open_by_key(documento_id)

        nombre_hoja = "CRM (Oportunidad)"
        hoja_crm = hoja.worksheet(nombre_hoja)

        data_crm = hoja_crm.get_all_values()[1:]  # Omitir la primera fila (encabezados)

        # Convertir la lista de listas en un DataFrame
        crm_oportunidad = pd.DataFrame(data_crm, columns=hoja_crm.get_all_values()[0])

        # Limpieza de datos del teléfono en CRM
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\+', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\=', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r"\'", "", regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace("'", "")
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'\(.*?\)', '', regex=True)
        crm_oportunidad['Celular'] = crm_oportunidad['Celular'].str.replace(r'^57', '', regex=True)

        # Limpieza de teléfono recibido
        phone_to_check = ''
        if 'phone' in data and data['phone']:
            phone_to_check = data['phone']
            phone_to_check = re.sub(r'\(.*?\)', '', phone_to_check)  # Eliminar paréntesis si existen
            phone_to_check = phone_to_check.replace('+', '').replace("'", "").replace('=', '').replace('-', '')
            if phone_to_check.startswith('57'):  # Eliminar código de país si es necesario
                phone_to_check = phone_to_check[2:]

        # Verificar si el usuario ya existe por teléfono
        if not user_already_exists and 'phone' in data and data['phone']:
            user_already_exists = phone_to_check in crm_oportunidad['Celular'].values

        # Si el usuario no existe, agregarlo al CRM
        if not user_already_exists:
            spreadsheet = gc.open_by_url(config('CRM_URL'))
            
            # Verificar si 'data' contiene las claves necesarias
            if not data.get('phone'):
                data['phone'] = ''
            if not data.get('email'):
                data['email'] = ''

            # Procesar fecha y hora de creación
            created_at = data.get('createdAt')
            if created_at:
                entry_date = pd.to_datetime(created_at).strftime('%d/%m/%Y')
                entry_time = pd.to_datetime(created_at).strftime('%H:%M')
            else:
                entry_date = None
                entry_time = None

            # Crear el nuevo registro en el DataFrame
            df = pd.DataFrame({
                'Nombre': [data.get('name', '')],
                'Apellido': [""],
                'Celular': [data.get('phone', '')],
                'Email': [data.get('email', '')],
                'Como nos conocio': [data.get('leadOrigin', '')],
                'Origen': "Agente IA",
                'Proyecto': ["Nido de Agua"],
                'Fecha ingreso': [entry_date],
                'Hora Ingreso': [entry_time],
                'Fecha Atención': None,
                'Hora Atención': None,
                'Tiempo Atención': None,
                'Tiempo en atencion en horas': None,
                'Estado Oportunidad': "Interesado",
            })

            # Obtener la hoja de trabajo
            sheet_title = 'CRM (Oportunidad)'
            worksheet = spreadsheet.worksheet(sheet_title)
            empty_rows = [i + 2 for i, row in enumerate(worksheet.get_all_values()[1:]) if not any(row[0:4])]

            if empty_rows:
                # Asegurarse de que los valores en el DataFrame tengan el formato correcto
                columnas_df = df.columns.tolist()
                columnas_hoja = worksheet.row_values(1)
                values = df[columnas_df].values.tolist()

                for row in values:
                    while len(row) < len(columnas_hoja):
                        row.append('')

                # Insertar los datos en las filas vacías
                for row_index, value_row in zip(empty_rows, values):
                    worksheet.update(f'A{row_index}', [value_row])

                return "Usuario agregado correctamente a CRM."
            else:
                return "No hay filas vacías para agregar datos."

        else:
            return "El usuario ya existe, no es necesario agregarlo a CRM."
    
    except Exception as error:
        print("Se produjo un error:", error)
        return "Error guardando el lead desde Laura"

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from decouple import config
import re

from ..utils.credentials import credentials

def update_lead(data):
    try:
        url_documento = config('CRM_URL')

        # Iniciar sesión con las credenciales de Google
        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc = gspread.authorize(credenciales)

        documento_id = url_documento.split("/")[5]
        hoja = gc.open_by_key(documento_id)

        nombre_hoja = "CRM (Oportunidad)"
        hoja_crm = hoja.worksheet(nombre_hoja)

        data_crm = hoja_crm.get_all_values()[1:]  # Omitir la primera fila (encabezados)

        # Convertir la lista de listas en un DataFrame
        crm_oportunidad = pd.DataFrame(data_crm, columns=hoja_crm.get_all_values()[0])

        # Eliminar espacios extra antes y después de las columnas
        crm_oportunidad.columns = crm_oportunidad.columns.str.strip()

        # Normalización del teléfono
        phone_to_check = data.get('phone', '')
        phone_to_check = re.sub(r'\(.*?\)', '', phone_to_check)  # Eliminar paréntesis si existen
        phone_to_check = phone_to_check.replace('+', '').replace("'", "").replace('=', '').replace('-', '')
        if phone_to_check.startswith('57'):  # Eliminar código de país si es necesario
            phone_to_check = phone_to_check[2:]

        # Buscar las filas que tengan el teléfono en cualquier parte del texto (no solo exacto)
        rows_to_update = crm_oportunidad[crm_oportunidad['Celular'].str.contains(phone_to_check, na=False)]

        if rows_to_update.empty:
            return f"No se encontraron registros con el teléfono {phone_to_check}. No se actualizaron datos."

        # Si se encuentran registros, proceder con la actualización
        updated_rows = []
        for index, row in rows_to_update.iterrows():
            updated_row = row.tolist()
            
            # Verificamos si los campos son no nulos antes de actualizar
            if data.get('firstName') and data['firstName'] != '':
                updated_row[crm_oportunidad.columns.get_loc('Nombre')] = data['firstName']
            if data.get('lastName') and data['lastName'] != '':
                updated_row[crm_oportunidad.columns.get_loc('Apellido')] = data['lastName']
            if data.get('email') and data['email'] != '':
                updated_row[crm_oportunidad.columns.get_loc('Email')] = data['email']
            if data.get('status') and data['status'] != '':
                updated_row[crm_oportunidad.columns.get_loc('Estado Oportunidad')] = data['status']
                
            if data.get('utmSource') and data['utmSource'] != '':
                updated_row[crm_oportunidad.columns.get_loc('utmSource')] = data['utmSource']
            if data.get('utmMedium') and data['utmMedium'] != '':
                updated_row[crm_oportunidad.columns.get_loc('utmMedium')] = data['utmMedium']
            if data.get('utmCampaign') and data['utmCampaign'] != '':
                updated_row[crm_oportunidad.columns.get_loc('utmCampaign')] = data['utmCampaign']
            if data.get('utmTerm') and data['utmTerm'] != '':
                updated_row[crm_oportunidad.columns.get_loc('utmTerm')] = data['utmTerm']
            if data.get('utmContent') and data['utmContent'] != '':
                updated_row[crm_oportunidad.columns.get_loc('utmContent')] = data['utmContent']

            # Reemplazar valores NaN o None con un valor por defecto
            updated_row = ["" if pd.isna(value) else value for value in updated_row]

            updated_rows.append(updated_row)

        # Ahora actualizamos las filas de la hoja de cálculo
        # Usamos el índice + 2 porque en la hoja de cálculo, la primera fila son los encabezados
        sheet_title = 'CRM (Oportunidad)'
        spreadsheet = gc.open_by_url(config('CRM_URL'))
        worksheet = spreadsheet.worksheet(sheet_title)

        for row_index, updated_row in zip(rows_to_update.index, updated_rows):
            worksheet.update(f"A{row_index + 2}", [updated_row])

        return f"Registros actualizados correctamente con el teléfono {phone_to_check}."

    except Exception as error:
        print("Se produjo un error:", error)
        return "Error al actualizar el lead."
