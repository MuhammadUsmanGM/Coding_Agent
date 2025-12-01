class CodeExecutionService {
  constructor() {
    this.pyodide = null;
    this.isLoadingPyodide = false;
    this.pyodideReadyPromise = null;
  }

  async loadPyodide() {
    if (this.pyodide) return this.pyodide;
    if (this.pyodideReadyPromise) return this.pyodideReadyPromise;

    this.isLoadingPyodide = true;
    this.pyodideReadyPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js';
      script.onload = async () => {
        try {
          this.pyodide = await window.loadPyodide();
          // Redirect stdout/stderr
          this.pyodide.setStdout({ batched: (msg) => console.log('[Pyodide stdout]', msg) });
          resolve(this.pyodide);
        } catch (err) {
          reject(err);
        } finally {
          this.isLoadingPyodide = false;
        }
      };
      script.onerror = (err) => {
        this.isLoadingPyodide = false;
        reject(err);
      };
      document.head.appendChild(script);
    });

    return this.pyodideReadyPromise;
  }

  async runPython(code, onOutput) {
    try {
      const pyodide = await this.loadPyodide();
      
      // Capture output
      const outputs = [];
      pyodide.setStdout({ batched: (msg) => {
        outputs.push(msg);
        if (onOutput) onOutput(msg);
      }});
      
      // Run code
      await pyodide.runPythonAsync(code);
      return outputs.join('\n');
    } catch (err) {
      throw new Error(err.message);
    }
  }

  async runJavaScript(code, onOutput) {
    return new Promise((resolve, reject) => {
      const logs = [];
      
      // Create a sandboxed iframe
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      document.body.appendChild(iframe);
      
      const win = iframe.contentWindow;
      
      // Override console.log
      win.console.log = (...args) => {
        const msg = args.map(arg => 
          typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
        ).join(' ');
        logs.push(msg);
        if (onOutput) onOutput(msg);
      };
      
      win.console.error = win.console.log;
      
      try {
        // Wrap in async function to allow await
        const wrappedCode = `
          (async () => {
            try {
              ${code}
            } catch (e) {
              console.error(e.message);
            }
          })();
        `;
        
        win.eval(wrappedCode);
        
        // Wait a bit for async ops (simple timeout for now)
        setTimeout(() => {
          document.body.removeChild(iframe);
          resolve(logs.join('\n'));
        }, 1000);
        
      } catch (err) {
        document.body.removeChild(iframe);
        reject(err);
      }
    });
  }

  async execute(code, language, onOutput) {
    if (language === 'python' || language === 'py') {
      return this.runPython(code, onOutput);
    } else if (language === 'javascript' || language === 'js') {
      return this.runJavaScript(code, onOutput);
    } else {
      throw new Error(`Execution not supported for language: ${language}`);
    }
  }
}

export const codeExecutionService = new CodeExecutionService();
