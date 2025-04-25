from flask import Flask, request, jsonify, render_template, session
import requests
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 用于启用 session

# ============ GPT API 配置（使用学校接口） ============
apiKey = "7494a97a-bc8f-4f53-9931-f896c1c45982"
basicUrl = "https://genai.hkbu.edu.hk/general/rest"
modelName = "gpt-4-o"
apiVersion = "2024-10-21"
url = f"{basicUrl}/deployments/{modelName}/chat/completions/?api-version={apiVersion}"
headers = {'Content-Type': 'application/json', 'api-key': apiKey}

# ============ 路由 ============
@app.route('/')
def index():
    age = request.args.get("age", "unknown")
    session['age'] = age  # 将年龄记录在 session 中，便于后续对话使用
    session['history'] = [
        {"role": "system", "content": f"You are chatting with a user who is {age} years old."}
    ]
    return render_template("chat.html")  # age 不再通过 Jinja2 传入

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    age = data.get("age", session.get("age", "unknown"))  # 从请求数据中读取 age，如果没有则回退到 session

    # 初始化聊天历史（如果尚未设置）
    if "history" not in session:
        session['history'] = [
            {"role": "system", "content": f"You are chatting with a user who is {age} years old."}
        ]

    # 添加用户信息到对话历史
    session['history'].append({"role": "user", "content": user_message})

    # 控制上下文长度，避免 token 超限
    session['history'] = session['history'][-10:]  # 只保留最近10轮

    # 发请求到 GPT
    payload = {"messages": session['history']}
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    reply = response.json()['choices'][0]['message']['content']
    print(f"[LOG] {datetime.now().isoformat()} | Age: {age} | User: {user_message} | Bot: {reply}")

    # 添加助手回复到历史
    session['history'].append({"role": "assistant", "content": reply})

    # 保存记录到 chat_log.csv
    with open("chat_log.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            age,
            user_message,
            reply
        ])

    return jsonify({"reply": reply})

# ============ 启动服务 ============
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)