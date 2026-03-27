export default function Footer() {
    const year = new Date().getFullYear();

    const links = {
        Product: ['Features', 'Pricing', 'Security', 'Changelog'],
        Company: ['About', 'Blog', 'Careers', 'Press'],
        Support: ['Documentation', 'Help Center', 'Contact', 'Status'],
        Legal: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'GDPR'],
    };

    return (
        <>
            <style>{`
        .ap-footer {
          font-family: 'Sora', 'DM Sans', sans-serif;
          background: #060E1C;
          border-top: 1px solid rgba(0,196,180,0.1);
          padding: 72px 32px 32px;
          position: relative;
          overflow: hidden;
        }
        .ap-footer::before {
          content: '';
          position: absolute; top: 0; left: 50%; transform: translateX(-50%);
          width: 600px; height: 1px;
          background: linear-gradient(90deg, transparent, #00C4B4, #FFB800, #FF5733, #00E5FF, transparent);
        }
        .ap-footer-glow {
          position: absolute; top: -120px; left: 50%; transform: translateX(-50%);
          width: 800px; height: 300px; border-radius: 50%;
          background: radial-gradient(ellipse, rgba(0,196,180,0.05) 0%, transparent 70%);
          pointer-events: none;
        }
        .ap-footer-inner {
          max-width: 1200px; margin: 0 auto; position: relative;
        }
        .ap-footer-top {
          display: grid;
          grid-template-columns: 1.6fr repeat(4, 1fr);
          gap: 40px;
          margin-bottom: 56px;
        }
        .ap-footer-brand {}
        .ap-footer-logo {
          display: flex; align-items: center; gap: 10px;
          text-decoration: none; margin-bottom: 16px;
        }
        .ap-footer-logo-icon {
          width: 36px; height: 36px; border-radius: 10px;
          background: linear-gradient(135deg, #00C4B4, #00E5FF);
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 0 16px rgba(0,196,180,0.3);
        }
        .ap-footer-logo-text {
          font-size: 17px; font-weight: 800; color: #fff; letter-spacing: -0.3px;
        }
        .ap-footer-logo-text span { color: #00C4B4; }
        .ap-footer-tagline {
          color: rgba(255,255,255,0.45);
          font-size: 13.5px; line-height: 1.75;
          max-width: 240px; margin-bottom: 24px;
        }
        .ap-footer-socials {
          display: flex; gap: 10px;
        }
        .ap-social-btn {
          width: 36px; height: 36px; border-radius: 9px;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.09);
          display: flex; align-items: center; justify-content: center;
          color: rgba(255,255,255,0.5);
          cursor: pointer; transition: all 0.25s;
          text-decoration: none;
        }
        .ap-social-btn:hover {
          background: rgba(0,196,180,0.12);
          border-color: rgba(0,196,180,0.3);
          color: #00C4B4;
          transform: translateY(-2px);
        }
        .ap-footer-col h4 {
          color: rgba(255,255,255,0.9);
          font-size: 13px; font-weight: 700;
          letter-spacing: 0.6px; text-transform: uppercase;
          margin-bottom: 18px;
        }
        .ap-footer-col ul {
          list-style: none; margin: 0; padding: 0;
          display: flex; flex-direction: column; gap: 10px;
        }
        .ap-footer-col ul li a {
          color: rgba(255,255,255,0.42);
          text-decoration: none; font-size: 13.5px;
          transition: color 0.2s;
          display: block;
        }
        .ap-footer-col ul li a:hover { color: #00C4B4; }
        .ap-footer-divider {
          height: 1px;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
          margin-bottom: 28px;
        }
        .ap-footer-bottom {
          display: flex; justify-content: space-between; align-items: center;
          flex-wrap: wrap; gap: 16px;
        }
        .ap-footer-copy {
          color: rgba(255,255,255,0.3); font-size: 12.5px;
        }
        .ap-footer-badges {
          display: flex; gap: 10px; align-items: center;
          flex-wrap: wrap;
        }
        .ap-badge {
          padding: 4px 12px; border-radius: 20px;
          font-size: 11px; font-weight: 700; letter-spacing: 0.3px;
          border: 1px solid;
        }
        .ap-badge-teal { color: #00C4B4; border-color: rgba(0,196,180,0.25); background: rgba(0,196,180,0.07); }
        .ap-badge-gold { color: #FFB800; border-color: rgba(255,184,0,0.25); background: rgba(255,184,0,0.07); }
        .ap-badge-coral { color: #FF5733; border-color: rgba(255,87,51,0.25); background: rgba(255,87,51,0.07); }
        @media (max-width: 900px) {
          .ap-footer-top { grid-template-columns: 1fr 1fr; gap: 32px; }
        }
        @media (max-width: 540px) {
          .ap-footer-top { grid-template-columns: 1fr; }
          .ap-footer { padding: 56px 20px 28px; }
        }
      `}</style>

            <footer className="ap-footer">
                <div className="ap-footer-glow" />
                <div className="ap-footer-inner">
                    <div className="ap-footer-top">
                        {/* Brand */}
                        <div className="ap-footer-brand">
                            <a href="/" className="ap-footer-logo">
                                <div className="ap-footer-logo-icon">
                                    <svg width="18" height="18" fill="none" stroke="#081120" strokeWidth="2.3" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                    </svg>
                                </div>
                                <span className="ap-footer-logo-text">Exam<span>SaaS</span></span>
                            </a>
                            <p className="ap-footer-tagline">
                                India's most trusted examination platform for universities, colleges, and schools.
                            </p>
                            <div className="ap-footer-socials">
                                {/* Twitter */}
                                <a href="#" className="ap-social-btn" aria-label="Twitter">
                                    <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                                    </svg>
                                </a>
                                {/* LinkedIn */}
                                <a href="#" className="ap-social-btn" aria-label="LinkedIn">
                                    <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                                    </svg>
                                </a>
                                {/* YouTube */}
                                <a href="#" className="ap-social-btn" aria-label="YouTube">
                                    <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                                    </svg>
                                </a>
                            </div>
                        </div>

                        {/* Links */}
                        {Object.entries(links).map(([category, items]) => (
                            <div key={category} className="ap-footer-col">
                                <h4>{category}</h4>
                                <ul>
                                    {items.map(item => (
                                        <li key={item}><a href="#">{item}</a></li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>

                    <div className="ap-footer-divider" />

                    <div className="ap-footer-bottom">
                        <p className="ap-footer-copy">
                            © {year} ExamSaaS Technologies Pvt. Ltd. All rights reserved. Made with ❤️ in India.
                        </p>
                        <div className="ap-footer-badges">
                            <span className="ap-badge ap-badge-teal">GDPR Compliant</span>
                            <span className="ap-badge ap-badge-gold">ISO 27001</span>
                            <span className="ap-badge ap-badge-coral">99.9% Uptime</span>
                        </div>
                    </div>
                </div>
            </footer>
        </>
    );
}