import argparse
from generator import generate_diagram

# ---------------------------------------
# ✅ Interactive Prompt Helper
# ---------------------------------------
def prompt_value(prompt, default):
    user_input = input(f"{prompt} [{default}]: ").strip()
    return user_input if user_input else default

# ---------------------------------------
# ✅ CLI Argument Parsing
# ---------------------------------------
parser = argparse.ArgumentParser(
    description="Generate AWS Organization diagrams from CLI JSON outputs."
)

parser.add_argument(
    "--input",
    default=None,
    help="Input directory containing AWS Organizations JSON files"
)
parser.add_argument(
    "--output",
    default=None,
    help="Base output directory for Mermaid and image files"
)
parser.add_argument(
    "--format",
    choices=["png", "svg"],
    default=None,
    help="Output image format: png or svg"
)
parser.add_argument(
    "--scale",
    default=None,
    help="Scale factor for image resolution"
)

args = parser.parse_args()

# ---------------------------------------
# ✅ Interactive Prompts with Defaults
# ---------------------------------------
print("\n🟢 AWS Visualization Tool Interactive Setup")

INPUT_DIR = args.input or prompt_value("Input folder", "input")
OUTPUT_DIR = args.output or prompt_value("Base output folder", "output")
OUTPUT_IMAGE_FORMAT = args.format or prompt_value("Image format (png/svg)", "png")
SCALE_FACTOR = args.scale or prompt_value("Scale factor", "5")

print("\n✅ Configuration:")
print(f"  Input folder: {INPUT_DIR}")
print(f"  Base output folder: {OUTPUT_DIR}")
print(f"  Image format: {OUTPUT_IMAGE_FORMAT}")
print(f"  Scale factor: {SCALE_FACTOR}\n")

# ---------------------------------------
# ✅ Call Generator Function
# ---------------------------------------
try:
    final_output_dir = generate_diagram(
        INPUT_DIR,
        OUTPUT_DIR,
        OUTPUT_IMAGE_FORMAT,
        SCALE_FACTOR
    )

    print(f"\n✅ Diagram generation complete!")
    print(f"✅ Files saved in: {final_output_dir}\n")

except Exception as e:
    print(f"\n❗ ERROR: {e}\n")
