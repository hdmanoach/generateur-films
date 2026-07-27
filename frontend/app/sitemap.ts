import type { MetadataRoute } from "next";

// ⚠️ Remplace par ton vrai nom de domaine une fois déployé
const SITE_URL = "https://ton-domaine.com";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 1,
    },
  ];
}
