ARG DATABASE_URL
ARG BETTER_AUTH_SECRET

FROM node:24-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app



ARG DATABASE_URL
ARG BETTER_AUTH_SECRET
FROM base AS prod
COPY package.json /app
COPY pnpm-lock.yaml /app
RUN pnpm install --frozen-lockfile --prod


COPY . /app
ENV DATABASE_URL=${DATABASE_URL}
RUN echo "DATABASE_URL is set to $DATABASE_URL"
ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
ENV UPLOAD_PATH=/app/uploads
RUN pnpm run build

FROM base
WORKDIR /app
COPY --from=prod /app/node_modules ./node_modules
COPY --from=prod /app/build ./build
EXPOSE 5173
CMD ["node", "build"]