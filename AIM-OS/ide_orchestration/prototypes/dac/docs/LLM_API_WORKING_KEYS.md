# LLM API Working Keys - Quick Reference

**Date:** 2025-01-28  
**Status:** ✅ **6 WORKING KEYS** (2 Gemini + 4 Cerebras)

---

## ✅ **WORKING GEMINI KEYS**

1. **Key 4:** `AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w` ✅
2. **Key 6:** `AIzaSyDiZIEkjqgyJSmQsBYnYuo69fAlkEsgplI` ✅ (NEW)

**Model:** gemini-2.5-flash  
**Endpoint:** Google Generative AI SDK  
**Status:** Both keys tested and working

---

## ✅ **WORKING CEREBRAS KEYS**

1. **Key 1:** `csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht` ✅
2. **Key 2:** `csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty` ✅
3. **Key 3:** `csk-p32pv3mykm96jrkj5cn38mf8nxhr988n5vdwrf6d5ep9kcyd` ✅
4. **Key 4:** `csk-5vch3rmdnfyx8v3vmjw84r2e28wveychjyy48pdf4rmk3xdm` ✅

**Model:** llama3.1-8b (corrected from "llama-3.1-8b-instruct")  
**Endpoint:** `https://api.cerebras.ai/v1/chat/completions`  
**Status:** All 4 keys tested and working

---

## 📋 **USAGE**

### **Environment Variables:**
```bash
# Gemini (use one of the working keys)
GEMINI_API_KEY=AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w
# OR
GEMINI_API_KEY=AIzaSyDiZIEkjqgyJSmQsBYnYuo69fAlkEsgplI

# Cerebras (use any of the working keys)
CEREBRAS_API_KEY=csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht
```

### **Multiple Keys (Rotation):**
```bash
# Gemini keys (for rotation)
GEMINI_API_KEY=AIzaSyCL2QTE7zT8oT6hC_GxM0Nt1p8QDmB5j7w
GEMINI_API_KEY_1=AIzaSyDiZIEkjqgyJSmQsBYnYuo69fAlkEsgplI

# Cerebras keys (for rotation)
CEREBRAS_API_KEY=csk-prtm28t8d2wttrh5nwj63wpvy9xpejvymw84cm25dtrwhpht
CEREBRAS_API_KEY_1=csk-xv6x26revypveycj6vffvf3yc4fhvx3mxwt9dy6de4xct5ty
CEREBRAS_API_KEY_2=csk-p32pv3mykm96jrkj5cn38mf8nxhr988n5vdwrf6d5ep9kcyd
CEREBRAS_API_KEY_3=csk-5vch3rmdnfyx8v3vmjw84r2e28wveychjyy48pdf4rmk3xdm
```

---

## 🎯 **STATUS**

- ✅ **Gemini:** 2/6 keys working (33% success rate)
- ✅ **Cerebras:** 4/4 keys working (100% success rate)
- ✅ **Total:** 6 working keys ready for production

---

**Last Updated:** 2025-01-28  
**Next Review:** When new keys are added or issues reported

