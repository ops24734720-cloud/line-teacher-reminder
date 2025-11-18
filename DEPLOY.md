# 部署到 Render - 完整指南

## 步驟 1：準備 GitHub 倉庫

### 1.1 建立新倉庫

1. 進入 https://github.com/new
2. 倉庫名稱：`line-teacher-reminder`
3. 選擇 **Public**
4. 點擊 **Create repository**

### 1.2 上傳代碼

```bash
# 複製倉庫
git clone https://github.com/YOUR_USERNAME/line-teacher-reminder.git
cd line-teacher-reminder

# 複製以下文件到此目錄：
# - app_simple.py
# - requirements.txt
# - Procfile
# - README.md
# - .gitignore

# 上傳到 GitHub
git add .
git commit -m "Initial commit: LINE teacher reminder system"
git push origin main
```

## 步驟 2：在 Render 上部署

### 2.1 建立 Web Service

1. 進入 https://render.com
2. 點擊 **Sign Up**（推薦用 GitHub 帳號登入）
3. 授權 GitHub
4. 點擊 **New +** → **Web Service**
5. 選擇 **Connect a repository**
6. 選擇 `line-teacher-reminder` 倉庫
7. 點擊 **Connect**

### 2.2 配置部署設定

填寫以下欄位：

| 欄位 | 值 |
|------|-----|
| **Name** | `line-teacher-reminder` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT app_simple:app` |
| **Plan** | Free 或 Paid |

### 2.3 新增環境變數

點擊 **Environment** 標籤，新增以下 4 個環境變數：

```
CHANNEL_1_ACCESS_TOKEN
值: oDuJRb/q7oBHUobgLQC/i7/Pg/6Z6EME4/Z7W2h1OrtH0+DAxmsLBeSyvHHn1SViyEe5rHJZqg2o7ZP3RnK/V0aw/uBISldppxPf0GqzUAWGDMPN62nfwfdjBCj0ZG/71uQpqJVQXJ9JYSr0JF0ZQQdB04t89/1O/w1cDnyilFU=

CHANNEL_1_SECRET
值: cb58ea355a8c2a01259cd1dc33704264

CHANNEL_2_ACCESS_TOKEN
值: OvwM4sNCR0rVtI8e4EdBeqHLIxAKHg6CiPef66s/g9ONcTRujuGGp5UnUtrLSwvuGjRPxGZiadZfiBL9juCO8IpiK99RAD5NmzCs6pCNt+b+XL1z0JubWAkDnZE++81JOPSSRpxYoZ+p0bdg8p8HXwdB04t89/1O/w1cDnyilFU=

CHANNEL_2_SECRET
值: 5aba0d7769b5e4468ac1855e78f4e5c8
```

### 2.4 開始部署

點擊 **Create Web Service**，等待部署完成（通常 2-5 分鐘）。

部署完成後，您會看到一個公開 URL，例如：
```
https://line-teacher-reminder.onrender.com
```

## 步驟 3：更新 LINE Developers Console

### 3.1 更新 Webhook URL

1. 進入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Channel
3. 進入 **Messaging API** 設定
4. 找到 **Webhook URL** 欄位
5. 更新為：
   - **帳號 1**: `https://line-teacher-reminder.onrender.com/callback/account1`
   - **帳號 2**: `https://line-teacher-reminder.onrender.com/callback/account2`
6. 點擊 **Verify** 進行驗證

### 3.2 確保 Webhook 已啟用

確保 **"Use webhook"** 開關是 **ON**

## 步驟 4：測試系統

1. 用測試帳號向您的 LINE 官方帳號發送訊息
2. 訪問 `https://line-teacher-reminder.onrender.com`
3. 查看是否顯示了捕獲的老師資訊

## 常見問題

### Q: 如何更新應用程式？

在本地修改代碼後：
```bash
git add .
git commit -m "Update description"
git push origin main
```

Render 會自動檢測到變更並重新部署。

### Q: 如何查看應用程式日誌？

1. 進入 Render Dashboard
2. 選擇您的 Web Service
3. 點擊 **Logs** 標籤查看實時日誌

### Q: 免費方案有什麼限制？

- 15 分鐘無活動後會進入休眠
- 重新喚醒需要幾秒鐘
- 推薦使用付費方案（$7/月）以獲得 24/7 運行

### Q: 如何停止或刪除應用程式？

1. 進入 Render Dashboard
2. 選擇您的 Web Service
3. 點擊 **Settings** → **Delete Web Service**

### Q: 訊息無法接收怎麼辦？

1. 檢查 Webhook URL 是否正確
2. 檢查 Channel Access Token 和 Secret 是否正確
3. 在 Render Dashboard 中查看日誌，看是否有錯誤訊息

### Q: 訊息無法發送怎麼辦？

1. 確認老師已經向官方帳號發送過訊息（系統才能捕獲 User ID）
2. 檢查課程表是否正確設定
3. 檢查 Channel Access Token 是否有效

## 需要幫助？

如有其他問題，請：
1. 檢查 Render 的應用程式日誌
2. 檢查 LINE Developers Console 的 Webhook 驗證狀態
3. 確保所有環境變數都正確設定

