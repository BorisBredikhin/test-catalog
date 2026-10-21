import type { Product, ProductList } from "@/lib/types";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://backend:8000";

export async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${BACKEND_URL}/product`, {
      next: { revalidate: 60 },
    });

    if (!res.ok) {
      console.error(`Backend вернул ${res.status}: ${await res.text()}`);
      return [];
    }

    const data = (await res.json()) as ProductList;
    return data.products ?? [];
  } catch (error) {
    console.error("Не удалось получить товары:", error);
    return [];
  }
}
