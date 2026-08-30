import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Image de prod Docker minimale : ne copie que le strict nécessaire au
  // runtime (server.js + deps utilisées) au lieu de tout node_modules.
  // Uniquement pour NOTRE build Docker (Phase 14) — Vercel a son propre
  // pipeline de packaging serverless et échoue si ce mode est actif
  // (`ENOENT next-server.js.nft.json`, trouvé en déployant réellement sur
  // Vercel). `VERCEL=1` est fixé automatiquement par leurs builds.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
