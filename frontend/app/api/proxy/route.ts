import { NextRequest } from "next/server";

const MINIO_URL = process.env.MINIO_PUBLIC_URL ?? "http://minio:9000"

export async function GET(request: NextRequest) {
    const path = request.nextUrl.pathname.replace('/api/minio', ''); // убираем префикс маршрута
    const url = `${MINIO_URL}${path}${request.url.split('?')[1] ? '?' + request.url.split('?')[1] : ''}`;

    try {
        const res = await fetch(url, {
            headers: {
                'Host': new URL(MINIO_URL).host, // критично для S3: Host должен совпадать с endpoint
                // остальные заголовки можно пробрасывать выборочно, но не все
            },
            method: request.method,
            body: request.body,
            cache: 'no-store',
        });

        const headers = new Headers(res.headers);
        // Важно: Content-Type и Content-Length нужно обязательно пробросить
        return new NextResponse(res.body as any, {
            status: res.status,
            headers,
        });
    } catch (e) {
        return NextResponse.json({ error: 'Proxy failed' }, { status: 502 });
    }
}