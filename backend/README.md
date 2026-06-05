# FastAPI Local Model Backend

这个后端提供两个 AI 营销接口：

- `POST /api/seo-keywords`：SEO 关键词生成
- `POST /api/copywriting`：宣传文案生成

## 启动

```powershell
cd D:\tool\backend
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

按需调整 `.env` 里的本地模型地址和模型名，然后启动：

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

## 本地模型配置

后端会从环境变量或后端目录下的 `.env` 读取配置，环境变量优先级更高。

开发环境：

```text
D:\tool\backend\.env
```

打包后：

```text
安装目录\resources\backend\.env
```

默认配置：

```text
LOCAL_MODEL_BASE_URL=http://192.168.0.124:8081/v1
LOCAL_MODEL_NAME=Qwen3.6-35B-A3B-UD-Q8_K_XL
LOCAL_MODEL_MAX_TOKENS=2048
LOCAL_MODEL_TOP_P=0.9
REQUEST_TIMEOUT_SECONDS=300
```

后端会调用本地 OpenAI-compatible Chat 接口：

```text
POST http://192.168.0.124:8081/v1/chat/completions
```

请求体使用本地 chat-completions 格式：

```json
{
  "model": "Qwen3.6-35B-A3B-UD-Q8_K_XL",
  "messages": [
    { "role": "system", "content": "系统指令" },
    { "role": "user", "content": "用户任务" }
  ],
  "max_tokens": 2048,
  "temperature": 0.7,
  "top_p": 0.9,
  "enable_thinking": false,
  "stream": false
}
```

## SEO 关键词生成示例

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/seo-keywords `
  -Method Post `
  -ContentType 'application/json; charset=utf-8' `
  -Body '{
    "business_description": "智能家居设备",
    "product_features": "支持语音控制，兼容米家和苹果 HomeKit，安装简单",
    "keyword_count": 10,
    "search_engines": ["百度", "360搜索", "必应"]
  }'
```

## 宣传文案生成示例

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/copywriting `
  -Method Post `
  -ContentType 'application/json; charset=utf-8' `
  -Body '{
    "keyword": "智能家居设备推荐",
    "keyword_repeat_count": 2,
    "article_count": 3,
    "platform_styles": ["小红书", "B站"]
  }'
```
