import Header from './Header';
import Footer from './Footer';

// ─── Asian Paints T20 World Cup Pre-Match Palette ─────────────────────────────
// Deep Navy #081120 · Vivid Teal #00C4B4 · Electric Cyan #00E5FF
// Coral Burst #FF5733 · Amber Gold #FFB800 · Soft White #F0F6FF
// ─────────────────────────────────────────────────────────────────────────────

const featureGroups = [
  {
    category: 'Examination',
    accent: '#00C4B4',
    badge: 'badge-teal',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
    ),
    features: [
      { title: 'Multiple Question Types', description: 'MCQ, multiple select, true/false, fill in blank, and descriptive with auto/manual grading.' },
      { title: 'Randomized Question Pools', description: 'Pull from your bank randomly, shuffle options, and ensure every student gets a unique paper.' },
      { title: 'Flexible Time Windows', description: 'Set start/end times, grace periods, and auto-submit across all time zones.' },
      { title: 'Secure Exam Mode', description: 'Browser lockdown, fullscreen enforcement, copy-paste disable, and tab-switch monitoring.' },
    ],
  },
  {
    category: 'AI & Automation',
    accent: '#FFB800',
    badge: 'badge-gold',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    features: [
      { title: 'AI Question Generation', description: 'Import a PDF or describe a topic — AI generates high-quality MCQs instantly.' },
      { title: 'AI Proctoring', description: 'Face verification, face matching, and anomaly detection during live exams.' },
      { title: 'Smart Analytics', description: 'AI-powered insights into question difficulty and personalized performance recommendations.' },
      { title: 'Auto-Grading', description: 'Instant scoring for objective questions. Descriptive answers graded manually or with AI.' },
    ],
  },
  {
    category: 'Management',
    accent: '#FF5733',
    badge: 'badge-coral',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    features: [
      { title: 'Role-Based Access', description: 'Super admins, institute admins, teachers, and students — each with tailored dashboards.' },
      { title: 'Bulk Student Import', description: 'Upload CSV files or integrate with your student information system in minutes.' },
      { title: 'Certificate Generation', description: 'Automatically generate and send branded PDF certificates to students who pass.' },
      { title: 'Payment & Wallet', description: 'Built-in wallet system with Razorpay integration for exam purchases and top-ups.' },
    ],
  },
  {
    category: 'Integration',
    accent: '#00E5FF',
    badge: 'badge-cyan',
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    features: [
      { title: 'Cloud Storage', description: 'All uploaded files stored securely on Cloudinary — images, answer sheets, certificates.' },
      { title: 'REST API', description: 'Comprehensive API for integrating with your LMS, SIS, or custom applications.' },
      { title: 'Webhooks', description: 'Real-time event notifications for exam completion, payments, and certificate generation.' },
      { title: 'SSO & SAML', description: 'Enterprise SSO with SAML 2.0 integration for seamless institutional authentication.' },
    ],
  },
];

const stack = [
  { name: 'MongoDB Atlas', desc: 'Database', color: '#00C4B4' },
  { name: 'Cloudinary', desc: 'File Storage', color: '#FFB800' },
  { name: 'Razorpay', desc: 'Payments', color: '#FF5733' },
  { name: 'Redis', desc: 'Caching', color: '#00E5FF' },
];

