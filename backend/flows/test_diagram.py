from pathlib import Path

from flows.drawio_from_plan import build_drawio_from_plan
from flows.drawio_render import render_drawio_png
from flows.openai_interpreter import interpret_diagram_plan_openai


# -------------------
#  INPUT HERE
# -------------------
flow_name = "Finance Overview"

narrative = """Historically, the finance team has used Sage 50, but processing took place outside of the finance system using teams and multiple Excel spreadsheets and workbooks between 50-100Mb, with data entry duplicated several times. The finance team has recently moved to using the cloud version, Sage Intacct. The department is 18 months into the migration.
Moving to Sage Intacct has made accounting easier, reduced human error, and made it easier to produce management accounts and submit audited accounts. There is no longer a need to reconcile different workbooks to match invoices to orders. Moreover, there was no longer a need to have an internal server to run the programs.
Legacy Information within Sage 50 remains on the old server as read only and is fully backed up.
The Auckland Project (TAP) Company No: 07931440 and charity Number: 1146219.  TAP has a controlling interest in all the companies, including Tap Trading Limited (Company No: 08148123), Park Head Leisure Ltd (Company No: 06465097) and Weardale Railway Ltd (Company No. 12392050)
Trustees of TAP are replaced every 3 years but can stay for a further 3 years. If there are extenuating circumstances, they may stay longer. 
Hotel staff use Sage for requisitioning. For day-to-day work, the hotel staff use Guestline, a cloud-based property management system (PMS) for booking accommodations and restaurant reservations. Finance uses Guestline to identify the income from this part of the business.
Finance will reconcile payments with the bank; no names and addresses are used in the reconciliation process. 
Gift Aid is stored in finance. Completed forms come in via various routes, left on Keith's desk, via email, etc. 
There is no due diligence policy for donors. 
People can give through Tap and Go machines that are placed around the site. No personal information is recorded. 
The finance team is in the middle of reviewing the policy on expenses. They do not use a dedicated system for processing expenses.
Finance runs an internal payroll. The system used is Cascade for HR and Payroll, the finance team will export payroll reports along with RotaCloud for timesheets. 
Internal communication is a mixture of MS Teams chat and email. Staff find that they can get a quick answer from an MS Teams chat. 
Some of the directors of the different limited companies use separate emails; they use both TAP email addresses and personal email addresses

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
