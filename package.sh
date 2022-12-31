#!/usr/bin/env sh

readonly addon_name=mortician
readonly root_dir=$(git rev-parse --show-toplevel)
readonly branch=$(git branch --show-current)
readonly zip_name=${addon_name}_${branch}.ankiaddon

cd -- "$root_dir" || exit 1
rm -- "$zip_name" 2>/dev/null

export root_dir branch

git archive "$branch" --format=zip --output "$zip_name"

# package ajt common
(cd -- ajt_common && git archive HEAD --prefix="${PWD##*/}/" --format=zip -o "$root_dir/${PWD##*/}.zip")

zipmerge "$zip_name" ./*.zip
rm -- ./*.zip
