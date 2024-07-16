import gspread
from oauth2client.service_account import ServiceAccountCredentials
from decouple import config
import pandas as pd
from src.utils.credentials import credentials
import ast

def hotelDummies():
    try:
        json_credenciales = credentials()
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credenciales = ServiceAccountCredentials.from_json_keyfile_dict(json_credenciales, scope)
        gc = gspread.authorize(credenciales)
        
        spreadsheet = gc.open_by_url(config('HOTELS_URL'))
        hotels_looker_sheet = spreadsheet.worksheet('hotels_looker')
        hotels_looker_sheet.clear()
        
        hotels_df_sheet = spreadsheet.worksheet('hotels_df')

        data = hotels_df_sheet.get_all_values()
        hotels_df = pd.DataFrame(data[1:], columns=data[0])

        hotels_df = hotels_df.drop_duplicates(subset=['hotel_title'], keep='last')

        hotels_df['features'] = hotels_df['features'].apply(ast.literal_eval)
        df_features_dummies = pd.get_dummies(hotels_df['features'].apply(pd.Series).stack()).groupby(level=0).sum()
        hotels_df = pd.concat([hotels_df, df_features_dummies], axis=1)
        hotels_df = hotels_df.drop('features', axis=1)

        # Reemplazar valores NaN e infinitos
        hotels_df = hotels_df.replace([float('inf'), float('-inf')], 0)
        hotels_df = hotels_df.fillna(0)

        # Convertir todos los valores a cadenas
        new_data = [hotels_df.columns.values.tolist()] + hotels_df.astype(str).values.tolist()
        hotels_looker_sheet.update(new_data)

        return ("The hotels were dummies successfully!"), 201

    except gspread.exceptions.GSpreadException as e:
        return (f"Google Sheets error: {e}"), 400
    except KeyError as e:
        return (f"Key error: {e}"), 400
    except ValueError as e:
        return (f"Value error: {e}"), 400
    except Exception as e:
        return (f"Unexpected error: {e}"), 400
