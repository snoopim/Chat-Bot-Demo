// app/lib/processes.ts

export const PROCESS_GROUPS = [
  {
    group: "Human Resources",
    items: [
      { label: "Recruitment", common: true },
      { label: "Onboarding (New Starters)", common: true },
      { label: "Appraisal", common: false },
      { label: "Job role changes", common: false },
      { label: "Special leave", common: false },
      { label: "Reasonable Adjustment", common: false },
      { label: "Return to Work", common: false },
      { label: "Offboarding (Leavers)", common: true },
    ],
  },
  {
    group: "Finance",
    items: [
      { label: "Invoices", common: false },
      { label: "Payroll", common: false },
      { label: "Expenses", common: false },
      { label: "Gift Aid (charities only)", common: false },
      { label: "Donation / grants (charities only)", common: false },
    ],
  },
  {
    group: "Data Protection Lead/Officer",
    items: [
      { label: "Data Subject Access requests", common: true },
      { label: "Breach Reporting", common: true },
      { label: "Data protection Complaints", common: true },
    ],
  },
  {
    group: "Marketing & Comms",
    items: [
      { label: "Promotional material", common: false },
      { label: "Newsletter", common: false },
      { label: "Campaigns", common: false },
    ],
  },
  {
    group: "Other",
    items: [{ label: "Safe Recruiting", common: false }],
  },
] as const;