export default function Features() {
  return (
    <div style={{ fontFamily: "'Sora','DM Sans',sans-serif", background: '#081120', minHeight: '100vh', color: '#F0F6FF' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        @keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
        @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        .shimmer-text{background:linear-gradient(90deg,#00C4B4,#00E5FF,#FFB800,#FF5733,#00C4B4);background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 5s linear infinite;}
        .orb{position:absolute;border-radius:50%;filter:blur(90px);pointer-events:none;}
        .sdivider{height:1px;background:linear-gradient(90deg,transparent,rgba(0,196,180,0.22),rgba(255,184,0,0.18),transparent);}
        .fcard{background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:26px;transition:all 0.3s;position:relative;overflow:hidden;}
        .fcard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac,#00C4B4);transform:scaleX(0);transition:transform 0.3s;}
        .fcard:hover::before{transform:scaleX(1);}
        .fcard:hover{background:rgba(255,255,255,0.06);transform:translateY(-5px);border-color:rgba(255,255,255,0.12);}
        .badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
        .badge-teal{background:rgba(0,196,180,0.12);color:#00C4B4;border:1px solid rgba(0,196,180,0.25);}
        .badge-gold{background:rgba(255,184,0,0.12);color:#FFB800;border:1px solid rgba(255,184,0,0.25);}
        .badge-coral{background:rgba(255,87,51,0.12);color:#FF5733;border:1px solid rgba(255,87,51,0.25);}
        .badge-cyan{background:rgba(0,229,255,0.12);color:#00E5FF;border:1px solid rgba(0,229,255,0.25);}
        .btn-p{background:linear-gradient(135deg,#00C4B4,#00E5FF);color:#081120;font-weight:700;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
        .btn-p:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(0,196,180,0.45);}
        .grid-bg{position:absolute;inset:0;opacity:0.03;background-image:linear-gradient(rgba(0,196,180,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,196,180,1) 1px,transparent 1px);background-size:56px 56px;mask-image:radial-gradient(ellipse at center,black 20%,transparent 75%);}
        .stack-card{border-radius:16px;padding:26px 18px;text-align:center;transition:all 0.3s;}
        .stack-card:hover{transform:translateY(-4px);}
      `}</style>

      <Header />

      {/* ─── HERO ─── */}
      <section style={{ position: 'relative', overflow: 'hidden', padding: '140px 24px 100px', textAlign: 'center' }}>
        <div className="orb" style={{ width: 700, height: 450, top: -150, right: -100, background: 'radial-gradient(circle,rgba(0,196,180,0.14) 0%,transparent 70%)' }} />
        <div className="orb" style={{ width: 500, height: 400, bottom: -100, left: -100, background: 'radial-gradient(circle,rgba(255,184,0,0.09) 0%,transparent 70%)' }} />
        <div className="grid-bg" />
        <div style={{ maxWidth: 760, margin: '0 auto', position: 'relative' }}>
          <span className="badge badge-teal" style={{ marginBottom: 20 }}>Features</span>
          <h1 style={{ fontSize: 'clamp(36px,6.5vw,72px)', fontWeight: 900, letterSpacing: '-2px', lineHeight: 1.07, marginBottom: 22 }}>
            Built for <span style={{ color: '#00C4B4' }}>Modern</span><br />Education
          </h1>
          <p style={{ color: 'rgba(240,246,255,0.55)', fontSize: 18, lineHeight: 1.75, maxWidth: 540, margin: '0 auto' }}>
            Every feature designed with educators and students in mind — from simple quizzes to high-stakes proctored examinations.
          </p>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── FEATURE GROUPS ─── */}
      {featureGroups.map((group, gi) => (
        <section key={group.category} style={{ padding: '88px 24px', background: gi % 2 === 1 ? 'rgba(255,255,255,0.018)' : 'transparent' }}>
          <div style={{ maxWidth: 1160, margin: '0 auto' }}>
            {/* Group header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 38 }}>
              <div style={{ width: 46, height: 46, borderRadius: 13, background: `${group.accent}18`, border: `1px solid ${group.accent}35`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: group.accent, flexShrink: 0 }}>
                {group.icon}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1 }}>
                <h2 style={{ fontSize: 28, fontWeight: 800, color: '#F0F6FF', letterSpacing: '-0.5px', whiteSpace: 'nowrap' }}>{group.category}</h2>
                <div style={{ flex: 1, height: 1, background: `linear-gradient(90deg,${group.accent}35,transparent)` }} />
              </div>
              <span className={`badge ${group.badge}`}>{group.features.length} Features</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 18 }}>
              {group.features.map(f => (
                <div key={f.title} className="fcard" style={{ '--ac': group.accent }}>
                  <div style={{ width: 34, height: 34, borderRadius: 10, background: `${group.accent}18`, border: `1px solid ${group.accent}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: group.accent, boxShadow: `0 0 10px ${group.accent}80` }} />
                  </div>
                  <h3 style={{ fontSize: 15.5, fontWeight: 700, marginBottom: 9, color: '#F0F6FF' }}>{f.title}</h3>
                  <p style={{ color: 'rgba(240,246,255,0.5)', fontSize: 13.5, lineHeight: 1.7 }}>{f.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      ))}

      <div className="sdivider" />

      {/* ─── TECH STACK ─── */}
      <section style={{ padding: '88px 24px' }}>
        <div style={{ maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
          <span className="badge badge-cyan" style={{ marginBottom: 18 }}>Infrastructure</span>
          <h2 style={{ fontSize: 'clamp(26px,4vw,44px)', fontWeight: 800, marginBottom: 12, letterSpacing: '-0.5px' }}>
            Built With <span className="shimmer-text">Best-in-Class</span>
          </h2>
          <p style={{ color: 'rgba(240,246,255,0.48)', marginBottom: 48, fontSize: 16, lineHeight: 1.7 }}>Powered by enterprise-grade infrastructure for reliability, security, and performance at scale.</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 16 }}>
            {stack.map(item => (
              <div key={item.name} className="stack-card" style={{ background: `${item.color}0E`, border: `1px solid ${item.color}28` }}>
                <div style={{ width: 40, height: 40, borderRadius: 12, background: `${item.color}20`, border: `1px solid ${item.color}35`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px' }}>
                  <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color, boxShadow: `0 0 12px ${item.color}90` }} />
                </div>
                <div style={{ fontWeight: 700, fontSize: 15, color: '#F0F6FF' }}>{item.name}</div>
                <div style={{ color: 'rgba(240,246,255,0.4)', fontSize: 12, marginTop: 4 }}>{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section style={{ padding: '88px 24px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div className="orb" style={{ width: 600, height: 350, top: '50%', left: '50%', transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle,rgba(0,196,180,0.1) 0%,transparent 70%)' }} />
        <div style={{ position: 'relative' }}>
          <h2 style={{ fontSize: 'clamp(28px,4vw,48px)', fontWeight: 900, letterSpacing: '-1px', marginBottom: 14 }}>Ready to Experience It?</h2>
          <p style={{ color: 'rgba(240,246,255,0.55)', marginBottom: 34, fontSize: 17, lineHeight: 1.7 }}>Start your free trial today. No credit card required.</p>
          <a href="/register" className="btn-p" style={{ padding: '14px 36px', borderRadius: 14, fontSize: 16 }}>
            Get Started Free
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
          </a>
        </div>
      </section>

      <Footer />
    </div>
  );
}