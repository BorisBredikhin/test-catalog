"use client";

import { useEffect, useState } from "react";

import { useTelegram } from "@/components/telegram-provider";
import type { TelegramProfile } from "@/lib/types";

/**
 * Шапка приложения: показывает, внутри Telegram мы или нет, и подтверждает
 * авторизацию — профиль приходит с бэкенда, где подпись initData уже проверена.
 */
export function TelegramHeader() {
  const { isTelegram, user, initData } = useTelegram();
  const [profile, setProfile] = useState<TelegramProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!initData) return;

    const controller = new AbortController();

    void (async () => {
      try {
        const res = await fetch("/api/me", {
          headers: { "X-Telegram-Init-Data": initData },
          signal: controller.signal,
        });

        if (!res.ok) {
          setError(`Ошибка авторизации: ${res.status}`);
          return;
        }

        setProfile((await res.json()) as TelegramProfile);
      } catch (fetchError) {
        if ((fetchError as Error).name === "AbortError") return;
        setError("Не удалось связаться с сервером");
      }
    })();

    return () => controller.abort();
  }, [initData]);

  if (!isTelegram) {
    return (
      <p className="mb-4 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--muted)]">
        Каталог открыт в браузере. В Telegram он запускается как Mini App по
        кнопке в чате с ботом.
      </p>
    );
  }

  const displayName =
    profile?.first_name ??
    user?.firstName ??
    "Пользователь Telegram";

  return (
    <div className="mb-6 flex items-center justify-between gap-3">
      <div className="flex min-w-0 items-center gap-3">
        {user?.photoUrl ? (
          // Фото из Telegram — внешний домен, next/image его не оптимизирует.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={user.photoUrl}
            alt=""
            className="h-9 w-9 shrink-0 rounded-full object-cover"
          />
        ) : null}
        <div className="min-w-0">
          <p className="truncate font-medium">{displayName}</p>
          <p className="truncate text-sm text-[var(--muted)]">
            {profile
              ? `Авторизация подтверждена · id ${profile.id}`
              : "Проверяем авторизацию…"}
          </p>
        </div>
      </div>

      <span className="shrink-0 rounded-full bg-[var(--surface)] px-3 py-1 text-xs text-[var(--muted)]">
        Mini App
      </span>

      {error ? (
        <p className="w-full text-sm text-red-600 dark:text-red-400">{error}</p>
      ) : null}
    </div>
  );
}
