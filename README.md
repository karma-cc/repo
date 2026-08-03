# karma-cc 越狱源

一个标准的 Cydia / Sileo 兼容 apt 源，托管在 GitHub Pages 上。

## 添加源（iOS 设备）

打开 **Sileo** 或 **Cydia**，添加源：

```
https://karma-cc.github.io/repo/
```

添加后即可看到仓库中的插件包。

## 目录结构

```
repo/
├── Packages          # 包索引（apt 读取）
├── Packages.bz2      # 压缩版索引
├── Release           # 仓库元数据 + 校验和
├── CydiaIcon.png     # 源图标
├── debs/             # 放你的 .deb 包
│   └── com.karma.example_1.0.0_iphoneos-arm64.deb  # 示例包，可删除
├── make-packages.py  # 索引生成器（纯 Python，无需 dpkg）
└── build.sh          # 一键重新生成索引
```

## 发布新插件

1. 把编译好的 `.deb` 放进 `debs/`；
2. 运行 `./build.sh` 重新生成索引；
3. 提交并推送（GitHub Pages 会自动更新）。

示例包 `com.karma.example` 只是用来验证源是否可用，安装没有实际效果，验证完可删除 `debs/com.karma.example_1.0.0_iphoneos-arm64.deb` 并重新运行 `./build.sh`。

## 要求

- 每个 `.deb` 必须包含 `Package`、`Version`、`Architecture`、`Maintainer`、`Description` 字段，否则会被跳过。
- 支持的架构声明：`iphoneos-arm`（rootful）、`iphoneos-arm64`（rootless）、`iphoneos-arm64e`。
