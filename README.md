# LINE 老師提醒系統

一個簡單易用的 LINE 官方帳號老師提醒系統，支援多帳號管理、自動每日提醒、課程表管理。

## 功能特性

- ✅ 支援 2 個 LINE 官方帳號
- ✅ 自動捕獲老師 User ID（無需手動輸入）
- ✅ 網頁介面管理老師和課程表
- ✅ 每天上午 8:00 AM 自動發送提醒
- ✅ 自訂提醒訊息
- ✅ 獨立的帳號管理

## 快速開始

### 本地測試

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 執行應用程式
python3 app_simple.py
```

訪問 http://localhost:8080

### 部署到 Render

詳見 `DEPLOY.md`

## 系統架構

- **Flask**: 網頁伺服器和 API
- **LINE Messaging API**: 訊息接收和發送
- **SQLite**: 資料庫
- **APScheduler**: 定時任務（每日提醒）

## 環境變數

```
CHANNEL_1_ACCESS_TOKEN=<your_channel_1_access_token>
CHANNEL_1_SECRET=<your_channel_1_secret>
CHANNEL_2_ACCESS_TOKEN=<your_channel_2_access_token>
CHANNEL_2_SECRET=<your_channel_2_secret>
```

## 使用說明

1. **老師發送訊息**
   - 老師向您的 LINE 官方帳號發送任何訊息
   - 系統自動捕獲老師的 User ID 和顯示名稱

2. **管理課程表**
   - 在網頁介面中選擇老師
   - 設定每週課程日期

3. **自動提醒**
   - 系統會在每天上午 8:00 AM 檢查課程表
   - 自動向有課程的老師發送提醒訊息

## 部署

推薦使用 Render 進行部署（免費或付費方案）。

詳見 `DEPLOY.md` 文件。

## 常見問題

**Q: 系統如何知道老師的名稱？**
A: 系統會自動讀取老師在 LINE 上的顯示名稱。

**Q: 可以自訂提醒訊息嗎？**
A: 可以，在網頁介面的「設定」中修改提醒訊息模板。

**Q: 支援多少個老師？**
A: 沒有限制，可以無限新增。

**Q: 免費方案有什麼限制？**
A: Render 免費方案在 15 分鐘無活動後會進入休眠。推薦使用付費方案（$7/月）以獲得 24/7 運行。

## 技術支援

如有問題，請檢查：
1. Webhook URL 是否正確設定
2. Channel Access Token 和 Secret 是否正確
3. 應用程式日誌中是否有錯誤訊息

