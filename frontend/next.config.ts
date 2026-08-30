import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Image de prod Docker minimale : ne copie que le strict nécessaire au
  // runtime (server.js + deps utilisées) au lieu de tout node_modules.
  output: "standalone",
};

export default nextConfig;
