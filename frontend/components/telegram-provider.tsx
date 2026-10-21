"use client";

import { createContext, useContext, useEffect, useState } from "react";

import type { TelegramState, TelegramUser } from "@/lib/telegram";
import { applyDevMock } from "@/lib/telegram-dev";

const TelegramContext = createContext<TelegramState>({
  isTelegram: false,
  ready: false,
});

/** Доступ к состоянию Telegram Mini App. */
export function useTelegram(): TelegramState {
  return useContext(TelegramContext);
}

/**
 * Инициализирует Telegram Mini App SDK: поднимает тему, viewport и
 * сообщает Telegram, что приложение готово к показу.
 *
 * SDK импортируется динамически — на сервере `window` недоступен, да и
 * запускать его вне Telegram бессмысленно.
 */
export function TelegramProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<TelegramState>({
    isTelegram: false,
    ready: false,
  });

  useEffect(() => {
    let disposed = false;
    let cleanup: (() => void) | undefined;

    void (async () => {
      try {
        const sdk = await import("@telegram-apps/sdk");
        if (disposed) return;

        // Локально Telegram недоступен — подменяем окружение (см. lib/telegram-dev.ts).
        applyDevMock(sdk);

        if (!sdk.isTMA()) {
          // Обычный браузер: приложение работает как обычный сайт.
          setState({ isTelegram: false, ready: true });
          return;
        }

        cleanup = sdk.init();

        const initData = readInitData(sdk);
        const user = readUser(sdk);
        const launchParams = readLaunchParams(sdk);

        await mountTheme(sdk);
        await mountMiniApp(sdk);
        mountViewport(sdk);

        if (disposed) return;

        setState({
          isTelegram: true,
          ready: true,
          initData,
          user,
          platform: launchParams?.tgWebAppPlatform,
          version: launchParams?.tgWebAppVersion,
        });
      } catch (error) {
        console.error("Не удалось инициализировать Telegram Mini App SDK", error);
        if (!disposed) {
          setState({ isTelegram: false, ready: true });
        }
      }
    })();

    return () => {
      disposed = true;
      cleanup?.();
    };
  }, []);

  return (
    <TelegramContext.Provider value={state}>{children}</TelegramContext.Provider>
  );
}

/**
 * Сырая initData нужна бэкенду для проверки HMAC-подписи.
 *
 * В SDK 3.x `initData.restore()` надо вызывать явно — `init()` этого не делает.
 * Если разбор не удался (например, у клиента нет поля `signature`), берём
 * строку напрямую: подпись всё равно проверит бэкенд.
 */
function readInitData(
  sdk: typeof import("@telegram-apps/sdk"),
): string | undefined {
  try {
    sdk.initData.restore();
    return sdk.initData.raw();
  } catch (error) {
    console.warn("Не удалось разобрать initData", error);
  }

  try {
    return sdk.retrieveRawInitData();
  } catch (error) {
    console.warn("Не удалось получить сырую initData", error);
    return undefined;
  }
}

function readUser(
  sdk: typeof import("@telegram-apps/sdk"),
): TelegramUser | undefined {
  const user = sdk.initData.user();
  if (!user) return undefined;

  return {
    id: user.id,
    firstName: user.first_name,
    lastName: user.last_name,
    username: user.username,
    photoUrl: user.photo_url,
    languageCode: user.language_code,
  };
}

function readLaunchParams(
  sdk: typeof import("@telegram-apps/sdk"),
): { tgWebAppPlatform?: string; tgWebAppVersion?: string } | undefined {
  try {
    return sdk.retrieveLaunchParams(true);
  } catch (error) {
    console.warn("Не удалось получить параметры запуска Telegram", error);
    return undefined;
  }
}

/** Цвета Telegram → CSS-переменные `--tg-theme-*`. */
async function mountTheme(sdk: typeof import("@telegram-apps/sdk")): Promise<void> {
  try {
    await sdk.themeParams.mount();
    sdk.themeParams.bindCssVars();
  } catch (error) {
    console.warn("Не удалось применить тему Telegram", error);
  }
}

/**
 * Размеры вьюпорта и safe area приходят от Telegram асинхронно, а ответа
 * может не быть вовсе — поэтому не блокируем показ приложения.
 */
function mountViewport(sdk: typeof import("@telegram-apps/sdk")): void {
  void sdk.viewport
    .mount()
    .then(() => sdk.viewport.bindCssVars())
    .catch((error) => {
      console.warn("Не удалось получить размеры вьюпорта Telegram", error);
    });

  try {
    sdk.viewport.expand();
  } catch (error) {
    console.warn("Не удалось развернуть Mini App на всю высоту", error);
  }
}

/** Готовность приложения, цвета шапки и фона. */
async function mountMiniApp(
  sdk: typeof import("@telegram-apps/sdk"),
): Promise<void> {
  try {
    await sdk.miniApp.mount();
  } catch (error) {
    console.warn("Не удалось подключить Mini App", error);
  }

  try {
    sdk.miniApp.ready();
  } catch (error) {
    console.warn("Не удалось сообщить Telegram о готовности", error);
  }

  try {
    sdk.miniApp.setHeaderColor("bg_color");
    sdk.miniApp.setBackgroundColor("bg_color");
  } catch (error) {
    console.warn("Не удалось применить цвета Telegram", error);
  }
}
