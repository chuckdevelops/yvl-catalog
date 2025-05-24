'use client';

import React from 'react';
import Layout from './components/Layout';
import AlbumGrid from './components/AlbumGrid';
import CartiFigure from './components/CartiFigure';

export default function Home() {
  return (
    <Layout>
      <div className="space-y-12">
        <CartiFigure />
        <AlbumGrid />
      </div>
    </Layout>
  );
}
