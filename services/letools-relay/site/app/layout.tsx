import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LE-filter 角色读取服务",
  description: "为 LE-filter 工作台读取 LETools 公开角色配装。",
};

export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
