# Quick Start Guide - Phase B (MongoDB Integration)

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install pymongo>=4.6.0
```

### Step 2: Verify MongoDB is Running
```bash
python backend/test_mongo_connection.py
```

**Expected Output**:
```
============================================================
MongoDB Connection Test
============================================================
✓ MongoDB connection successful!
✓ Available databases: [...]
✓ Collections in 'physioai' database: [...]
✓ Users collection: 0 documents
✓ Sessions collection: 0 documents
============================================================
MongoDB is ready! You can start the Flask server.
============================================================
```

**If MongoDB is not running**:
- Windows: `net start MongoDB` or check Services
- Mac/Linux: `sudo systemctl start mongod`

### Step 3: Start Flask Server
```bash
python backend/app.py
```

**Expected Output**:
```
[MongoDB] Connected successfully to mongodb://localhost:27017
 * Running on http://0.0.0.0:5000
```

---

## ✅ Quick Test Flow

### 1. Test Health Check
```bash
curl http://localhost:5000/ping
```
**Expected**: `{"status":"ok"}`

### 2. Register a User
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@physioai.com",
    "name": "Demo User",
    "age": 30,
    "gender": "male",
    "password": "demo123"
  }'
```
**Expected**: `{"message":"User registered successfully","user_id":"..."}`

### 3. Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@physioai.com",
    "password": "demo123"
  }' \
  -c cookies.txt
```
**Expected**: `{"message":"Login successful",...}`

### 4. Get Exercises
```bash
curl http://localhost:5000/exercises -b cookies.txt
```
**Expected**: List of 10 exercises

### 5. Verify in MongoDB
```bash
mongosh
use physioai
db.users.find().pretty()
```

---

## 🎯 Test Session Persistence

### Complete a Session
1. Start session with 5 exercises
2. Update with landmarks (or skip for testing)
3. End session

### Verify Persistence
```bash
# Check history
curl http://localhost:5000/history -b cookies.txt

# Restart Flask server
# Ctrl+C, then: python backend/app.py

# Check history again - data should still be there!
curl http://localhost:5000/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@physioai.com","password":"demo123"}' \
  -c cookies.txt

curl http://localhost:5000/history -b cookies.txt
```

**Expected**: Sessions persist across server restarts ✅

---

## 🔍 Troubleshooting

### "MongoDB connection failed"
- Ensure MongoDB is installed and running
- Check `MONGO_URI` in `.env` file (default: `mongodb://localhost:27017`)
- Try: `mongosh` to test MongoDB CLI access

### "Authentication required"
- Make sure to save cookies with `-c cookies.txt`
- Use cookies in subsequent requests with `-b cookies.txt`

### "Email already registered"
- This is expected behavior (email uniqueness enforced)
- Use a different email or check existing users in MongoDB

### "Invalid email or password"
- User must be registered first (no auto-registration)
- Check password matches registration

---

## 📊 View Data in MongoDB Compass

1. Download **MongoDB Compass** (GUI tool)
2. Connect to: `mongodb://localhost:27017`
3. Navigate to: `physioai` database
4. View collections:
   - `users` - User accounts
   - `sessions` - Completed sessions

---

## 🎉 Success Criteria

- ✅ MongoDB connects successfully
- ✅ User registration creates document in `users` collection
- ✅ Login works (no auto-registration)
- ✅ Session end saves document in `sessions` collection
- ✅ `/history` returns saved sessions
- ✅ Data persists after server restart
- ✅ Data persists after browser close

---

## 📝 Next Steps

Once testing is complete:

1. **Commit to Git**:
   ```bash
   git add .
   git commit -m "Phase B: MongoDB database integration complete"
   ```

2. **Integrate with Frontend**:
   - Update frontend to use email (not username)
   - Add history display UI
   - Show session details view

3. **Phase C Planning**:
   - Advanced analytics
   - OpenAI report generation
   - Export functionality

---

**Need help?** Check `PHASE_B_IMPLEMENTATION_SUMMARY.md` for detailed documentation.
