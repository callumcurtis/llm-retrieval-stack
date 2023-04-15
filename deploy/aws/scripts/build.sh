#!/usr/bin/env bash

runtime=$1
src_code=$2
build_path=$3
output_name=$4
resource_type=$5

[[ -z "$runtime" ]]       && echo "ERROR: runtime is not defined"       && exit 1
[[ -z "$src_code" ]]      && echo "ERROR: src_code is not defined"      && exit 1
[[ -z "$build_path" ]]    && echo "ERROR: build_path is not defined"    && exit 1
[[ -z "$output_name" ]]   && echo "ERROR: output_name is not defined"   && exit 1
[[ -z "$resource_type" ]] && echo "ERROR: resource_type is not defined" && exit 1

parent_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
runtime_builds_dir=${parent_dir}/runtime

if [[ "${runtime}" == "python3.9" ]]; then
  bash ${runtime_builds_dir}/py_build.sh ${src_code} ${build_path} ${output_name} ${resource_type}
else
  echo "ERROR: Only python3.9 is currently supported"
  exit 1
fi