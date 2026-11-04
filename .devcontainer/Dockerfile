# The container MathWiz runs in on the Spark.

FROM python:3.12-slim-bookworm

# Node, for `npm ci` / `npm run build`
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

RUN apt-get update && apt-get install -y --no-install-recommends \
        # pip builds pycairo and manimpango from source on the Spark (an ARM machine); these are the compiler and the libraries they build against.
        build-essential pkg-config libcairo2-dev libpango1.0-dev \
        # Manim's Text() draws with system fonts. The slim image has none, so we install them.
        fonts-dejavu-core \
        # tmux keeps the server running after we disconnect (deploy/run.sh). curl lets run.sh check the server answers. git for `git status` etc.
        tmux curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
