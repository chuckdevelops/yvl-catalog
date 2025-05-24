
const Footer = () => {
  return (
    <footer className="py-6 border-t border-white/10 backdrop-blur-md bg-black/30">
      <div className="container mx-auto px-4 text-center">
        <p className="carti-font text-sm flex items-center justify-center text-white/80 hover-scale">
          CARTI CATALOG © {new Date().getFullYear()}
          <span className="album-row ml-2 flex items-center">
            <img className="album-icon spin mx-1" src="https://cache.umusic.com/_sites/playboicarti.com/images/products/CD13-375x375-1.png" alt="Whole Lotta Red" />
            <img className="album-icon mx-1" src="https://cache.umusic.com/_sites/playboicarti.com/images/products/CD10-375x375-1.png" alt="Die Lit" />
            <img className="album-icon mx-1" src="https://cache.umusic.com/_sites/playboicarti.com/images/products/CD11-375x375-1.png" alt="Self Titled" />
          </span>
        </p>
      </div>
    </footer>
  );
};

export default Footer;
