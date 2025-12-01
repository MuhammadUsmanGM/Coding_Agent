# 🚀 Quick Start Guide - Testing Your New Features

## Prerequisites
Wait for `npm install` to complete in the Codeius-GUI directory.

## Starting the Application

### Option 1: Development Mode (Recommended for Testing)
```bash
cd Codeius-GUI
npm run dev
```
Then open http://localhost:5173 (or the port shown in terminal)

### Option 2: Production Build
```bash
cd Codeius-GUI
npm run build
cd ..
codeius web
```
Then open http://localhost:8080

---

## 🧪 Feature Testing Checklist

### ✅ Theme Toggle
- [ ] Click sun/moon icon in navbar
- [ ] Verify colors change smoothly
- [ ] Refresh page - theme should persist

### ✅ Markdown Rendering
Send this test message:
```markdown
# Heading 1
## Heading 2

This is **bold** and *italic* and ~~strikethrough~~.

- Bullet point 1
- Bullet point 2
  - Nested point

1. Numbered item
2. Another item

> This is a blockquote

[Click me](https://example.com)

Inline `code` example
```

### ✅ Syntax Highlighting
Send this:
```
\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
\`\`\`

\`\`\`javascript
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
greet('World');
\`\`\`
```

- [ ] Code blocks have syntax highlighting
- [ ] Language badge appears
- [ ] Copy button works
- [ ] Clicking copy shows "✓ Copied!"

### ✅ Message Actions
- [ ] Hover over any message
- [ ] Action buttons appear (📋, 🔄, 🗑️)
- [ ] Copy button copies text
- [ ] Delete button removes message
- [ ] Regenerate button appears only on AI messages

### ✅ Command Autocomplete
- [ ] Type `/` in input field
- [ ] Autocomplete dropdown appears
- [ ] Type `mod` - filters to `/models`
- [ ] Use ↑↓ arrows to navigate
- [ ] Press Enter to select
- [ ] Press Esc to close

### ✅ Keyboard Shortcuts
- [ ] Press `Ctrl+/` - shortcuts overlay appears
- [ ] Press `Ctrl+L` - conversation clears
- [ ] Press `Ctrl+K` - input field focuses
- [ ] Press `Esc` - closes modals/autocomplete
- [ ] Press `Enter` - sends message
- [ ] Press `Shift+Enter` - creates new line

### ✅ File Upload
- [ ] Scroll to see file drop zone
- [ ] Click drop zone - file browser opens
- [ ] Select files - file chips appear
- [ ] Drag files onto drop zone - visual feedback
- [ ] Click × on file chip - removes file
- [ ] File size displays correctly

### ✅ Chat Persistence
- [ ] Send several messages
- [ ] Refresh the page
- [ ] Messages are still there
- [ ] Scroll position maintained

### ✅ Model Switcher
- [ ] Click ⚙️ settings icon
- [ ] Settings dropdown appears
- [ ] Available models listed
- [ ] Current model marked with "✓ Active"
- [ ] Click different model
- [ ] Loading state shows
- [ ] Model switches successfully

### ✅ Toast Notifications
- [ ] Perform actions that trigger toasts
- [ ] Toast appears in top-right
- [ ] Auto-dismisses after 3 seconds
- [ ] Multiple toasts stack properly
- [ ] Click × to dismiss manually

### ✅ Typing Indicator
- [ ] Send a message to AI
- [ ] Bouncing dots appear
- [ ] Dots disappear when response arrives

### ✅ Send Button
- [ ] Input field has 📤 button
- [ ] Button disabled when input empty
- [ ] Button shows ⏳ when sending
- [ ] Click button sends message

### ✅ Character Counter
- [ ] Type in input field
- [ ] Character count updates in real-time
- [ ] Displays in bottom-right

### ✅ Responsive Design
Test on different screen sizes:
- [ ] Desktop (> 1440px) - full layout
- [ ] Laptop (1024-1440px) - optimized
- [ ] Tablet (768-1024px) - adapted
- [ ] Mobile (< 768px) - compact
- [ ] Portrait orientation - vertical layout
- [ ] Landscape orientation - horizontal layout

---

## 🎨 Visual Checks

### Dark Theme
- Background: Deep blue (#0a192f)
- Text: White with high contrast
- Accents: Blue (#0072ff)
- Borders: Subtle white

### Light Theme
- Background: Light gray (#f5f7fa)
- Text: Dark gray (#1a202c)
- Accents: Blue (#0072ff)
- Borders: Subtle black

---

## 🐛 Common Issues & Fixes

### Issue: npm install still running
**Fix:** Wait for it to complete. It may take 2-5 minutes.

### Issue: Module not found errors
**Fix:** 
```bash
cd Codeius-GUI
npm install
```

### Issue: Port already in use
**Fix:** Kill the process or use a different port:
```bash
npm run dev -- --port 3001
```

### Issue: Theme not changing
**Fix:** Hard refresh (Ctrl+Shift+R) to clear cache

### Issue: Autocomplete not showing
**Fix:** Make sure you type `/` at the start of input

### Issue: Messages not persisting
**Fix:** Check browser localStorage is enabled

---

## 📸 Screenshot Checklist

Take screenshots of:
1. Dark theme with markdown message
2. Light theme with code block
3. Message actions on hover
4. Command autocomplete dropdown
5. Keyboard shortcuts overlay
6. File upload with files attached
7. Settings panel with models
8. Toast notification
9. Mobile responsive view

---

## ✨ Pro Tips

1. **Use keyboard shortcuts** - Much faster than clicking
2. **Drag multiple files** - Upload several at once
3. **Copy code blocks** - Hover and click copy
4. **Switch themes** - Match your environment
5. **Use autocomplete** - Type `/` for quick commands
6. **Delete mistakes** - Hover and click delete
7. **Regenerate responses** - Get different AI answers

---

## 🎯 Performance Benchmarks

Expected performance:
- **First load**: < 2 seconds
- **Theme switch**: < 100ms
- **Message render**: < 50ms
- **Autocomplete**: < 10ms
- **File upload UI**: Instant
- **Toast animation**: 300ms

---

## 📝 Notes

- All features work offline except AI responses
- Chat history stored in browser localStorage
- Theme preference syncs across tabs
- File uploads ready (backend integration pending)
- WebSocket streaming ready (backend pending)

---

## ✅ Success Criteria

You've successfully tested all features when:
- [x] All 19 features work as described
- [x] No console errors
- [x] Smooth animations
- [x] Responsive on all devices
- [x] Theme persists on refresh
- [x] Messages persist on refresh
- [x] Keyboard shortcuts work
- [x] File upload UI functional

---

## 🎉 Congratulations!

If all tests pass, your Codeius GUI is now a **production-ready, professional AI chat interface** with all modern features! 🚀
