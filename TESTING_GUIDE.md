# 🧪 Testing Guide - Quant Learning Platform MVP v1.0

Welcome! Thank you for testing the Quant Learning Platform. This guide will help you evaluate all MVP features and provide valuable feedback.

## 📋 Pre-Testing Checklist

Before you start testing, ensure:

- [ ] Backend is running on `http://localhost:8000`
- [ ] Frontend is running on `http://localhost:3000`
- [ ] Browser console is open (F12 or Cmd+Option+I)
- [ ] Backend terminal is visible (to see cache logs)

## 🎯 Test Scenarios

### Test 1: User Onboarding & Level Selection

**Purpose**: Verify that users can set their learning level and that it persists.

**Steps**:
1. Open `http://localhost:3000`
2. Click **⚙️ Settings** icon in top navigation
3. Select **🎓 Graduate Student** (Level 3)
4. Add optional background: "Physics undergraduate"
5. Click **Save Preferences**
6. Refresh the page
7. Open Settings again

**Expected Results**:
- ✅ Settings modal opens smoothly
- ✅ All 5 levels are visible with descriptions
- ✅ Selected level is highlighted with checkmark
- ✅ Alert shows "Settings saved!"
- ✅ After refresh, Level 3 is still selected

**Report Issues**:
- Settings not saving?
- Wrong level showing after refresh?
- UI bugs in the settings modal?

---

### Test 2: Level-Specific Content Generation

**Purpose**: Verify that content adapts to different learning levels.

**Steps**:
1. Set your level to **🌱 Undergraduate - New** (Level 1)
2. Navigate to **Linear Algebra**
3. Click **"Vectors and Spaces"**
4. Wait for content to load (30-60 seconds first time)
5. Read the generated content
6. Note the mathematical complexity and language style
7. Go to Settings, change to **⭐ Experienced Researcher** (Level 5)
8. Click **"Vectors and Spaces"** again
9. Wait for content to load
10. Compare the two versions

**Expected Results**:
- ✅ **Level 1**: Simple language, analogies, minimal equations
- ✅ **Level 5**: Technical depth, research-level, production code
- ✅ Both have LaTeX math formulas (but different complexity)
- ✅ Both have Python code examples
- ✅ Different real-world applications
- ✅ Loading takes 30-60 seconds first time
- ✅ Second time for same level is instant (<1s)

**What to Look For**:
- Is the Level 1 content truly simpler?
- Is the Level 5 content more advanced?
- Are mathematical formulas rendering correctly?
- Is Python code syntax-highlighted?
- Any formatting issues?

**Report Issues**:
- Content too similar between levels?
- Math formulas showing as raw LaTeX?
- Code not highlighted?
- Content structure broken?

---

### Test 3: Independent Progress Tracking

**Purpose**: Verify that completion tracking is separate for each level.

**Steps**:
1. Set level to **Level 3**
2. Go to Linear Algebra → **"Eigenvalues & Eigenvectors"**
3. Click **"Mark as Complete"** button
4. Observe checkmark appears
5. Note the progress stats (should show 1/19 or similar)
6. Change level to **Level 5** in Settings
7. Go back to Linear Algebra → **"Eigenvalues & Eigenvectors"**
8. Observe completion status
9. Mark as complete at Level 5
10. Switch back to Level 3
11. Check if still shows as complete

**Expected Results**:
- ✅ At Level 3: Topic shows completed after marking
- ✅ At Level 5: Same topic shows as NOT complete
- ✅ Completing at Level 5 doesn't affect Level 3
- ✅ Progress stats update correctly for current level
- ✅ Checkmarks in sidebar update appropriately

**Report Issues**:
- Completions affecting other levels?
- Progress stats not updating?
- Checkmarks not appearing?

---

### Test 4: Mathematical Rendering (LaTeX)

**Purpose**: Verify that mathematical formulas render beautifully.

**Steps**:
1. Click any Linear Algebra topic
2. Scroll through the content
3. Look for **inline math** (e.g., $E[X] = \mu$)
4. Look for **display math** (centered equations)
5. Try zooming in/out
6. Try selecting and copying a formula

**Expected Results**:
- ✅ Inline math renders inline with text
- ✅ Display math is centered and larger
- ✅ Formulas are crisp and clear
- ✅ No raw LaTeX showing (e.g., `$x^2$`)
- ✅ Responsive to zoom
- ✅ Can select and copy

**Common Formulas to Check**:
- Summations: $\sum_{i=1}^{n} x_i$
- Fractions: $\frac{a}{b}$
- Integrals: $\int_{-\infty}^{\infty} f(x)dx$
- Matrices: $\begin{bmatrix} a & b \\ c & d \end{bmatrix}$
- Greek letters: $\alpha, \beta, \gamma, \mu, \sigma$

**Report Issues**:
- Raw LaTeX showing instead of rendered math?
- Formulas overlapping text?
- Rendering errors or broken symbols?

---

### Test 5: Python Code Highlighting

**Purpose**: Verify that code examples are properly highlighted.

**Steps**:
1. Find a topic with **## Python Implementation** section
2. Examine the code block
3. Look for syntax highlighting:
   - Keywords (import, def, return) in purple
   - Strings in green
   - Comments in gray/italic
   - Functions in blue

**Expected Results**:
- ✅ Dark theme (VS Code Dark Plus)
- ✅ Proper syntax highlighting
- ✅ Code is readable and well-formatted
- ✅ Can copy code easily

**Report Issues**:
- Code showing as plain text?
- Wrong colors or no highlighting?
- Broken formatting?

---

