/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  swcMinify: true,
  basePath: process.env.NEXT_PUBLIC_BASE_PATH,
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH,
  distDir: "build",
  images: {
    domains: [
      "images.unsplash.com",
      "i.ibb.co",
      "scontent.fotp8-1.fna.fbcdn.net",
    ],
    // Make ENV
    unoptimized: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
