import { useState, useEffect } from 'react';

export default function Header() {
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    const currentPath = typeof window !== 'undefined' ? window.location.pathname : '';

    return (
        <>
            <style>{`
        .ap-nav {
          position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
          transition: all 0.4s ease;
          padding: 0 32px; height: 68px;
          display: flex; align-items: center; justify-content: space-between;
          font-family: 'Sora', sans-serif;
        }
        .ap-nav.scrolled {
          background: rgba(8, 17, 32, 0.92);
          backdrop-filter: blur(24px);
          border-bottom: 1px solid rgba(0, 196, 180, 0.12);
          box-shadow: 0 4px 32px rgba(0,0,0,0.4);
        }
        .ap-nav.top {
          background: linear-gradient(180deg, rgba(8,17,32,0.7) 0%, transparent 100%);
        }
        .ap-logo {
          display: flex; align-items: center; gap: 10px;
          text-decoration: none;
        }
        .ap-logo-icon {
          width: 38px; height: 38px; border-radius: 11px;
          background: linear-gradient(135deg, #00C4B4 0%, #00E5FF 100%);
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 20px rgba(0,196,180,0.35);
          position: relative; overflow: hidden;
        }
        .ap-logo-icon::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent);
        }
        .ap-logo-text {
          font-size: 18px; font-weight: 800; letter-spacing: -0.4px;
          color: #fff;
        }
        .ap-logo-text span { color: #00C4B4; }
        .ap-nav-links {
          display: flex; gap: 36px; align-items: center;
          list-style: none; margin: 0; padding: 0;
        }
        .ap-nav-links a {
          color: rgba(255,255,255,0.65);
          text-decoration: none;
          font-size: 14px; font-weight: 500;
          letter-spacing: 0.1px;
          transition: color 0.2s;
          position: relative;
        }
        .ap-nav-links a::after {
          content: '';
          position: absolute; bottom: -4px; left: 0; right: 0;
          height: 1.5px; background: #00C4B4;
          transform: scaleX(0);
          transition: transform 0.25s ease;
          border-radius: 2px;
        }
        .ap-nav-links a:hover, .ap-nav-links a.active { color: #fff; }
        .ap-nav-links a:hover::after, .ap-nav-links a.active::after { transform: scaleX(1); }
        .ap-nav-links a.active::after { background: #00C4B4; }
        .ap-btn-signin {
          padding: 8px 22px; border-radius: 10px;
          font-size: 13.5px; font-weight: 600;
          background: transparent;
          color: rgba(255,255,255,0.8);
          border: 1.5px solid rgba(255,255,255,0.2);
          cursor: pointer; text-decoration: none;
          font-family: 'Sora', sans-serif;
          transition: all 0.25s;
          letter-spacing: 0.1px;
        }
        .ap-btn-signin:hover {
          border-color: #00C4B4;
          color: #00C4B4;
          background: rgba(0,196,180,0.08);
        }
        .ap-btn-cta {
          padding: 9px 22px; border-radius: 10px;
          font-size: 13.5px; font-weight: 700;
          background: linear-gradient(135deg, #00C4B4, #00E5FF);
          color: #081120; border: none;
          cursor: pointer; text-decoration: none;
          font-family: 'Sora', sans-serif;
          display: inline-flex; align-items: center; gap: 6px;
          transition: all 0.25s;
          letter-spacing: 0.1px;
          box-shadow: 0 4px 16px rgba(0,196,180,0.25);
        }
        .ap-btn-cta:hover {
          transform: translateY(-1px);
          box-shadow: 0 8px 28px rgba(0,196,180,0.4);
        }
        .ap-mobile-menu-btn {
          display: none; background: none; border: none;
          cursor: pointer; padding: 6px;
          color: rgba(255,255,255,0.8);
        }
        .ap-mobile-drawer {
          display: none; position: fixed; top: 68px; left: 0; right: 0; bottom: 0;
          background: rgba(8,17,32,0.98); backdrop-filter: blur(20px);
          z-index: 999; padding: 32px; flex-direction: column; gap: 28px;
          border-top: 1px solid rgba(0,196,180,0.12);
        }
        .ap-mobile-drawer.open { display: flex; }
        .ap-mobile-drawer a {
          color: rgba(255,255,255,0.75); text-decoration: none;
          font-size: 22px; font-weight: 600; letter-spacing: -0.3px;
          transition: color 0.2s;
          font-family: 'Sora', sans-serif;
        }
        .ap-mobile-drawer a:hover { color: #00C4B4; }
        @media (max-width: 768px) {
          .ap-desktop-nav { display: none !important; }
          .ap-mobile-menu-btn { display: flex !important; }
          .ap-nav { padding: 0 20px; }
        }
      `}</style>

            <nav className={`ap-nav ${scrolled ? 'scrolled' : 'top'}`}>
                <a href="/" className="ap-logo">
                    <div className="ap-logo-icon">
                        <svg width="20" height="20" fill="none" stroke="#081120" strokeWidth="2.3" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                    </div>
                    <span className="ap-logo-text">Exam<span>SaaS</span></span>
                </a>

                <ul className="ap-nav-links ap-desktop-nav">
                    {[
                        { label: 'Features', path: '/features' },
                        { label: 'Pricing', path: '/pricing' },
                        { label: 'About', path: '/about' },
                    ].map(({ label, path }) => (
                        <li key={label}>
                            <a href={path} className={currentPath === path ? 'active' : ''}>{label}</a>
                        </li>
                    ))}
                </ul>

                <div style={{ display: 'flex', gap: 10, alignItems: 'center' }} className="ap-desktop-nav">
                    <a href="/login" className="ap-btn-signin">Sign In</a>
                    <a href="/register" className="ap-btn-cta">
                        Get Started
                        <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    </a>
                </div>

                <button className="ap-mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
                    {menuOpen ? (
                        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    ) : (
                        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    )}
                </button>
            </nav>

            <div className={`ap-mobile-drawer ${menuOpen ? 'open' : ''}`}>
                <a href="/features" onClick={() => setMenuOpen(false)}>Features</a>
                <a href="/pricing" onClick={() => setMenuOpen(false)}>Pricing</a>
                <a href="/about" onClick={() => setMenuOpen(false)}>About</a>
                <div style={{ height: 1, background: 'rgba(255,255,255,0.08)' }} />
                <a href="/login" onClick={() => setMenuOpen(false)} style={{ fontSize: 16, color: 'rgba(255,255,255,0.5)' }}>Sign In</a>
                <a href="/register" onClick={() => setMenuOpen(false)} style={{
                    fontSize: 16, color: '#081120',
                    background: 'linear-gradient(135deg,#00C4B4,#00E5FF)',
                    padding: '12px 24px', borderRadius: 12, fontWeight: 700, textAlign: 'center',
                }}>Get Started Free</a>
            </div>
        </>
    );
}