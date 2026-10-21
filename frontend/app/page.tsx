import Image from "next/image";

import { getProducts } from "@/lib/api";
import { toInternalSrc } from "@/lib/images";

export default async function Home() {
  "use cache";
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
