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
    const res = await fetch(`${BACKEND_URL}/product`, { cache: "no-store" });

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

export default async function Home() {
  const products = await getProducts();

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 p-6">
      <h1 className="mb-6 text-2xl font-bold">Каталог товаров</h1>

      {products.length === 0 ? (
        <p>Товары не найдены.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {products.map((product) => (
            <li
              key={product.id}
              className="flex items-center gap-4 rounded-lg border border-neutral-200 p-4"
            >
              <img
                src={product.photo_url}
                alt={product.name}
                className="h-20 w-20 rounded object-cover"
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
