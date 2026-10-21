/**
 * Локальная имитация Telegram Mini App.
 *
 * Telegram открывает Mini App только по HTTPS, поэтому локально приложение
 * живёт в обычном браузере. Чтобы проверить тему, авторизацию и разметку
 * так же, как внутри Telegram, подставьте поддельные launch-параметры:
 *
 *   http://localhost:3000/?tgWebAppData=<initData>
 *
 * или через переменную окружения:
 *
 *   NEXT_PUBLIC_TELEGRAM_INIT_DATA=<initData> pnpm dev
 *
 * initData генерируется скриптом `backend/scripts/make_init_data.py`.
 * Внимание: initData — это подписанный Telegram идентификатор пользователя,
 * не коммитьте его в репозиторий.
 */

/** Параметры запуска, которыми имитируем Telegram. */
const MOCK_LAUNCH_PARAMS = {
  tgWebAppPlatform: "web",
  tgWebAppVersion: "8.0",
  tgWebAppThemeParams: {
    bg_color: "#ffffff",
    text_color: "#000000",
    hint_color: "#707579",
    link_color: "#2481cc",
    button_color: "#2481cc",
    button_text_color: "#ffffff",
    secondary_bg_color: "#f1f1f1",
  },
} as const;

/** initData для имитации: из query-параметра или из переменной окружения. */
export function devInitData(): string | undefined {
  if (typeof window === "undefined") return undefined;

  const fromQuery = new URLSearchParams(window.location.search).get("tgWebAppData");
  if (fromQuery) return fromQuery;

  return process.env.NEXT_PUBLIC_TELEGRAM_INIT_DATA || undefined;
}

/**
 * Подменяет окружение Telegram, чтобы SDK считал приложение запущенным
 * внутри мессенджера. Вызывать нужно до `sdk.init()`.
 */
export function applyDevMock(sdk: typeof import("@telegram-apps/sdk")): void {
  const initData = devInitData();
  if (!initData) return;

  sdk.mockTelegramEnv({
    launchParams: {
      ...MOCK_LAUNCH_PARAMS,
      tgWebAppData: initData,
    },
  });

  console.info(
    "Telegram Mini App: используется локальная имитация окружения Telegram",
  );
}
