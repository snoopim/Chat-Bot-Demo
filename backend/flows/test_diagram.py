from pathlib import Path

from flows.drawio_from_plan import build_drawio_from_plan
from flows.drawio_render import render_drawio_png
from flows.openai_interpreter import interpret_diagram_plan_openai


# -------------------
#  INPUT HERE
# -------------------
flow_name = "One off Giving"

narrative = """ One-off donations are made through the website, linked to Squarespace. Information is sent by email, marked as Squarespace donation. These go into a separate email folder marked “Donations”. 
Payment goes into the bank account. The information is reconciled by the account and then posted to Xero.   
"""


# -------------------
# Generate Plan (dynamically via OpenAI)
# -------------------
plan = interpret_diagram_plan_openai(flow_name, narrative)
plan["title"] = flow_name

print("\n PLAN:")
for key in ("title", "lanes", "nodes", "edges"):
    print(f"  {key}: {plan.get(key)}")


# -------------------
# Build XML
# -------------------
xml = build_drawio_from_plan(plan)

out_dir = Path("out")
out_dir.mkdir(exist_ok=True)
result = render_drawio_png(xml, out_dir, "demo_flow")


# -------------------
# Result
# -------------------
if result.ok:
    print("\n PNG created:", result.png_path)
else:
    print("\n ERROR:")
    print(result.error)
