import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';

export const exportToPDF = async (elementId, filename = 'conversation.pdf') => {
  const element = document.getElementById(elementId);
  if (!element) return;

  try {
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = canvas.width;
    const imgHeight = canvas.height;
    const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
    
    const imgX = (pdfWidth - imgWidth * ratio) / 2;
    const imgY = 30;

    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, (imgHeight * pdfWidth) / imgWidth);
    pdf.save(filename);
  } catch (error) {
    console.error('Export to PDF failed:', error);
    throw error;
  }
};

export const exportToHTML = (messages, filename = 'conversation.html') => {
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Codeius Conversation Export</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; background: #1e1e1e; color: #e0e0e0; }
        .message { margin-bottom: 20px; padding: 15px; border-radius: 8px; }
        .user { background: #2d2d2d; border-left: 4px solid #007acc; }
        .ai { background: #252526; border-left: 4px solid #4ec9b0; }
        .timestamp { font-size: 0.8em; color: #888; margin-bottom: 5px; }
        pre { background: #1e1e1e; padding: 10px; border-radius: 4px; overflow-x: auto; }
        code { font-family: 'Consolas', 'Monaco', monospace; }
      </style>
    </head>
    <body>
      <h1>Codeius Conversation</h1>
      <p>Exported on ${new Date().toLocaleString()}</p>
      <hr style="border-color: #333; margin-bottom: 30px;">
      ${messages.map(msg => `
        <div class="message ${msg.sender === 'user' ? 'user' : 'ai'}">
          <div class="timestamp">${msg.sender.toUpperCase()} • ${new Date(msg.timestamp).toLocaleString()}</div>
          <div class="content">${msg.text.replace(/\n/g, '<br>')}</div>
        </div>
      `).join('')}
    </body>
    </html>
  `;

  const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
  saveAs(blob, filename);
};

export const exportCodeToZip = async (messages, filename = 'code_snippets.zip') => {
  const zip = new JSZip();
  let count = 0;

  messages.forEach((msg, msgIndex) => {
    if (msg.sender === 'ai') {
      // Simple regex to find code blocks
      const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
      let match;
      while ((match = codeBlockRegex.exec(msg.text)) !== null) {
        const lang = match[1] || 'txt';
        const code = match[2];
        const ext = getExtension(lang);
        const name = `snippet_${msgIndex}_${count++}.${ext}`;
        zip.file(name, code);
      }
    }
  });

  if (count === 0) {
    throw new Error("No code snippets found to export.");
  }

  const content = await zip.generateAsync({ type: 'blob' });
  saveAs(content, filename);
};

const getExtension = (lang) => {
  const map = {
    python: 'py', javascript: 'js', typescript: 'ts', html: 'html', css: 'css',
    json: 'json', markdown: 'md', sql: 'sql', java: 'java', c: 'c', cpp: 'cpp'
  };
  return map[lang.toLowerCase()] || 'txt';
};
