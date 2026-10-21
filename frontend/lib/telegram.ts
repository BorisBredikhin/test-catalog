/**
 * Типы Telegram Mini App.
 *
 * Данные из `initData` нельзя использовать для авторизации на своей стороне —
 * подпись проверяет бэкенд. Здесь они нужны только для отображения.
 */

export type TelegramUser = {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  photoUrl?: string;
  languageCode?: string;
};

export type TelegramState = {
  /** Приложение запущено внутри Telegram. */
  isTelegram: boolean;
  /** SDK инициализирован (вне Telegram — сразу true). */
  ready: boolean;
  /** Сырая initData: её подпись проверяет бэкенд. */
  initData?: string;
  /** Пользователь из initData — только для отображения. */
  user?: TelegramUser;
  /** tgWebAppPlatform: ios / android / web / tdelegram и т.п. */
  platform?: string;
  /** Версия Bot API, доступная клиенту. */
  version?: string;
};
