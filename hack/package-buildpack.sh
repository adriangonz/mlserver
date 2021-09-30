#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o pipefail

ROOT_FOLDER="$(dirname "${0}")/.."

if [ "$#" -ne 1 ]; then
  echo "Usage: ./prepare-buildpack.sh <buildpackName>"
  exit 1
fi

_buildPackages() {
  make -C $ROOT_FOLDER build-pypi
}

_copyFiles() {
  local _buildpackPath=$1

  mkdir -p "$_buildpackPath/mlserver"
  cp "$ROOT_FOLDER/dist/"* "$_buildpackPath/mlserver"

  cp "$ROOT_FOLDER/buildpack.toml" $_buildpackPath
  cp "$ROOT_FOLDER/package.toml" $_buildpackPath
  cp -r "$ROOT_FOLDER/bin" $_buildpackPath
}

_packageBuildpack() {
  local _buildpackPath=$1
  local _buildpackName=$2

  pack buildpack package \
    $_buildpackName \
    --config "$_buildpackPath/package.toml"
}

_main() {
  local _buildpackName=$1
  local _tempFolder=$(mktemp -d)

  # Remove temporary folder at the end
  trap "rm -rf -- '${_tempFolder}'" EXIT

  echo "---> Building MLServer packages"
  _buildPackages

  echo "---> Preparing Buildpack folder"
  _copyFiles $_tempFolder

  echo "---> Packaging Buildpack"
  _packageBuildpack $_tempFolder $_buildpackName
}

_main $1
