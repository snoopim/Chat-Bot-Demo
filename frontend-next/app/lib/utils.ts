// app/lib/utils.ts

/**
 * Normalize yes/no so depends_on works even if user writes "No, ..." etc
 */
export function normalizeYesNo(text?: string | null): string {
  const t = (text || "").trim().toLowerCase();
  if (t.startsWith("y")) return "yes";
  if (t.startsWith("n")) return "no";
  return "";
}

/**
 * Trigger a file download from a Blob
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}
