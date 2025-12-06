#!/usr/bin/env bash
set -e

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <target_name>"
  exit 1
fi

OS_TYPE=$(uname -s)

cd external/greener-reporter
cargo build --release

if [[ "$OS_TYPE" == "Darwin" ]]; then
  install_name_tool -id @rpath/libgreener_reporter.dylib target/release/libgreener_reporter.dylib
  install_name_tool -id @rpath/libgreener_servermock.dylib target/release/libgreener_servermock.dylib
elif [[ "$OS_TYPE" == "MINGW"* || "$OS_TYPE" == "MSYS"* || "$OS_TYPE" == "CYGWIN"* ]]; then
  cp target/release/greener_reporter.dll.lib target/release/greener_reporter.lib
  cp target/release/greener_servermock.dll.lib target/release/greener_servermock.lib
fi

cargo test --release

cd ../..

if [[ "$OS_TYPE" == "Darwin" ]]; then
  cp external/greener-reporter/target/release/libgreener_reporter.dylib greener_reporter/greener_reporter/
  cp external/greener-reporter/target/release/libgreener_servermock.dylib greener_servermock/greener_servermock/
elif [[ "$OS_TYPE" == "Linux" ]]; then
  cp external/greener-reporter/target/release/libgreener_reporter.so greener_reporter/greener_reporter/
  cp external/greener-reporter/target/release/libgreener_servermock.so greener_servermock/greener_servermock/
elif [[ "$OS_TYPE" == "MINGW"* || "$OS_TYPE" == "MSYS"* || "$OS_TYPE" == "CYGWIN"* ]]; then
  cp external/greener-reporter/target/release/greener_reporter.dll greener_reporter/greener_reporter/
  cp external/greener-reporter/target/release/greener_reporter.lib greener_reporter/greener_reporter/
  cp external/greener-reporter/target/release/greener_servermock.dll greener_servermock/greener_servermock/
  cp external/greener-reporter/target/release/greener_servermock.lib greener_servermock/greener_servermock/
fi
