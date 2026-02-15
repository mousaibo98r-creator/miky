# ⚡ QUICK START GUIDE

## 🎯 Goal
Fix the "Model returned text instead of JSON" error and enable real-time data refresh in your Antigravity Intelligence Matrix.

---

## 🚀 Installation (5 minutes)

### Option 1: Automatic Install (Recommended)
```bash
# 1. Download the antigravity_fix folder
# 2. Navigate to it
cd antigravity_fix

# 3. Run the installer
chmod +x install.sh
./install.sh
```

### Option 2: Manual Install
```bash
# 1. Backup your files
mkdir backup
cp app.py backup/
cp services/*.py backup/services/

# 2. Copy new files
cp antigravity_fix/deepseek_client.py YOUR_PROJECT/
cp antigravity_fix/services/*.py YOUR_PROJECT/services/
cp antigravity_fix/app.py YOUR_PROJECT/

# 3. Install dependencies
pip install -r antigravity_fix/requirements.txt
```

---

## ✅ Verify Installation

### 1. Check Files
```bash
ls -la deepseek_client.py services/search_agent.py services/database.py
```
All three should exist.

### 2. Check Environment
```bash
cat .env
```
Should contain:
```
SUPABASE_URL=...
SUPABASE_KEY=...
DEEPSEEK_API_KEY=...
```

### 3. Test Run
```bash
streamlit run app.py
```

---

## 🧪 Test the Fix

1. **Open your app** (http://localhost:8501)

2. **Select a company** in the table (e.g., "FERO METAL INC.")

3. **Click "🔍 Scavenge Data"** in the right panel

4. **Watch for success indicators:**
   - ✅ "Scavenge Complete!" (not error)
   - 📊 "Found: X email(s), Y phone(s), website"
   - ✅ "Saved 2 emails, 1 phones"
   - 🔄 UI refreshes automatically

5. **Verify data appears:**
   - Email visible in table
   - Phone visible in table
   - Stats card updated (EMAILS count increased)

---

## ❓ Troubleshooting

### Error: "DEEPSEEK_API_KEY not found"
**Fix:** Add to .env file:
```bash
echo "DEEPSEEK_API_KEY=your_key_here" >> .env
```

### Error: "No module named 'deepseek_client'"
**Fix:** Make sure deepseek_client.py is in project root:
```bash
cp antigravity_fix/deepseek_client.py .
```

### Error: "Cannot find company"
**Fix:** This is normal for some companies. Try:
- Different company name
- Check spelling
- Wait 30 seconds (rate limits)

### Error: "Supabase connection failed"
**Fix:** Check credentials:
```bash
python -c "from services.database import get_supabase; print(get_supabase())"
```

---

## 📊 What Changed?

### Before ❌:
- "Model returned text instead of JSON"
- No data saved
- Manual refresh needed

### After ✅:
- Clean JSON responses
- Data saves automatically
- UI refreshes immediately

---

## 📖 Full Documentation

- **README.md** - Complete installation guide
- **CHANGES.md** - Detailed technical changes
- **requirements.txt** - Dependencies list

---

## 🎉 Success Checklist

- [ ] Installation completed without errors
- [ ] App starts successfully
- [ ] Can search for company
- [ ] Gets "✅ Scavenge Complete!" message
- [ ] Data appears in table
- [ ] Stats card updates
- [ ] No more JSON errors

**All checked? You're all set! 🚀**

---

## 🆘 Still Having Issues?

1. Check logs in terminal
2. Review README.md troubleshooting section
3. Verify all files copied correctly:
   ```bash
   ls -la deepseek_client.py
   ls -la services/search_agent.py
   ls -la services/database.py
   ```

---

**Need more help? Review the detailed CHANGES.md for technical deep-dive.**