### Test 6: Content Caching Performance

**Purpose**: Verify that caching makes subsequent loads instant.

**Steps**:
1. Clear your browser cache (Cmd+Shift+Del or Ctrl+Shift+Del)
2. Navigate to **Calculus** → **"Multivariable Calculus"**
3. Note the loading time (use a stopwatch or count)
4. Observe backend logs showing "Cache MISS"
5. Wait for "Content cached" in backend
6. Navigate away, then back to same topic
7. Note the new loading time
8. Check backend logs for "Cache HIT"

**Expected Results**:
- ✅ **First load**: 30-60 seconds
- ✅ **Second load**: <1 second
- ✅ Backend shows "✗ Cache MISS" first time
- ✅ Backend shows "✓ Cache HIT" second time
- ✅ Content is identical both times

**Report Issues**:
- Cache not working (slow every time)?
- Content different on second load?
- Backend not showing cache logs?

---

### Test 7: Mind Map Exploration

**Purpose**: Verify interactive mind map functionality.

**Steps**:
1. Go to **Linear Algebra**
2. Click **"Explore Mode"** button
3. Interact with the mind map:
   - Drag nodes around
   - Click on a node
   - Observe connections
   - Check difficulty colors
4. Click a node to view its content

**Expected Results**:
- ✅ Mind map renders with all topics
- ✅ Nodes are draggable
- ✅ Connections show prerequisites
- ✅ Difficulty levels have different colors
- ✅ Clicking node shows content
- ✅ Completed topics marked differently

**Report Issues**:
- Mind map not loading?
- Nodes overlapping or illegible?
- Can't drag or click nodes?
- Connections missing?

---

### Test 8: Progress Dashboard

**Purpose**: Verify progress tracking and statistics.

**Steps**:
1. Go to home/landing page
2. Observe **Progress Stats** section
3. Complete 2-3 topics in different categories
4. Return to home page
5. Check stats updated
6. Switch learning level
7. Check stats reflect new level

**Expected Results**:
- ✅ Shows topics completed out of total
- ✅ Shows percentage progress
- ✅ Shows current learning level
- ✅ Updates after completing topics
- ✅ Resets when switching levels

**Report Issues**:
- Stats not updating?
- Wrong numbers showing?
- Doesn't reflect level changes?

---

### Test 9: Recommended Topics

**Purpose**: Verify personalized recommendations.

**Steps**:
1. As a new user, check recommendations on home page
2. Complete recommended topic
3. Check if recommendations update
4. Test prerequisite-based suggestions

**Expected Results**:
- ✅ Shows 3 recommended topics
- ✅ New users see fundamental topics
- ✅ Updates after completing topics
- ✅ Suggests topics with met prerequisites

**Report Issues**:
- No recommendations showing?
- Same recommendations after completion?
- Inappropriate difficulty suggested?

---

### Test 10: Cross-Browser Testing

**Purpose**: Verify platform works across browsers.

**Test the same workflow in**:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (macOS)
- [ ] Edge

**Expected Results**:
- ✅ All features work in all browsers
- ✅ Math rendering consistent
- ✅ Code highlighting consistent
- ✅ No console errors

**Report Issues**:
- Features broken in specific browser?
- Visual inconsistencies?
- Performance differences?

---

## 🐛 How to Report Issues

For each issue found, please provide:

### Issue Template

```markdown
**Issue Title**: Brief description

**Severity**: Critical / High / Medium / Low

**Test Scenario**: Which test scenario from above?

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happened

**Screenshots**:
[Attach if relevant]

**Browser Console Errors**:
[Copy any red errors from console]

**Backend Logs**:
[Copy relevant backend output]

**Environment**:
- OS: [macOS/Windows/Linux]
- Browser: [Chrome/Firefox/Safari]
- Browser Version: [e.g., 120.0]
```

## 📊 Feedback Form

After testing, please provide feedback on:

### User Experience (1-5 stars)
- Overall ease of use: ⭐⭐⭐⭐⭐
- Content quality: ⭐⭐⭐⭐⭐
- Mathematical rendering: ⭐⭐⭐⭐⭐
- Loading speed: ⭐⭐⭐⭐⭐
- Visual design: ⭐⭐⭐⭐⭐

### Open-Ended Questions

1. **What did you like most about the platform?**

2. **What frustrated you or didn't work as expected?**

3. **How does the content quality compare to other learning resources?**

4. **Would you use this platform for learning quant finance? Why/why not?**

5. **What features are you missing?**

6. **Any other comments or suggestions?**

## ✅ Testing Completion Checklist

Mark off as you complete each test:

- [ ] Test 1: User Onboarding & Level Selection
- [ ] Test 2: Level-Specific Content Generation
- [ ] Test 3: Independent Progress Tracking
- [ ] Test 4: Mathematical Rendering
- [ ] Test 5: Python Code Highlighting
- [ ] Test 6: Content Caching Performance
- [ ] Test 7: Mind Map Exploration
- [ ] Test 8: Progress Dashboard
- [ ] Test 9: Recommended Topics
- [ ] Test 10: Cross-Browser Testing
- [ ] Filled out feedback form
- [ ] Reported all issues found

---

## 📧 Submitting Your Feedback

Send your completed testing report to:
- **Email**: [Your email]
- **GitHub Issues**: https://github.com/ImenAlSamarai/Quants_Learn/issues

---

**Thank you for helping improve the Quant Learning Platform!** 🙏

Your feedback is invaluable for making this the best learning resource for aspiring quants.

---

*MVP v1.0 Testing Guide*
*Last updated: November 2024*
