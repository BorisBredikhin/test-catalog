import Image from "next/image";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://backend:8000";

type Product = {
  id: string;
  name: string;
  photo_url: string;
};

type ProductList = {
  products: Product[];
};

async function getProducts(): Promise<Product[]> {
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

// В БД фото может лежать и абсолютным URL MinIO (http://localhost:9000/...),
// и корневым относительным путём. next/image оптимизирует только свои пути и
// разрешённые remote-хосты, а ходить в MinIO напрямую из контейнера нельзя —
// нормализуем к пути: rewrite в next.config отдаст его через MinIO.
function toInternalSrc(url: string): string {
  if (!/^https?:\/\//.test(url)) {
    return url;
  }
  return new URL(url).pathname;
}

export default async function Home() {
  "use cache";
  const products = await getProducts();

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 p-6">
      <h1 className="mb-6 text-2xl font-bold">Каталог</h1>

      {products.length === 0 ? (
        <p>Товары не найдены.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {products.map((product) => (
            <li
              key={product.id}
              className="flex items-center gap-4 rounded-lg border border-neutral-200 p-4"
            >
              <Image
                src={toInternalSrc(product.photo_url)}
                alt={product.name}
                className="h-20 w-20 rounded object-cover"
                width={80}
                height={80}
              />
              <div>
                <p className="font-medium">{product.name}</p>
                <p className="text-sm text-neutral-500">{product.id}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
