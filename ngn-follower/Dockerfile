ARG PYTHON_VERSION=3.10

# Builder Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS builder

WORKDIR /app
COPY ngn-follower /app/ngn-follower

RUN pip install build~=0.9.0 && \
    python3 -m build --wheel --outdir /app/dist/ ngn-follower

# Runtime Stage
FROM python:${PYTHON_VERSION}-slim-bullseye AS runtime

# Create a non-root user
RUN useradd ngn \
    && mkdir -p /home/ngn \
    && chown -R ngn:ngn /home/ngn

WORKDIR /home/ngn

ENV PATH=${PATH}:/home/ngn/.local/bin

# Copy from the builder stage
COPY --from=builder /app/dist/ngn_follower*.whl \
    /app/ngn-follower/src/ngn/follower/* \
    /home/ngn/

# Change ownership
RUN chown -R ngn:ngn /home/ngn
USER ngn:ngn

# Install application dependencies
RUN pip install build~=0.9.0 \
    && pip install --user --no-warn-script-location /home/ngn/ngn_follower*.whl \
    && rm /home/ngn/*.whl
