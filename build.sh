#!/bin/bash
# 重新生成 Packages / Packages.bz2 / Release。
# 用法：把新的 .deb 放进 debs/ 后运行 ./build.sh，然后 git add -A && git commit && git push
cd "$(dirname "$0")"
python3 make-packages.py
