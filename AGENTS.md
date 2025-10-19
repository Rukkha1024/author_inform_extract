## Environment rules
- Use the existing conda env: `author_extract` (WSL2, Python 3.11.13).
- Installed packages: requests 2.32.5, beautifulsoup4 4.14.2
- Always run Python/pip as: `conda run -n author_extract python` / `conda run -n author_extract pip`.
- **Do not** create or activate any `venv` or `.venv` or run `uv venv`.
- If a package is missing, prefer:
  1) `mamba/conda install -n author_extract <pkg>` (if available)
  2) otherwise `conda run -n author_extract pip install <pkg>`
- Before running Python, verify the interpreter path with:
  `conda run -n author_extract python -c "import sys; print(sys.executable)"`

---

### **Codebase Rule: Configuration Management**

- Save outputs in the "output" folder.
- Save code files in the "script" folder.
 
