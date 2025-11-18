# 🚀 快速部署指南 - 5 分鐘完成

## 準備工作

- GitHub 帳號（https://github.com）
- Render 帳號（https://render.com）

## 第 1 步：建立 GitHub 倉庫（1 分鐘）

1. 進入 https://github.com/new
2. 倉庫名稱：`line-teacher-reminder`
3. 選擇 **Public**
4. 點擊 **Create repository**

## 第 2 步：上傳代碼（1 分鐘）

在您的電腦上打開命令行：

```bash
# 複製倉庫
git clone https://github.com/YOUR_USERNAME/line-teacher-reminder.git
cd line-teacher-reminder

# 將此部署包中的所有文件複製到此目錄

# 上傳到 GitHub
git add .
git commit -m "Initial commit"
git push origin main
```

## 第 3 步：在 Render 上部署（2 分鐘）

### 3.1 連接 GitHub

1. 進入 https://render.com
2. 點擊 **Sign Up**（用 GitHub 帳號登入）
3. 授權 GitHub 帳號

### 3.2 建立 Web Service

1. 點擊 **New +** → **Web Service**
2. 點擊 **Connect a repository**
3. 選擇 `line-teacher-reminder` 倉庫
4. 點擊 **Connect**

### 3.3 配置設定

填寫以下內容：

```
Name: line-teacher-reminder
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app_simple:app
Plan: Free (或 Paid)
```

### 3.4 新增環境變數

點擊 **Environment** 標籤，新增以下變數：

| 名稱 | 值 |
|------|-----|
| CHANNEL_1_ACCESS_TOKEN | `oDuJRb/q7oBHUobgLQC/i7/Pg/6Z6EME4/Z7W2h1OrtH0+DAxmsLBeSyvHHn1SViyEe5rHJZqg2o7ZP3RnK/V0aw/uBISldppxPf0GqzUAWGDMPN62nfwfdjBCj0ZG/71uQpqJVQXJ9JYSr0JF0ZQQdB04t89/1O/w1cDnyilFU=` |
| CHANNEL_1_SECRET | `cb58ea355a8c2a01259cd1dc33704264` |
| CHANNEL_2_ACCESS_TOKEN | `OvwM4sNCR0rVtI8e4EdBeqHLIxAKHg6CiPef66s/g9ONcTRujuGGp5UnUtrLSwvuGjRPxGZiadZfiBL9juCO8IpiK99RAD5NmzCs6pCNt+b+XL1z0JubWAkDnZE++81JOPSSRpxYoZ+p0bdg8p8HXwdB04t89/1O/w1cDnyilFU=` |
| CHANNEL_2_SECRET | `5aba0d7769b5e4468ac1855e78f4e5c8` |

### 3.5 開始部署

點擊 **Create Web Service**

等待 2-5 分鐘，部署完成！您會看到一個 URL，例如：
```
https://line-teacher-reminder.onrender.com
```

## 第 4 步：更新 LINE Webhook URL（1 分鐘）

1. 進入 [LINE Developers Console](https://developers.line.biz/console/)
2. 選擇您的 Channel
3. 進入 **Messaging API** 設定
4. 找到 **Webhook URL** 欄位
5. 更新為：
   - **帳號 1**: `https://line-teacher-reminder.onrender.com/callback/account1`
   - **帳號 2**: `https://line-teacher-reminder.onrender.com/callback/account2`
6. 點擊 **Verify** 驗證

## 完成！✅

您的系統現在已部署到 Render！

- 網頁介面：`https://line-teacher-reminder.onrender.com`
- 系統會每天上午 8:00 AM 自動發送提醒

## 下一步

1. 用測試帳號向您的 LINE 官方帳號發送訊息
2. 在網頁介面中設定課程表
3. 系統會自動發送每日提醒

## 需要幫助？

詳見 `DEPLOY.md` 文件。

