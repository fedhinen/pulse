FROM oven/bun:alpine

WORKDIR /app

COPY package.json bun.lock ./

RUN bun install --frozen-lockfile --production

COPY bootstrap.ts /app/bootstrap.ts

CMD ["bun", "bootstrap.ts"]
