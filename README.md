# AWS Visualization Tool

A utility to visualize your AWS Organizations hierarchy as clear, professional diagrams. It transforms AWS CLI JSON exports into Mermaid diagrams and renders them as PNG or SVG images—complete with OU hierarchy, accounts, and status coloring.

## Features

- Input:
  - AWS Organizations CLI JSON exports:
    - `list-roots.json`
    - `list-organizational-units-for-parent.json`
    - `list-accounts-for-parent-*.json`
- Outputs:
  - Mermaid `.mmd` diagram source
  - Rendered PNG or SVG image
  - Timestamped subfolders for organized history
- CLI interface:
  - Interactive prompts
  - Command-line arguments for automation
  - User-defined output format (PNG/SVG) and scale factor
- Webapp interface (Flask):
  - Upload multiple JSON files or a single ZIP bundle
  - Choose output format (PNG/SVG)
  - Specify scale factor (e.g., 1, 2, 3, ...)
  - Flash error handling and user-friendly feedback

## Installation & Setup

### Requirements
- Python 3.8+
- Node.js / npm (for Mermaid CLI)

### Install Dependencies
```
pip install Flask
npm install -g @mermaid-js/mermaid-cli
```

### Export Your AWS Organizations Data
```
aws organizations list-roots > list-roots.json
aws organizations list-organizational-units-for-parent --parent-id <root-id> > list-organizational-units-for-parent.json
aws organizations list-accounts-for-parent --parent-id <ou-id> > list-accounts-for-parent-<OU>.json
```
Place all resulting JSON files in one folder.

## Running the CLI Tool

**Interactive mode:**
```
python main.py
```
You’ll be prompted for:
```
Input folder [input]:
Base output folder [output]:
Image format (png/svg) [png]:
Scale factor [2]:
```

**Command-line arguments:**
```
python main.py --input input --output output --format svg --scale 3
```
Supports automation in scripts and CI/CD pipelines.

## Running the Webapp

Start the Flask server:
```
cd webapp
flask run
```
Open in your browser:
```
http://localhost:5000
```
- Upload multiple JSON files or a single ZIP archive
- Choose output format (PNG/SVG)
- Specify scale factor
- Click **Generate Diagram** to receive your downloadable image

## Example Project Structure
```
aws_visualizations/
  input/                     ← CLI input files
  output/                    ← CLI results (timestamped folders)
  main.py                    ← CLI entry point
  generator.py               ← Shared generation logic

  webapp/
    app.py                   ← Flask web server
    templates/
      index.html             ← Web upload form
    uploads/                 ← Temporary upload storage
    outputs/                 ← Generated diagrams
```
Example CLI output folder:
```
output/
  2025-06-30-221530/
    aws_org_diagram.mmd
    aws_org_diagram.png
```

## Diagram Features

- Root node explicitly linked to each OU
- OU subgraphs with contained accounts
- Self-referencing accounts automatically renamed to avoid cycles
- Color-coded ACTIVE and SUSPENDED status
- Supports PNG and SVG output formats
- Scalable resolution with `--scale` option
- Clean, timestamped output folders for history and audit

## Potential Future Enhancements

- Inline diagram preview in webapp
- Nicer styling with Bootstrap
- Input validation before generation (missing required files check)
- Auto-cleanup of old output folders
- Support for nested OU hierarchies
- Packaging as an installable CLI tool
- Hosting the Flask interface online

## Author

Erick Perales  — IT Architect, Cloud Migration Specialist
