"use client";

import React from "react";

export function Tag({
  children,
  variant = "normal",
}: {
  children: React.ReactNode;
  variant?: "normal" | "common" | "status";
}) {
  const base =
    "inline-flex items-center rounded-full px-2 py-1 text-xs border";

  const styles =
    variant === "common"
      ? "bg-emerald-950 border-emerald-800 text-emerald-200"
      : variant === "status"
      ? "bg-zinc-900 border-zinc-700 text-zinc-200"
      : "bg-zinc-950 border-zinc-800 text-zinc-200";

  return <span className={`${base} ${styles}`}>{children}</span>;
}

