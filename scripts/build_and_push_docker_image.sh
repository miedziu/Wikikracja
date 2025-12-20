#!/bin/sh
set -eu

if ! command -v docker >/dev/null 2>&1; then
    echo "docker is required"
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "git is required"
    exit 1
fi

REGISTRY_IMAGE_DEFAULT="registry.gitlab.com/robert.fialek/wiki-prv"
REGISTRY_IMAGE="${REGISTRY_IMAGE:-$REGISTRY_IMAGE_DEFAULT}"

CONFIRM_OFFICIAL_PUSH="${CONFIRM_OFFICIAL_PUSH:-0}"

if [ -z "$REGISTRY_IMAGE" ]; then
    cat <<EOF

REGISTRY_IMAGE is required.

Set REGISTRY_IMAGE explicitly, e.g.:
  REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh
EOF
    exit 1
fi

if [ "$REGISTRY_IMAGE" = "$REGISTRY_IMAGE_DEFAULT" ] && [ "$CONFIRM_OFFICIAL_PUSH" != "1" ]; then
    cat <<EOF

Refusing to push to the official image name by default:
  $REGISTRY_IMAGE_DEFAULT

If you are the maintainer and intentionally want to push the official image, run:
  CONFIRM_OFFICIAL_PUSH=1 ./scripts/build_and_push_docker_image.sh

Otherwise, set REGISTRY_IMAGE to your own namespace:
  REGISTRY_IMAGE=registry.gitlab.com/<group>/<project> ./scripts/build_and_push_docker_image.sh
EOF
    exit 1
fi

TAG="${TAG:-$(git rev-parse --short HEAD)}"
PUSH_LATEST="${PUSH_LATEST:-1}"

echo "Building ${REGISTRY_IMAGE}:${TAG}"
docker build -t "${REGISTRY_IMAGE}:${TAG}" .

if [ "$PUSH_LATEST" = "1" ]; then
    docker tag "${REGISTRY_IMAGE}:${TAG}" "${REGISTRY_IMAGE}:latest"
fi

echo "Pushing ${REGISTRY_IMAGE}:${TAG}"
docker push "${REGISTRY_IMAGE}:${TAG}"

if [ "$PUSH_LATEST" = "1" ]; then
    echo "Pushing ${REGISTRY_IMAGE}:latest"
    docker push "${REGISTRY_IMAGE}:latest"
fi

cat <<EOF

Done.

Notes:
- You must be logged in: docker login registry.gitlab.com
- Override image name: REGISTRY_IMAGE=registry.gitlab.com/<group>/<project>
- Override tag: TAG=v1.2.3
- Disable latest: PUSH_LATEST=0
EOF
