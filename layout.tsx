import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Mankkoo",
  description: "Mankkoo - personal finances",
};

export default function RootLayout({ children, }: Readonly<{children: React.ReactNode;}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <div className="main">
          <div className="menu">
            <ul>
              <li className="menuHeader">Mankkoo</li>
              <li>Overview</li>
              <li>Investments</li>
              <li>Streams</li>
            </ul>
          </div>
          <div className="content">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
