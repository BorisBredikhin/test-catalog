# MinIO собран из исходников: официальные Docker-образы minio/minio
# удалены с Docker Hub и Quay.io (сентябрь 2025), репозиторий заархивирован.
FROM golang:1.24-bookworm AS build

ARG MINIO_RELEASE=RELEASE.2025-10-15T17-29-55Z

RUN git clone --depth 1 --branch "${MINIO_RELEASE}" \
    https://github.com/minio/minio.git /src
WORKDIR /src

RUN go mod download

# Рецепт из Makefile проекта (build-таргет), CGO выключено — статический бинарник
RUN LDFLAGS="$(go run buildscripts/gen-ldflags.go)" \
    && CGO_ENABLED=0 go build -tags kqueue -trimpath \
       --ldflags "${LDFLAGS}" -o /out/minio

FROM alpine:3.22

RUN apk add --no-cache ca-certificates tzdata

COPY --from=build /out/minio /usr/bin/minio

EXPOSE 9000 9001
VOLUME /data

ENTRYPOINT ["/usr/bin/minio"]
CMD ["server", "/data", "--console-address", ":9001"]
