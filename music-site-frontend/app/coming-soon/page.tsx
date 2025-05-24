import React from 'react';
import Layout from '../components/Layout';

export default function ComingSoonPage() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
          <h1 className="text-6xl md:text-8xl font-display uppercase tracking-wider mb-6 text-accent">
            Coming Soon
          </h1>
          
          {/* Teaser Image */}
          <div className="relative w-full max-w-2xl mx-auto mb-8">
            <div className="aspect-w-16 aspect-h-9 relative">
              <img 
                src="https://picsum.photos/seed/comingsoon/1000/600" 
                alt="Mysterious Teaser" 
                className="w-full h-full object-cover rounded-lg shadow-2xl"
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black opacity-60"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <img 
                  src="https://picsum.photos/seed/logo/200/200" 
                  alt="Mysterious Logo" 
                  className="w-24 h-24 opacity-80 animate-pulse"
                />
              </div>
            </div>
          </div>
          
          {/* Mysterious Message */}
          <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mb-10 font-mono">
            <span className="inline-block animate-pulse">.</span>
            <span className="inline-block animate-pulse delay-100">.</span>
            <span className="inline-block animate-pulse delay-200">.</span>
            <span className="text-accent">NARCISSIST</span>
            <span className="inline-block animate-pulse delay-200">.</span>
            <span className="inline-block animate-pulse delay-100">.</span>
            <span className="inline-block animate-pulse">.</span>
          </p>
          
          {/* Sign Up Form */}
          <div className="w-full max-w-md">
            <h2 className="text-xl font-medium mb-4">Get Notified</h2>
            <form className="flex flex-col md:flex-row gap-3">
              <input 
                type="email" 
                placeholder="Your Email" 
                className="flex-grow bg-gray-900 text-white border border-gray-700 rounded-md px-4 py-3 focus:outline-none focus:border-accent"
              />
              <button className="btn btn-primary md:w-auto">
                Sign Up
              </button>
            </form>
            <p className="text-sm text-gray-500 mt-2">
              We'll notify you when it drops. No spam.
            </p>
          </div>
          
          {/* Cryptic Countdown */}
          <div className="mt-16">
            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="bg-gray-900 bg-opacity-80 p-4 rounded-lg">
                <div className="text-3xl font-bold">16</div>
                <div className="text-xs text-gray-400">DAYS</div>
              </div>
              <div className="bg-gray-900 bg-opacity-80 p-4 rounded-lg">
                <div className="text-3xl font-bold">23</div>
                <div className="text-xs text-gray-400">HOURS</div>
              </div>
              <div className="bg-gray-900 bg-opacity-80 p-4 rounded-lg">
                <div className="text-3xl font-bold">42</div>
                <div className="text-xs text-gray-400">MINUTES</div>
              </div>
              <div className="bg-gray-900 bg-opacity-80 p-4 rounded-lg">
                <div className="text-3xl font-bold">16</div>
                <div className="text-xs text-gray-400">SECONDS</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
} 