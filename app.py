import pandas as pd
import glob
import random
import os
from dash import Dash, dcc, html, Input, Output, State, no_update

#--- データの読み込み ---
def load_data():
    all_files = glob.glob("*.csv")
    category_map = {}
    
    if not all_files:
        print("CSVファイルが見つかりません。")
        return category_map

    for filename in all_files:
        try:
            try:
                df = pd.read_csv(filename, header=None, encoding='utf-8')
            except:
                df = pd.read_csv(filename, header=None, encoding='shift-jis')
            
            current_cat = None
            for _, row in df.iterrows():
                # A列:カテゴリー, B列:数字
                a_val = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                b_val = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                
                # A列に文字があればカテゴリー更新
                if a_val != "" and a_val != "nan" and not a_val.replace(',', '').replace('-', '').isdigit():
                    current_cat = a_val
                    if current_cat not in category_map:
                        category_map[current_cat] = []
                
                # 数字の取得（B列優先、なければA列の数字）
                target_val = b_val if b_val != "" and b_val != "nan" else (a_val if a_val.replace(',', '').replace('-', '').isdigit() else "")
                
                if current_cat and target_val != "":
                    clean_num = target_val.replace(',', '').strip()
                    if clean_num and clean_num not in category_map[current_cat]:
                        category_map[current_cat].append(clean_num)
                        
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue
            
    return {k: v for k, v in category_map.items() if v}

# データの初期化
data_dict = load_data()
categories = sorted(list(data_dict.keys()))

#--- アプリ作成 ---
app = Dash(__name__)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Instant Roulette</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Noto+Sans+JP:wght@500;900&display=swap');
            body {
                background: #f8fafc;
                font-family: 'Noto Sans JP', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: white;
                padding: 40px;
                border-radius: 30px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                text-align: center;
                width: 90%;
                max-width: 400px;
            }
            .display-box {
                background: #111827;
                color: #10b981;
                font-family: 'Montserrat', sans-serif;
                font-size: 100px;
                height: 200px;
                line-height: 200px;
                border-radius: 20px;
                margin: 30px 0;
                box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
                text-shadow: 0 0 15px rgba(16,185,129,0.4);
            }
            .spin-button {
                background: #4f46e5;
                color: white;
                border: none;
                padding: 18px;
                width: 100%;
                font-size: 22px;
                font-weight: 900;
                border-radius: 15px;
                cursor: pointer;
                transition: transform 0.1s, background 0.2s;
            }
            .spin-button:active {
                transform: scale(0.95);
                background: #4338ca;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.Div([
        html.H1("ROULETTE", style={'margin': '0', 'fontWeight': '900', 'color': '#1e293b'}),
        
        html.Div([
            dcc.Dropdown(
                id='cat-drop',
                options=[{'label': c, 'value': c} for c in categories],
                placeholder="カテゴリーを選択",
                style={'textAlign': 'left'}
            ),
        ], style={'marginTop': '20px'}),

        html.Div("---", id='display-text', className="display-box"),

        html.Button("結果を表示！", id='spin-btn', className="spin-button"),
    ], className="card")
])

#--- コールバック (瞬間表示) ---
@app.callback(
    Output('display-text', 'children'),
    Input('spin-btn', 'n_clicks'),
    State('cat-drop', 'value'),
    prevent_initial_call=True
)
def show_result(n, cat):
    if not cat: 
        return "選択中"
    
    choices = data_dict.get(cat, [])
    if not choices:
        return "なし"
    
    # 瞬間的に1つ選んで返す
    return random.choice(choices)

if __name__ == '__main__':
    app.run(jupyter_mode='inline')
