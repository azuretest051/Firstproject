import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TasteMatch AI — Epicurean Discovery",
  description:
    "Personalized restaurant picks for Bangalore, explained by AI — budget, cuisine, rating, and vibe.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
          rel="stylesheet"
        />
      </head>
      <body
        className={`${plusJakarta.variable} font-sans bg-surface-container-lowest text-on-surface antialiased selection:bg-primary-container selection:text-on-primary min-h-screen flex flex-col`}
      >
        <Header />
        <main className="w-full pt-16 bg-surface-container-lowest min-h-screen relative flex-1">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[320px] bg-gradient-to-b from-primary-container/10 via-secondary-container/5 to-transparent blur-3xl pointer-events-none -z-10" />
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
