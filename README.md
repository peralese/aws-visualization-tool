# AWS Visualization Tool

**Automate AWS architecture documentation by transforming AWS CLI output into clear, customizable diagrams.**  

✅ Generate hierarchical AWS Organizations diagrams *(Root → OUs → Accounts)*  
✅ Renames self-referencing accounts to avoid cycles  
✅ Color-coded ACTIVE/SUSPENDED status  
✅ Auto-exports Mermaid to PNG or SVG with configurable scaling  
✅ Built in Python with Mermaid CLI integration  

---

## 🚀 Overview

AWS Visualization Tool helps cloud architects and engineers **document and visualize AWS Organizations automatically**.  

⭐ **Current MVP Features:**  
- Parses AWS Organizations CLI JSON output  
- Identifies management account (Root) and Organizational Units (OUs)  
- Explicitly links Root → OUs to enforce hierarchical layout  
- Generates subgraphs for OUs containing accounts  
- Renames self-referencing accounts (e.g. `OUName → OUName (Account)`) to avoid rendering errors  
- Color-codes ACTIVE and SUSPENDED accounts  
- Exports diagram automatically as PNG or SVG using Mermaid CLI with scaling  

⭐ **Future Goals:**  
- Support for VPCs, subnets, EC2, RDS, Load Balancers, etc.  
- Visualize complete AWS account and network architecture  
- Modular, reusable diagram generation  
- CLI arguments and interactive input  
- Web-based UI for easy upload/generate/download  

---

## 📦 Project Structure

```
aws_visualizations/
  input/            # Place your AWS CLI JSON output here
  output/           # Generated Mermaid (.mmd) and images
  main.py           # Main Python generator script
  .gitignore
  README.md
```

✅ By default:
- Input = `input/` folder
- Output = `output/aws_org_diagram.mmd`, `output/aws_org_diagram.png`

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

✅ **Step 2:** Run the generator:

```bash
python main.py
```

✅ **Result:**
- Mermaid diagram file: `output/aws_org_diagram.mmd`
- Rendered image (PNG/SVG): `output/aws_org_diagram.png`

---

## 🖼️ Example Output

- Root node shown at top of hierarchy  
- Explicit links from Root → OUs  
- Subgraphs for each OU  
- Accounts inside subgraphs  
- Self-referencing accounts renamed (e.g. `AccountFactoryTerraform (Account)`)  
- ACTIVE/SUSPENDED color-coded nodes  

---

## 🌟 Roadmap

✅ **Near-term goals:**
- Color-coded nodes (ACTIVE/SUSPENDED)
- Organizational Unit (OU) support (implemented)
- Hierarchical layout with Root → OUs
- Command-line arguments for custom input/output
- Interactive file selection

✅ **Planned support for:**
- VPC and subnet layouts
- EC2 instances in subnets
- RDS instances and networking
- Security Groups and NACLs
- Load balancers and other AWS resources

✅ **Possible future enhancements:**
- Packaged as installable CLI tool
- Web-based UI for upload/generate/download
- Export to PDF/Visio formats

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
