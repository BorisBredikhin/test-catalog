export type Product = {
  id: string;
  name: string;
  photo_url: string;
};

export type ProductList = {
  products: Product[];
};

/** Профиль пользователя Telegram, полученный от бэкенда после проверки initData. */
export type TelegramProfile = {
  id: number;
  first_name: string;
  last_name: string | null;
  username: string | null;
  language_code: string | null;
  photo_url: string | null;
  is_admin: boolean;
};
