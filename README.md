# AWS Visualization Tool

**Automate AWS architecture documentation by transforming AWS CLI output into clear, customizable diagrams.**  

✅ Generate AWS Organizations diagrams *(available now)*  
✅ Plan for broader AWS visualization support (VPCs, EC2, RDS, etc.)  
✅ Built in Python with Mermaid diagram export  

---

## 🚀 Overview

AWS Visualization Tool is designed to help cloud architects and engineers **document and visualize AWS environments automatically**.  

⭐ **Current MVP:**  
- Parses `aws organizations list-accounts` JSON output  
- Identifies management account and member accounts  
- Generates hierarchy diagrams using Mermaid syntax  
- Auto-exports diagrams as PNG or SVG  

⭐ **Future Goals:**  
- Support for VPCs, subnets, EC2, RDS, Load Balancers, and more  
- Visualize full account and network architecture  
- Enable modular, reusable diagram generation  

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
- Input = `input/org.json`
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

✅ **Step 1:** Get your AWS Organizations account list:

```bash
aws organizations list-accounts > input/org.json
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

**Current Diagram:**  
- Management account (root) node  
- Child accounts with ACTIVE/SUSPENDED status  

*(Color-coding and OU grouping planned in future enhancements.)*

---

## 🌟 Roadmap

✅ **Near-term goals:**
- Color-coded nodes (ACTIVE/SUSPENDED)
- Organizational Units (OU) support
- Command-line arguments for custom input/output paths
- Interactive input file selection

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
