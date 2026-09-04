from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Calculator</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 32px;
            width: 340px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        h2 {
            margin-top: 0;
            color: #58a6ff;
            text-align: center;
        }
        .input-group {
            margin-bottom: 16px;
        }
        label {
            display: block;
            font-size: 13px;
            color: #8b949e;
            margin-bottom: 6px;
        }
        input {
            width: 100%;
            padding: 10px 12px;
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #fff;
            font-size: 15px;
            box-sizing: border-box;
            outline: none;
        }
        input:focus {
            border-color: #58a6ff;
        }
        .buttons {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 20px;
        }
        button {
            padding: 12px;
            background-color: #21262d;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        button:hover {
            background-color: #30363d;
            border-color: #8b949e;
            color: #58a6ff;
        }
        .result-box {
            margin-top: 24px;
            padding: 14px;
            background: #0d1117;
            border: 1px dashed #30363d;
            border-radius: 6px;
            text-align: center;
        }
        .result-title {
            font-size: 12px;
            color: #8b949e;
            margin-bottom: 4px;
        }
        .result-val {
            font-size: 20px;
            font-weight: 600;
            color: #3fb950;
        }
        .error {
            color: #f85149;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Vibe Calc</h2>
        
        <div class="input-group">
            <label>Число A</label>
            <input type="number" id="numA" placeholder="Введите число" value="10">
        </div>
        
        <div class="input-group">
            <label>Число B</label>
            <input type="number" id="numB" placeholder="Введите число" value="5">
        </div>

        <div class="buttons">
            <button onclick="calculate('add')">+</button>
            <button onclick="calculate('sub')">−</button>
            <button onclick="calculate('mul')">×</button>
            <button onclick="calculate('div')">÷</button>
        </div>

        <div class="result-box">
            <div class="result-title">Результат бэкенда</div>
            <div id="output" class="result-val">—</div>
        </div>
    </div>

    <script>
        async function calculate(op) {
            const a = document.getElementById('numA').value;
            const b = document.getElementById('numB').value;
            const out = document.getElementById('output');

            if (a === '' || b === '') {
                out.className = 'result-val error';
                out.innerText = 'Заполните поля';
                return;
            }

            try {
                const res = await fetch(`/api/calc?op=${op}&a=${a}&b=${b}`);
                const data = await res.json();
                
                if (res.ok) {
                    out.className = 'result-val';
                    out.innerText = data.result;
                } else {
                    out.className = 'result-val error';
                    out.innerText = data.detail;
                }
            } catch (err) {
                out.className = 'result-val error';
                out.innerText = 'Ошибка сети';
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def get_ui():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/api/calc")
def calculate_api(op: str, a: float, b: float):
    from fastapi import HTTPException

    if op == "add":
        return {"result": a + b}
    elif op == "sub":
        return {"result": a - b}
    elif op == "mul":
        return {"result": a * b}
    elif op == "div":
        if b == 0:
            raise HTTPException(status_code=400, detail="Деление на ноль!")
        return {"result": a / b}
    else:
        raise HTTPException(status_code=400, detail="Неизвестная операция")