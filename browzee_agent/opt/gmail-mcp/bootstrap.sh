#!/usr/bin/env bash
set -e
docker compose up -d gmail-mcp
echo "📣 פתח דפדפן והשלם את ה‑OAuth:"
echo "   http://localhost:8080/auth"   # ה‑Image מפעיל דף auth על 3000
sleep 3
xdg-open http://localhost:8080/auth 2>/dev/null || start http://localhost:8080/auth
echo "לאחר אישור ‑ Ctrl+C והמשך."