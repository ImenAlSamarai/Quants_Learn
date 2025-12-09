# Emergency CSS Fix

Your local file didn't update from git pull. Here's how to fix it manually:

## Step 1: Check Your Current File

Run this command on your Mac:

```bash
cat ~/Documents/projects_MCP/Quants_Learn/frontend/src/styles/index.css | head -10
```

**You probably see (WRONG):**
```css
/* Import new design system */
@import './new-design.css';

@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
```

## Step 2: Fix It Manually

Open the file in any text editor:

```bash
# Using nano
nano ~/Documents/projects_MCP/Quants_Learn/frontend/src/styles/index.css

# OR using VS Code
code ~/Documents/projects_MCP/Quants_Learn/frontend/src/styles/index.css

# OR using vim
vim ~/Documents/projects_MCP/Quants_Learn/frontend/src/styles/index.css
```

**DELETE these lines (lines 1-6):**
```css
/* Import new design system */
@import './new-design.css';

@tailwind base;
@tailwind components;
@tailwind utilities;
```

**REPLACE with these 2 lines:**
```css
@import 'tailwindcss';
@import './new-design.css';
```

**The file should now start like this:**
```css
@import 'tailwindcss';
@import './new-design.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* Claude-inspired Light Theme */
  --cream-bg: #FAF9F6;
  --cream-surface: #FFFFFF;
  ...
```

## Step 3: Save and Restart

1. **Save the file** (in nano: Ctrl+O, Enter, Ctrl+X)
2. **Restart dev server**:
   ```bash
   # Stop with Ctrl+C
   # Then run:
   npm run dev
   ```

## Step 4: Verify

Terminal should show **NO errors**:
```
VITE v5.4.21  ready in 91 ms
➜  Local:   http://localhost:3000/
```

Browser at `http://localhost:3000` should show the landing page with categories.

---

## Why Git Pull Didn't Work

Possible reasons:
1. File was modified locally before pulling
2. Git merge conflict that needs resolution
3. Wrong branch checked out

## Alternative: Force Reset

If manual edit doesn't work, try:

```bash
cd ~/Documents/projects_MCP/Quants_Learn
git fetch origin claude/debug-work-status-01HeAn48N3zJvNZGNNtJgpda
git reset --hard origin/claude/debug-work-status-01HeAn48N3zJvNZGNNtJgpda
```

⚠️ **Warning**: This will overwrite ALL local changes!
