import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker での薄いイメージ化のため `.next/standalone` を生成する
  // ref: node_modules/next/dist/docs/01-app/03-api-reference/05-config/01-next-config-js/output.md
  output: "standalone",
};

export default nextConfig;
