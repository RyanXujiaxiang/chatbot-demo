from flask import Flask, request, jsonify, render_template
import requests
import time

app = Flask(__name__)

# 配置你的学校 API 信息
apiKey = "7494a97a-bc8f-4f53-9931-f896c1c45982"
basicUrl = "https://genai.hkbu.edu.hk/general/rest"
modelName = "gpt-4-o"
apiVersion = "2024-10-21"

@app.route('/')
def index():
    age = request.args.get("age", "unknown")
    return render_template("chat.html", age=age)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "")
    age = data.get("age", "unknown")

    # 构建 messages 列表
    messages = [
        {"role": "system", "content": f"You are a helpful assistant talking to a {age}-year-old user."},
        {"role": "user", "content": user_message}
    ]

    # 构建请求
    url = f"{basicUrl}/deployments/{modelName}/chat/completions/?api-version={apiVersion}"
    headers = {'Content-Type': 'application/json', 'api-key': apiKey}
    payload = {'messages': messages}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content']
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': f"API Error: {response.status_code} - {response.text}"})
    except requests.exceptions.RequestException as e:
        return jsonify({'reply': f"Connection Error: {str(e)}"})

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render 会自动提供 PORT 环境变量
    app.run(host='0.0.0.0', port=port, debug=True)