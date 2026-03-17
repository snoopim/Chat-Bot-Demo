from pathlib import Path

from flows.reactflow_from_plan import build_reactflow_html
from flows.reactflow_render import render_reactflow_png
from flows.openai_interpreter import interpret_diagram_plan_openai


# -------------------
#  INPUT HERE
# -------------------
flow_name = "Pledging"

narrative = """At the event, the attendees can pledge a donation using a Cognito form; the information goes directly to Beacon CRM. The donor receives a QR Code or a physical form. 
The QR code leads to a Cognito form. The pledge is entered into a Cognito form and sent to Beacon. If the donor completes the physical form at the event, it is submitted to Cognito. The form is destroyed once the information is entered into Cognito.  
The donor will then receive an email with instructions on how to donate the money to the charity. The money goes directly to the charity.     
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
# Build ReactFlow HTML
# -------------------
html = build_reactflow_html(plan)

out_dir = Path("out")
out_dir.mkdir(exist_ok=True)

# Save HTML for inspection
html_path = out_dir / "demo_flow_reactflow.html"
html_path.write_text(html, encoding="utf-8")
print(f"\n HTML saved: {html_path}")


# -------------------
# Render to PNG
# -------------------
result = render_reactflow_png(html, out_dir, "demo_flow_reactflow")


# -------------------
# Result
# -------------------
if result.ok:
    print("\n PNG created:", result.png_path)
else:
    print("\n ERROR:")
    print(result.error)
