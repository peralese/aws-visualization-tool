# AWS Visualization Tool

**Automate AWS Organizations documentation with easy-to-use, customizable diagrams.**  

✅ Generate hierarchical AWS Organizations diagrams *(Root → OUs → Accounts)*  
✅ Supports self-referencing account renaming to avoid cycles  
✅ Color-coded ACTIVE/SUSPENDED status  
✅ Auto-generates Mermaid diagram + image export (PNG/SVG)  
✅ CLI *and* interactive prompts for configuration  
✅ Normalized naming for robust matching  
✅ Organized, timestamped output folders for easy history  

---

## 🚀 Overview

AWS Visualization Tool helps architects and engineers **document and visualize AWS Organizations** automatically.  

⭐ **Current Features:**  
- Parses AWS Organizations CLI JSON output  
- Detects management account (Root) and Organizational Units (OUs)  
- Explicitly links Root → OUs to enforce hierarchical layout  
- Generates subgraphs for OUs containing accounts  
- Renames self-referencing accounts (e.g. `OUName → OUName (Account)`) to avoid rendering errors  
- Color-codes ACTIVE and SUSPENDED accounts  
- Normalizes naming to match files and OUs robustly  
- Saves diagrams to **timestamped subfolders** for easy versioning  
- Fully configurable via CLI or interactive prompts  

---

## 📦 Project Structure

```
aws_visualizations/
  input/            # Place AWS CLI JSON outputs here
  output/           # Auto-created timestamped folders with generated diagrams
  main.py           # Main Python generator script
  .gitignore
  README.md
```

✅ Example output after a run:

```
output/
  2025-06-30-221530/
    aws_org_diagram.mmd
    aws_org_diagram.png
```

---

## ⚙️ Requirements

- Python 3.7+  
- Node.js & npm (for Mermaid CLI)  

---

## ✅ Installation

1️⃣ Clone this repository:

```bash
git clone https://github.com/peralese/aws-visualization-tool.git
cd aws-visualization-tool
```

2️⃣ Install Python dependencies (optional):

```bash
pip install -r requirements.txt
```

3️⃣ Install Mermaid CLI:

```bash
npm install -g @mermaid-js/mermaid-cli
```

✅ Verify installation:

```bash
mmdc -V
```

---

## 🗺️ How to Use

✅ **Step 1:** Collect AWS Organizations CLI output:

```bash
aws organizations list-roots > input/list-roots.json
aws organizations list-organizational-units-for-parent --parent-id <ROOT_ID> > input/list-organizational-units-for-parent.json

# For each OU ID
aws organizations list-accounts-for-parent --parent-id <OU_ID> > input/list-accounts-for-parent-<OU-Name>.json
```

---

✅ **Step 2:** Run the generator:

⭐ Fully automatic with prompts:

```bash
python main.py
```

✅ Or with CLI arguments:

```bash
python main.py --input myinputs --output myoutputs --format svg --scale 3
```

---

✅ **Interactive prompts available**:

If you don’t pass an argument, you’ll be prompted:

```
Input folder [input]:
Base output folder [output]:
Image format (png/svg) [png]:
Scale factor [2]:
```

✅ You can hit ENTER to accept defaults.

---

## ✅ 📦 Output Structure

✅ Every run creates a **timestamped subfolder** in your output directory:

```
output/
  2025-06-30-221530/
    aws_org_diagram.mmd
    aws_org_diagram.png
```

✅ Keeps a **complete history** of all generated diagrams.

---

## 🖼️ Example Diagram Features

- Root node explicitly linked to each OU  
- OU subgraphs with contained accounts  
- Self-referencing accounts renamed safely  
- Color-coded ACTIVE and SUSPENDED status  
- Supports PNG and SVG output formats  
- Scalable resolution with `--scale` option  

---

## 🌟 Roadmap

✅ **Completed features:**
- Hierarchical Root → OU → Accounts layout
- Self-referencing account renaming
- Color-coded ACTIVE/SUSPENDED nodes
- Automatic .mmd + PNG/SVG generation
- Configurable scale factor
- Robust name normalization
- CLI arguments for configuration
- Interactive input prompts
- Timestamped output folders for easy history

✅ **Near-term planned features:**
- Advanced styling options (themes, shapes)
- Improved output file naming

✅ **Potential future enhancements:**
- Nested OU hierarchy rendering
- Support for other AWS resources (VPC, Subnets, EC2, RDS)
- Packaging as an installable CLI tool
- Web-based UI for upload/generate/download

---

## 🤝 Contributing

We welcome contributions!  
- Report issues  
- Submit feature requests  
- Open pull requests for improvements  

---

## 📜 License

[MIT License](LICENSE)

---

## ⭐ Author

- **Erick Perales**  
  [https://github.com/peralese](https://github.com/peralese)

