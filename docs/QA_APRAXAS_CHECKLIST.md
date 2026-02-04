# 🧪 APRAXAS QA CHECKLIST
**Refactor:** Single Render Authority + Navigation Data Structure  
**Date:** 2026-02-04

---

## PRE-EXECUTION CHECKLIST

### ✅ Files Modified:
- [x] `static/app.js` - Integrated layout renderer
- [x] `static/index.html` - Converted to pure shell
- [x] `static/ui/navigation.js` - NEW (Single source of truth)
- [x] `static/ui/layout.js` - NEW (Layout renderer)

### ✅ Files Removed/Cleaned:
- [x] Dead script in index.html (banner verification)
- [x] Static sidebar markup removed
- [x] Static header nav removed

---

## DETERMINISTIC VERIFICATION STEPS

### TEST 1: DOM STRUCTURE ✅

**What to check:**
- Header contains dynamically injected nav
- Sidebar contains dynamically injected links
- No duplicated elements

**Commands:**
```javascript
// Open browser console (F12)
// Run these checks:

// 1. Verify header button exists
const headerEcosystem = document.querySelector('[data-id="btn-ecosystem"]');
console.assert(headerEcosystem !== null, '❌ Header ECOSISTEMA button missing');
console.log('✅ Header button:', headerEcosystem);

// 2. Verify sidebar link exists
const sidebarEcosystem = document.querySelector('[data-id="nav-ecosystem"]');
console.assert(sidebarEcosystem !== null, '❌ Sidebar ECOSISTEMA link missing');
console.log('✅ Sidebar link:', sidebarEcosystem);

// 3. Verify NO duplicates
const allEcosystemLinks = document.querySelectorAll('a[href*="gahenaxaisolutions"]');
console.assert(allEcosystemLinks.length === 2, `❌ Expected 2 links, found ${allEcosystemLinks.length}`);
console.log('✅ Link count correct:', allEcosystemLinks.length);

// 4. Verify all sidebar links present
const expectedLinks = ['nav-list', 'nav-create', 'nav-support', 'nav-settings', 'nav-ecosystem'];
expectedLinks.forEach(id => {
    const el = document.getElementById(id);
    console.assert(el !== null, `❌ Link ${id} missing`);
});
console.log('✅ All navigation links present');
```

**Expected Output:**
```
✅ Header button: <a data-id="btn-ecosystem">...</a>
✅ Sidebar link: <a data-id="nav-ecosystem">...</a>
✅ Link count correct: 2
✅ All navigation links present
```

---

### TEST 2: FUNCTIONALITY ✅

**Manual Steps:**
1. Open application: `http://localhost:8000/static/index.html`
2. **Header Button:**
   - Click "ECOSISTEMA" button
   - ✅ Should open https://gahenaxaisolutions.com in new tab
3. **Sidebar Link:**
   - Click "ECOSISTEMA GAHENAX" in sidebar
   - ✅ Should open https://gahenaxaisolutions.com in new tab
4. **Internal Navigation:**
   - Click "EXPEDIENTES" → Should navigate to list view
   - Click "RADICACIÓN" → Should navigate to form view
   - Click "SOPORTE CRM" → Should navigate to support view
   - Click "ARCHIVO CENTRAL" → Should navigate to settings view

**Evidence to capture:**
- Screenshot of header with ECOSISTEMA button visible
- Screenshot of sidebar with ECOSISTEMA link at bottom
- Browser console showing no errors

---

### TEST 3: IDEMPOTENCY ✅

**What to check:**
- Re-rendering doesn't create duplicates
- Navigation still works after re-render

**Commands:**
```javascript
// In browser console:

// 1. Count elements before
const countBefore = {
    headerButtons: document.querySelectorAll('[data-layout="header-nav"] a').length,
    sidebarLinks: document.querySelectorAll('.lex-sidebar nav ul li').length
};
console.log('Before re-render:', countBefore);

// 2. Force re-render
window.GahenaxLayout.renderHeader();
window.GahenaxLayout.renderSidebar();

// 3. Count elements after
const countAfter = {
    headerButtons: document.querySelectorAll('[data-layout="header-nav"] a').length,
    sidebarLinks: document.querySelectorAll('.lex-sidebar nav ul li').length
};
console.log('After re-render:', countAfter);

// 4. Assert no change (idempotent)
console.assert(
    countBefore.headerButtons === countAfter.headerButtons,
    '❌ Header buttons duplicated'
);
console.assert(
    countBefore.sidebarLinks === countAfter.sidebarLinks,
    '❌ Sidebar links duplicated'
);

console.log('✅ Idempotency verified');
```

**Expected Output:**
```
Before re-render: {headerButtons: 1, sidebarLinks: 6}
After re-render: {headerButtons: 1, sidebarLinks: 6}
✅ Idempotency verified
```

---

### TEST 4: CONSOLE LOGS ✅

