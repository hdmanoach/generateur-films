import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";

// Fraunces : serif à forte présence pour les titres, évoque l'affiche de cinéma
const fraunces = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "600", "900"],
});

// Inter : sans-serif neutre pour l'interface, très lisible en petite taille
const inter = Inter({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  // ⚠️ Remplace par ton vrai nom de domaine une fois déployé (même valeur
  // que dans sitemap.ts et robots.ts)
  metadataBase: new URL("https://ton-domaine.com"),
  title: "Deux films, une trouvaille",
  description:
    "Donne deux films que tu aimes, on te trouve le prochain à voir.",
  openGraph: {
    title: "Deux films, une trouvaille",
    description:
      "Donne deux films que tu aimes, on te trouve le prochain à voir.",
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