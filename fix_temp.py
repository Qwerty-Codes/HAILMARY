with open('dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """        # Handle missing temperature by pulling from fcast_weather or creating a safe default
        weather_df = results.get('fcast_weather')
        if weather_df is not None and 'temperature' in weather_df.columns:
            # Pad or truncate if lengths don't match, though they should
            temps = weather_df['temperature'].values
            if len(temps) >= len(dash_df):
                dash_df['temperature'] = temps[:len(dash_df)]
            else:
                dash_df['temperature'] = -30.0
        elif 'temperature' not in dash_df.columns:
            dash_df['temperature'] = -30.0
            
        sim_data = dash_df[["load_kw", "temperature", "lp_solar", "lp_wind", "lp_diesel"]].to_dict(orient="records")"""

old_line = '        sim_data = dash_df[["load_kw", "temperature", "lp_solar", "lp_wind", "lp_diesel"]].to_dict(orient="records")'

if old_line in text:
    text = text.replace(old_line, replacement)
    with open('dashboard.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed dashboard.py!')
else:
    print('Line not found!')
