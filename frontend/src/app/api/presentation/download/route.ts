import { NextResponse } from "next/server";

const DOWNLOAD_SLIDES_URL = process.env.DOWNLOAD_SLIDES_URL;

export async function POST(req: Request) {
  try {
    const { title, items, references } = await req.json();
    if (!items || !Array.isArray(items)) {
      return NextResponse.json({ error: "Missing items" }, { status: 400 });
    }
    if (!DOWNLOAD_SLIDES_URL) {
      return NextResponse.json({ error: "DOWNLOAD_SLIDES_URL not set" }, { status: 500 });
    }
    const trimmedReferences = Array.isArray(references) ? references.slice(0, 30) : [];
    console.log("Generating PPT with title:", title, "items:", items, "trimmedReferences:", trimmedReferences);
    // 调用后端PPT生成服务
    const res = await fetch(DOWNLOAD_SLIDES_URL+"/generate-ppt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title, sections: items, references: trimmedReferences || [] }),
    });
    if (!res.ok) {
      return NextResponse.json({ error: "Failed to generate PPT" }, { status: 500 });
    }
    const data = await res.json();
    // 后端返回 { url: "/xxx/xxx" }
    return NextResponse.json({ url: data.ppt_url });
  } catch (e) {
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}