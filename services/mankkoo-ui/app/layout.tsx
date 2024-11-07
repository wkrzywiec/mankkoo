import type { Metadata } from "next";

import "./globals.css";
import { Inter } from 'next/font/google'

import Menu from '@/components/menu/Menu'


const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: "Mankkoo",
  description: "Mankkoo - personal finances",
};

export default function RootLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Menu />
        <div className="content">
          {children}
        </div>
      </body>
    </html>
  );
}
