import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";

const fraunces = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "600", "900"],
});

const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://generateur-films.vercel.app"),
  title: "Deux films, une trouvaille — Générateur de suggestions de films et séries par IA",
  description:
    "Donne deux films ou séries que tu aimes, découvre une suggestion personnalisée générée par IA à partir de tes goûts.",
  keywords: [
    "suggestion film",
    "recommandation film",
    "film similaire",
    "quel film regarder",
    "générateur de films",
    "recommandation série",
    "quelle série regarder",
    "IA films",
    "découvrir un film",
    "film comme",
    "série comme",
  ],
  openGraph: {
    title: "Deux films, une trouvaille",
    description:
      "Donne deux films ou séries que tu aimes, découvre une suggestion personnalisée générée par IA.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body className={`${fraunces.variable} ${inter.variable} film-grain`}>
        {children}
      </body>
    </html>
  );
}