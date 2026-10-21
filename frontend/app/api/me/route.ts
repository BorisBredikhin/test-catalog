import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://backend:8000";

/**
 * Прокси к бэкенду: initData уходит в заголовке, бэкенд проверяет подпись
 * и возвращает профиль пользователя. Запрос идёт через same-origin,
 * поэтому CORS настраивать не нужно.
 */
export async function GET(request: NextRequest) {
  const initData = request.headers.get("x-telegram-init-data");

  if (!initData) {
    return NextResponse.json(
      { detail: "Заголовок X-Telegram-Init-Data обязателен" },
      { status: 401 },
    );
  }

  try {
    const res = await fetch(`${BACKEND_URL}/me`, {
      headers: { "X-Telegram-Init-Data": initData },
      cache: "no-store",
    });

    return new NextResponse(res.body, {
      status: res.status,
      headers: {
        "content-type":
          res.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    console.error("Не удалось получить профиль пользователя:", error);
    return NextResponse.json(
      { detail: "Бэкенд недоступен" },
      { status: 502 },
    );
  }
}
