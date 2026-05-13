# LLM API Integration - Testing Instructions

**Date:** 2025-01-28  
**Status:** Ready for Testing

---

## 📋 **PREREQUISITES**

### **1. Install Dependencies**
```bash
pip install google-generativeai httpx
```

### **2. Set API Keys**
The test script automatically sets these keys:
- `GEMINI_API_KEY`: AIzaSyBbWCBLA4z0oNshsoXUcA55SaVulmBjQnU
- `CEREBRAS_API_KEY`: csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht

**Note:** For production, set these as environment variables or use a `.env` file.

---

## 🧪 **RUNNING TESTS**

### **Test Script:**
```bash
python test_llm_api_integration.py
```

### **What It Tests:**
1. **Gemini API Call** - Tests end-to-end flow through MCP server
2. **Cerebras API Call** - Tests end-to-end flow through MCP server
3. **Key Rotation Tracking** - Tests rotation event capture

### **Expected Output:**
- API calls succeed with real responses
- CMC storage creates atoms with proper tags
- VIF witness creation with confidence baselines
- TCS timeline entries for all calls
- Key rotation events captured

---

## ✅ **VERIFICATION CHECKLIST**

After running tests, verify:

### **CMC Storage:**
- [ ] Atoms created in CMC with `modality="llm_api_call"`
- [ ] Tags match Atlas recommendations (`system:gemini:p0`, etc.)
- [ ] Metadata includes provider, model, key_index, tokens, cost, latency

### **VIF Witness:**
- [ ] Witnesses created with provider-specific confidence baselines
- [ ] κ-gate passed based on task criticality
- [ ] Witness metadata includes provider, model, key_index

### **TCS Timeline:**
- [ ] Timeline entries created for LLM calls
- [ ] Timeline entries created for key rotation events
- [ ] Timeline entries created for quota exhaustion events
- [ ] Entry format matches Chronos recommendations

### **Key Rotation:**
- [ ] Rotation events captured in `key_manager._last_rotation_event`
- [ ] Rotation events logged to TCS timeline
- [ ] Quota exhaustion events captured

---

## 🔍 **DEBUGGING**

### **If API Calls Fail:**
1. Check API keys are set correctly
2. Check network connectivity
3. Check API quota/rate limits
4. Review error messages in test output

### **If AIM-OS Integration Fails:**
1. Check CMC memory store is initialized
2. Check VIF components are available
3. Check TCS timeline tracker is initialized
4. Review error messages in MCP server logs

### **If Key Rotation Fails:**
1. Check `key_manager._last_rotation_event` attribute exists
2. Check rotation logic in `APIKeyManager.rotate_key()`
3. Verify event is cleared after reading

---

## 📝 **TEST RESULTS**

After running tests, document:
- Which tests passed/failed
- Any errors encountered
- AIM-OS integration status
- Performance metrics (latency, tokens)

---

**Status:** Ready for testing with provided API keys

