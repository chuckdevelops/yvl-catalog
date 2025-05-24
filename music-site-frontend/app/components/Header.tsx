
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronDown, Menu, X, Search, MessageCircle } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/coming-soon?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };
  
  return (
    <header className="w-full py-4 px-6 border-b border-white/10 backdrop-blur-md bg-black/70 fixed top-0 left-0 right-0 z-50">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-xl hover:text-white/80 transition-colors carti-font tracking-wider flex items-center">
          CARTI CATALOG
        </Link>
        
        {/* Mobile menu button */}
        <button 
          className="md:hidden text-white hover:text-white/80"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
        
        {/* Desktop navigation */}
        <div className="hidden md:flex items-center space-x-6">
          <nav>
            <ul className="flex space-x-8">
              <li className="nav-item">
                <Link to="/" className="nav-link text-sm tracking-wide">Home</Link>
              </li>
              <li className="nav-item">
                <Link to="/songs" className="nav-link text-sm tracking-wide">Music</Link>
              </li>
              <li className="nav-item">
                <DropdownMenu>
                  <DropdownMenuTrigger className="nav-link flex items-center text-sm tracking-wide">
                    Media <ChevronDown className="h-4 w-4 ml-1" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="bg-black border border-white/10 text-white">
                    <DropdownMenuItem asChild>
                      <Link to="/fit-pics" className="w-full hover:bg-white/5">Fit Pics</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/interviews" className="w-full hover:bg-white/5">Interviews</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/social-media" className="w-full hover:bg-white/5">Social Media</Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </li>
              <li className="nav-item peace-sign-nav">
                <Link to="/coming-soon" className="nav-link flex items-center">
                  <img 
                    src="/lovable-uploads/42459934-4b78-4834-9817-96218cc02c96.png" 
                    alt="Peace Sign" 
                    className="h-6 w-6 hover:scale-110 transition-transform"
                    style={{ filter: "invert(100%)" }}
                  />
                </Link>
              </li>
              <li className="nav-item">
                <a 
                  href="https://discord.gg/playboicarti" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="nav-link flex items-center"
                  aria-label="Join our Discord server"
                >
                  <MessageCircle className="h-5 w-5 hover:scale-110 transition-transform hover:text-indigo-400" />
                </a>
              </li>
            </ul>
          </nav>
          
          <form onSubmit={handleSearch} className="flex">
            <div className="relative flex items-center">
              <input 
                type="search" 
                placeholder="Search" 
                className="pl-8 pr-3 py-1 bg-white/5 text-white border border-white/10 rounded-md focus:outline-none focus:ring-1 focus:ring-white/30 w-40 transition-all focus:w-56"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Search className="absolute left-2 h-4 w-4 text-white/50" />
            </div>
          </form>
        </div>
        
        {/* Mobile navigation */}
        {mobileMenuOpen && (
          <div className="absolute top-full left-0 right-0 bg-black border-b border-white/10 py-4 md:hidden shadow-lg slide-up">
            <nav className="container mx-auto px-6">
              <ul className="space-y-4">
                <li>
                  <Link 
                    to="/" 
                    className="block py-2 text-white hover:text-white/80"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Home
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/songs" 
                    className="block py-2 text-white hover:text-white/80"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Music
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/fit-pics" 
                    className="block py-2 text-white hover:text-white/80"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Fit Pics
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/interviews" 
                    className="block py-2 text-white hover:text-white/80"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Interviews
                  </Link>
                </li>
                <li>
                  <Link 
                    to="/social-media" 
                    className="block py-2 text-white hover:text-white/80"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Social Media
                  </Link>
                </li>
                <li>
                  <a 
                    href="https://discord.gg/playboicarti" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block py-2 text-white hover:text-indigo-400 flex items-center"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <MessageCircle className="h-5 w-5 mr-2" /> Discord
                  </a>
                </li>
                <li>
                  <form onSubmit={handleSearch} className="mt-4">
                    <input 
                      type="search" 
                      placeholder="Search" 
                      className="w-full px-3 py-2 bg-white/5 text-white border border-white/10 rounded-md focus:outline-none focus:ring-1 focus:ring-white/30"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </form>
                </li>
              </ul>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
