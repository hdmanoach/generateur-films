import type { MetadataRoute } from "next";

// ⚠️ Remplace par ton vrai nom de domaine une fois déployé
const SITE_URL = "https://ton-domaine.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
