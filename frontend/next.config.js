/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      'localhost',
      'images.unsplash.com',
      'source.unsplash.com',
      // Add your news sources domains here
      'cdn.cnn.com',
      'ichef.bbci.co.uk',
      'static01.nyt.com',
      'www.reuters.com',
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
};

module.exports = nextConfig;