**What to check:**
- No errors in console
- Expected initialization logs present

**Expected console output:**
```
GAHENAX Core Initializing (Lex-Tech Standard)...
✅ Header rendered
✅ Sidebar rendered
🎨 Layout initialized
✅ Navigation configured
```

**Errors to watch for:**
- ❌ "Cannot read property 'appendChild' of null"
- ❌ "getElementById returned null"
- ❌ "Uncaught TypeError"

---

### TEST 5: CROSS-VIEW PERSISTENCE ✅

**Manual Steps:**
1. Click "EXPEDIENTES" (list view)
2. Verify ECOSISTEMA button still in header
3. Click "RADICACIÓN" (form view)
4. Verify ECOSISTEMA button still in header
5. Click "SOPORTE CRM" (support view)
6. Verify ECOSISTEMA button still in header
7. Click "ARCHIVO CENTRAL" (settings view)
8. Verify ECOSISTEMA button still in header

**Expected:**
- ✅ ECOSISTEMA button persists across all views
- ✅ ECOSISTEMA sidebar link persists across all views
- ✅ No visual glitches or flickering

---

### TEST 6: STYLING ✅

**What to check:**
- Gradient background on header button
- Hover effects work
- Icons display correctly

**Manual verification:**
1. **Header Button:**
   - Has blue gradient background
   - Shows cube icon (left)
   - Shows external link icon (right)
   - Brightens on hover

2. **Sidebar Link:**
   - Has light blue background
   - Has orange left border
   - Shows grid icon (left)
   - Shows external link icon (right)
   - Background darkens on hover

---

### TEST 7: RESPONSIVE BEHAVIOR ✅

**Manual Steps:**
1. Resize browser window
2. Verify layout adjusts gracefully
3. Check mobile viewport (F12 → Device toolbar)
4. Verify sidebar still functional

---

## AUTOMATED QA SCRIPT

**Create this file:** `static/qa-verify.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>QA Verification - APRAXAS</title>
</head>
<body>
    <h1>APRAXAS QA Verification</h1>
    <div id="results"></div>
    
    <script>
        async function runQA() {
            const results = [];
            
            // Wait for DOM
            await new Promise(r => setTimeout(r, 2000));
            
            // TEST 1: Elements exist
            const headerBtn = document.querySelector('[data-id="btn-ecosystem"]');
            results.push({
                test: 'Header button exists',
                pass: headerBtn !== null
            });
            
            const sidebarLink = document.querySelector('[data-id="nav-ecosystem"]');
            results.push({
                test: 'Sidebar link exists',
                pass: sidebarLink !== null
            });
            
            // TEST 2: No duplicates
            const allLinks = document.querySelectorAll('a[href*="gahenaxaisolutions"]');
            results.push({
                test: 'Exactly 2 ecosystem links',
                pass: allLinks.length === 2
            });
            
            // TEST 3: All nav links
            const navIds = ['nav-list', 'nav-create', 'nav-support', 'nav-settings', 'nav-ecosystem'];
            const allPresent = navIds.every(id => document.getElementById(id));
            results.push({
                test: 'All 5 navigation links present',
                pass: allPresent
            });
            
            // Display results
            const resultsDiv = document.getElementById('results');
            results.forEach(r => {
                const status = r.pass ? '✅ PASS' : '❌ FAIL';
                resultsDiv.innerHTML += `<p>${status}: ${r.test}</p>`;
            });
            
            const allPass = results.every(r => r.pass);
            resultsDiv.innerHTML += `<h2>${allPass ? '🎉 ALL TESTS PASSED' : '⚠️ SOME TESTS FAILED'}</h2>`;
        }
        
        if (window.location.href.includes('index.html') || window.location.pathname === '/static/') {
            runQA();
        } else {
            window.location.href = '/static/index.html';
        }
    </script>
</body>
</html>
```

---

## REGRESSION TESTING

**Before deploying to production:**

1. ✅ Run all existing features
2. ✅ Verify no broken internal links
3. ✅ Check that Settings view still works
4. ✅ Verify form submission still works
5. ✅ Test AI search still functional
6. ✅ Chat widget still operational

---

## EVIDENCE CAPTURE

**Required screenshots:**
1. Full page with header button visible
2. Sidebar with all 5 links (including ECOSISTEMA)
3. Browser console with no errors
4. Network tab showing successful script loads

**Required console output:**
```
Save console output to: docs/qa-console-output.txt
```

---

## SIGN-OFF

- [ ] All tests pass
- [ ] No console errors
- [ ] Screenshots captured
- [ ] Evidence logged
- [ ] Ready for merge

**QA Engineer:** _________________  
**Date:** _________________  
**Status:** [ ] APPROVED / [ ] REJECTED

---

**Generated:** 2026-02-04  
**Protocol:** ANTIGRAVITY/APRAXAS
