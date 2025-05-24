import React from 'react';
import './globals.css';
import type { Metadata } from 'next';
import Script from 'next/script';
import { SearchProvider } from './context/SearchContext';
import SearchModal from './components/SearchModal';
import NowPlaying from './components/NowPlaying';

export const metadata: Metadata = {
  title: 'Carti Catalog',
  description: 'A comprehensive music catalog for Playboi Carti',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Font Awesome for icons */}
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" 
        />
      </head>
      <body className="min-h-screen flex flex-col">
        <SearchProvider>
          <SearchModal />
          {children}
          <NowPlaying />
        </SearchProvider>
        
        {/* Script to load the existing audio manager */}
        <Script src="/js/audio-manager.js" strategy="afterInteractive" />
        <Script src="/js/audio-url-fixer.js" strategy="afterInteractive" />
        <Script src="/js/album-interaction.js" strategy="afterInteractive" />
      </body>
    </html>
  );
}
