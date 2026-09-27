#!/usr/bin/env bash
# Lambda(arm64, Python3.12)向けのデプロイパッケージをビルドする。
# psycopg2等のコンパイル済み依存を避けるため、依存はすべてmanylinuxのビルド済みwheelを使う想定。
set -euo pipefail

# terraformのlocal-execは/bin/shの最小PATHで実行されるため明示的に補う
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH}"

INFRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${INFRA_DIR}/../backend"
BUILD_DIR="${INFRA_DIR}/build/lambda"

rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

python3.12 -m pip install \
  --platform manylinux2014_aarch64 \
  --target "${BUILD_DIR}" \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  --upgrade \
  -r "${BACKEND_DIR}/requirements.txt"

cp -R "${BACKEND_DIR}/src" "${BUILD_DIR}/src"

echo "Lambda package built at ${BUILD_DIR}"
