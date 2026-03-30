# Coffee Price Tracker

Theo dõi giá cà phê Việt Nam và thế giới theo thời gian thực.

## Website

**Live**: https://l3duym4nh.github.io/coffee-price/

## Tính năng

- Hiển thị giá 3 loại cà phê: Việt Nam (đ/kg), Robusta London ($/ton), Arabica NY (cents/lb)
- Biểu đồ lịch sử giá 30 ngày
- Click vào thẻ giá hoặc tab để xem biểu đồ từng loại
- Cập nhật tự động hàng ngày lúc 3:00 AM qua GitHub Actions

## Cấu trúc dự án

```
coffee-price/
├── index.html              # Website chính
├── fetch_prices.py         # Script lấy dữ liệu từ giacaphe.com
└── .github/
    └── workflows/
        └── fetch-prices.yml  # GitHub Actions workflow
```

## Nguồn dữ liệu

- **Website**: https://giacaphe.com/
- **Lưu trữ**: GitHub Gist (https://gist.github.com/l3duym4nh/d4d3e60a5fa00da0a7ee0128ac577304)

## GitHub Actions Secrets

Cần thiết lập secret `GH_TOKEN` với quyền Gist để workflow có thể cập nhật dữ liệu:

1. Tạo Personal Access Token tại https://github.com/settings/tokens
2. Cần quyền: `gist`
3. Thêm vào repo secrets: Settings → Secrets → Actions → New repository secret
   - Name: `GH_TOKEN`
   - Value: token đã tạo

## Chạy thủ công

### Lấy giá cà phê

```bash
cd /Users/lemanh/Documents/opencode/coffee-price
python3 fetch_prices.py
```

### Trigger GitHub Actions

Vào https://github.com/l3duym4nh/coffee-price/actions → chọn "Fetch Coffee Prices" → "Run workflow"

### Deploy thủ công

```bash
cd /Users/lemanh/Documents/opencode/coffee-price
git add .
git commit -m "your changes"
git push
```

## Workflow schedule

- **Cron**: `0 3 * * *` (3:00 AM mỗi ngày)
- **Trigger thủ công**: qua `workflow_dispatch`

## Cập nhật website

1. Chỉnh sửa `index.html`
2. Commit và push:

```bash
cd /Users/lemanh/Documents/opencode/coffee-price
git add index.html
git commit -m "mô tả thay đổi"
git push
```

GitHub Pages sẽ tự động cập nhật trong vài giây.

## Cập nhật script lấy giá

1. Chỉnh sửa `fetch_prices.py`
2. Test local: `python3 fetch_prices.py`
3. Commit và push

## Gỡ lỗi

### Website không load dữ liệu
- Kiểm tra Gist có dữ liệu: https://gist.github.com/l3duym4nh/d4d3e60a5fa00da0a7ee0128ac577304
- Kiểm tra workflow log tại: https://github.com/l3duym4nh/coffee-price/actions

### Workflow thất bại
- Kiểm tra `GH_TOKEN` secret còn hiệu lực
- Kiểm tra giacaphe.com có thể truy cập được

### Regex không khớp
- Fetch thử trang web: `curl -s https://giacaphe.com/ | head -100`
- Cập nhật pattern trong `fetch_prices.py`
