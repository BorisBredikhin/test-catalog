// В БД фото может лежать и абсолютным URL MinIO (http://localhost:9000/...),
// и корневым относительным путём. next/image оптимизирует только свои пути и
// разрешённые remote-хосты, а ходить в MinIO напрямую из контейнера нельзя —
// нормализуем к пути: rewrite в next.config отдаст его через MinIO.
export function toInternalSrc(url: string): string {
  if (!/^https?:\/\//.test(url)) {
    return url;
  }
  return new URL(url).pathname;
}
