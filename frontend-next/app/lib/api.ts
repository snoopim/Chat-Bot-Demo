// app/lib/api.ts
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8001/api",
  headers: {
    "Content-Type": "application/json",
  },
});
