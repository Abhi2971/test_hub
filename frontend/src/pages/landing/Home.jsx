import { useState, useEffect, useRef } from 'react';
import Header from './Header';
import Footer from './Footer';

// ─── Asian Paints T20 World Cup Pre-Match Palette ─────────────────────────────
// Deep Navy #081120 · Vivid Teal #00C4B4 · Electric Cyan #00E5FF
// Coral Burst #FF5733 · Amber Gold #FFB800 · Soft White #F0F6FF
// ─────────────────────────────────────────────────────────────────────────────

const features = [
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    title: 'Secure Exam Environment',
    description: 'AI-powered proctoring, tab-switch detection, and browser lockdown ensure exam integrity at every step.',
    accent: '#00C4B4',
  },
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    title: 'Instant Results',
    description: 'Automatic grading and real-time score calculation provide immediate, actionable feedback to students.',
    accent: '#FF5733',
  },
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Deep Analytics',
    description: 'Institutional-level reporting with AI-powered insights into student performance trends and outcomes.',
    accent: '#FFB800',
  },
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    title: 'Smart Question Bank',
    description: 'AI-generated questions from any PDF. Organize by subject, topic, and difficulty level automatically.',
    accent: '#00E5FF',
  },
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    title: 'Flexible Scheduling',
    description: 'Schedule in advance, set custom time windows, and manage multiple concurrent exam sessions effortlessly.',
    accent: '#00C4B4',
  },
  {
    icon: (
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="22" height="22">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.6} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
    title: 'Multi-tenant Platform',
    description: 'Support unlimited institutions and organizations from a single, unified, role-based dashboard.',
    accent: '#FF5733',
  },
];

const steps = [
  { number: '01', title: 'Create Account', description: 'Sign up in seconds. Set your role as student, teacher, or admin.', color: '#00C4B4' },
  { number: '02', title: 'Build Your Exam', description: 'Create questions, configure AI proctoring and schedule the exam.', color: '#FFB800' },
  { number: '03', title: 'Invite Students', description: 'Share exam links or import your entire student roster via CSV.', color: '#FF5733' },
  { number: '04', title: 'Monitor & Analyze', description: 'Watch live attempts and gain deep insights from analytics.', color: '#00E5FF' },
];

const testimonials = [
  {
    name: 'Dr. Priya Sharma',
    role: 'Director of Examinations, Delhi University',
    avatar: 'PS',
    content: 'ExamSaaS transformed our online examination process. The AI proctoring gave us complete confidence in result integrity.',
    color: '#00C4B4',
  },
  {
    name: 'Prof. Rajesh Kumar',
    role: 'Head of CS Department, IIT Roorkee',
    avatar: 'RK',
    content: 'The question bank and analytics are exceptional. We now identify student weaknesses and adapt teaching in real time.',
    color: '#FFB800',
  },
  {
    name: 'Anita Desai',
    role: 'Principal, Sunrise Public School',
    avatar: 'AD',
    content: 'Setting up exams used to take days. With ExamSaaS we launch a full exam in under an hour. Truly a game changer.',
    color: '#FF5733',
  },
];

function Counter({ target }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const started = useRef(false);
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true;
        const num = parseInt(target.replace(/\D/g, ''));
        let current = 0;
        const step = Math.ceil(num / 60);
        const timer = setInterval(() => {
          current = Math.min(current + step, num);
          setCount(current);
          if (current >= num) clearInterval(timer);
        }, 22);
      }
    });
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [target]);
  const hasPlus = target.includes('+');
  const hasPct = target.includes('%');
  const hasM = target.includes('M');
  const display = hasM
    ? (count >= 1000 ? (count / 1000).toFixed(0) + 'M' : count + 'k') + (hasPlus ? '+' : '')
    : count + (hasPlus ? '+' : '') + (hasPct ? '%' : '');
  return <span ref={ref}>{display}</span>;
}

export default function Home() {
  const [activeStep, setActiveStep] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setActiveStep(s => (s + 1) % 4), 2800);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={{ fontFamily: "'Sora', 'DM Sans', sans-serif", background: '#081120', minHeight: '100vh', color: '#fff' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        @keyframes shimmer { 0%{background-position:-200% center} 100%{background-position:200% center} }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(24px)} to{opacity:1;transform:translateY(0)} }
        @keyframes pulse-glow { 0%,100%{box-shadow:0 0 0 0 rgba(0,196,180,0.4)} 50%{box-shadow:0 0 0 8px rgba(0,196,180,0)} }
        @keyframes scan { 0%{transform:translateY(-100%)} 100%{transform:translateY(100vh)} }

        .shimmer-text {
          background: linear-gradient(90deg, #00C4B4, #00E5FF, #FFB800, #FF5733, #00C4B4);
          background-size: 300% auto;
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          animation: shimmer 5s linear infinite;
        }
        .orb { position: absolute; border-radius: 50%; filter: blur(90px); pointer-events: none; }
        .sdivider { height: 1px; background: linear-gradient(90deg,transparent,rgba(0,196,180,0.25),rgba(255,184,0,0.2),transparent); }
        .fcard {
          background: rgba(255,255,255,0.035);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 20px; padding: 28px;
          transition: all 0.3s; position: relative; overflow: hidden;
        }
        .fcard::before {
          content:''; position:absolute; top:0;left:0;right:0;height:2px;
          background:var(--ac,#00C4B4); transform:scaleX(0); transition:transform 0.3s;
        }
        .fcard:hover::before { transform:scaleX(1); }
        .fcard:hover { background:rgba(255,255,255,0.06); transform:translateY(-5px); border-color:rgba(255,255,255,0.12); }
        .tcard { background:rgba(255,255,255,0.035); border:1px solid rgba(255,255,255,0.07); border-radius:20px; padding:28px; transition:all 0.3s; }
        .tcard:hover { transform:translateY(-5px); background:rgba(255,255,255,0.06); }
        .stat-c { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07); border-radius:18px; padding:30px 20px; text-align:center; transition:all 0.3s; }
        .stat-c:hover { background:rgba(0,196,180,0.08); border-color:rgba(0,196,180,0.25); }
        .btn-p { background:linear-gradient(135deg,#00C4B4,#00E5FF); color:#081120; font-weight:700; border:none; cursor:pointer; transition:all 0.3s; text-decoration:none; display:inline-flex; align-items:center; gap:8px; font-family:inherit; }
        .btn-p:hover { transform:translateY(-2px); box-shadow:0 12px 40px rgba(0,196,180,0.45); }
        .btn-o { background:transparent; color:#fff; font-weight:600; border:1.5px solid rgba(255,255,255,0.2); cursor:pointer; transition:all 0.3s; text-decoration:none; display:inline-flex; align-items:center; gap:8px; font-family:inherit; }
        .btn-o:hover { border-color:#00C4B4; background:rgba(0,196,180,0.09); color:#00C4B4; }
        .badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
        .badge-teal { background:rgba(0,196,180,0.12); color:#00C4B4; border:1px solid rgba(0,196,180,0.25); }
        .badge-gold { background:rgba(255,184,0,0.12); color:#FFB800; border:1px solid rgba(255,184,0,0.25); }
        .badge-coral { background:rgba(255,87,51,0.12); color:#FF5733; border:1px solid rgba(255,87,51,0.25); }
        .badge-cyan { background:rgba(0,229,255,0.12); color:#00E5FF; border:1px solid rgba(0,229,255,0.25); }
        .grid-bg {
          position:absolute;inset:0;opacity:0.035;
          background-image:linear-gradient(rgba(0,196,180,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,196,180,1) 1px,transparent 1px);
          background-size:56px 56px;
          mask-image:radial-gradient(ellipse at center,black 20%,transparent 75%);
        }
        @media(max-width:768px) {
          .hero-ctas { flex-direction:column !important; align-items:center; }
          .steps-grid { grid-template-columns:1fr 1fr !important; }
        }
      `}</style>

      <Header />

      {/* ─── HERO ─── */}
      <section style={{ position: 'relative', overflow: 'hidden', paddingTop: '130px', paddingBottom: '100px', minHeight: '100vh', display: 'flex', alignItems: 'center' }}>
        <div className="orb" style={{ width: 700, height: 500, top: -180, right: -120, background: 'radial-gradient(circle,rgba(0,196,180,0.16) 0%,transparent 70%)' }} />
        <div className="orb" style={{ width: 550, height: 450, bottom: -150, left: -120, background: 'radial-gradient(circle,rgba(255,87,51,0.12) 0%,transparent 70%)' }} />
        <div className="orb" style={{ width: 400, height: 400, top: '45%', left: '42%', background: 'radial-gradient(circle,rgba(255,184,0,0.07) 0%,transparent 70%)' }} />
        <div className="grid-bg" />

        {/* Pre-match scan line effect */}
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg,transparent,rgba(0,196,180,0.6),transparent)', animation: 'scan 6s linear infinite', opacity: 0.4, zIndex: 1 }} />

        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', width: '100%', position: 'relative', zIndex: 2 }}>
          <div style={{ textAlign: 'center', maxWidth: 860, margin: '0 auto' }}>

            {/* Live badge */}
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '5px 14px', borderRadius: 100, background: 'rgba(0,196,180,0.1)', border: '1px solid rgba(0,196,180,0.28)', marginBottom: 28 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#00C4B4', display: 'inline-block', animation: 'pulse-glow 2s ease-out infinite' }} />
              <span style={{ color: '#00C4B4', fontSize: 12.5, fontWeight: 600, letterSpacing: 0.2 }}>Now serving 500+ institutions across India</span>
            </div>

            <h1 style={{ fontSize: 'clamp(40px,7vw,80px)', fontWeight: 900, lineHeight: 1.06, letterSpacing: '-2.5px', marginBottom: 24, color: '#F0F6FF' }}>
              The Modern Exam<br />
              <span className="shimmer-text">Platform for India</span>
            </h1>

            <p style={{ fontSize: 'clamp(15px,2vw,19px)', color: 'rgba(240,246,255,0.58)', lineHeight: 1.75, maxWidth: 580, margin: '0 auto 44px' }}>
              Conduct secure, scalable online examinations with AI-powered proctoring,
              instant results, and deep analytics — trusted by universities, colleges & schools.
            </p>

            <div className="hero-ctas" style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 72 }}>
              <a href="/register" className="btn-p" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>
                Start Free Trial
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
              </a>
              <a href="/about" className="btn-o" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>Learn More</a>
            </div>

            {/* Dashboard preview */}
            <div style={{ background: 'linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02))', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 26, padding: 3, boxShadow: '0 40px 100px rgba(0,0,0,0.7), 0 0 0 1px rgba(0,196,180,0.08)' }}>
              <div style={{ background: 'rgba(12,24,44,0.98)', borderRadius: '22px 22px 0 0', padding: '11px 16px', display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ display: 'flex', gap: 6 }}>
                  {['#FF5F57', '#FEBC2E', '#28C840'].map(c => <div key={c} style={{ width: 11, height: 11, borderRadius: '50%', background: c }} />)}
                </div>
                <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 7, padding: '4px 12px', color: 'rgba(255,255,255,0.3)', fontSize: 11.5, textAlign: 'center' }}>examsaas.com/dashboard</div>
              </div>
              <div style={{ background: '#0C1830', borderRadius: '0 0 22px 22px', padding: 20 }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 14 }}>
                  {[{ label: 'Active Exams', value: '24', color: '#00C4B4' }, { label: 'Students', value: '1,847', color: '#FFB800' }, { label: 'Avg Score', value: '78%', color: '#FF5733' }].map(s => (
                    <div key={s.label} style={{ background: 'rgba(255,255,255,0.04)', border: `1px solid ${s.color}28`, borderRadius: 12, padding: '13px 14px' }}>
                      <div style={{ color: s.color, fontSize: 22, fontWeight: 800 }}>{s.value}</div>
                      <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 11, marginTop: 2 }}>{s.label}</div>
                    </div>
                  ))}
                </div>
                <div style={{ background: 'rgba(255,255,255,0.025)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 12, padding: '13px 15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 11 }}>
                    <span style={{ color: 'rgba(255,255,255,0.65)', fontSize: 11.5, fontWeight: 600 }}>Recent Exams</span>
                    <span style={{ color: '#00C4B4', fontSize: 11 }}>View all →</span>
                  </div>
                  {[{ exam: 'Data Structures Midterm', score: '92%', dot: '#00C4B4' }, { exam: 'Mathematics Quiz', score: '85%', dot: '#FFB800' }, { exam: 'Physics Final', score: '71%', dot: '#FF5733' }].map((item, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '7px 0', borderBottom: i < 2 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div style={{ width: 5, height: 5, borderRadius: '50%', background: item.dot }} />
                        <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: 12 }}>{item.exam}</span>
                      </div>
                      <span style={{ color: item.dot, fontSize: 12, fontWeight: 700 }}>{item.score}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── STATS ─── */}
      <section style={{ padding: '80px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: 16 }}>
          {[
            { value: '500+', label: 'Institutions', color: '#00C4B4' },
            { value: '2000+', label: 'Exams Conducted (000s)', color: '#FFB800' },
            { value: '99%', label: 'Uptime SLA', color: '#FF5733' },
            { value: '10000+', label: 'Students Served (000s)', color: '#00E5FF' },
          ].map(stat => (
            <div key={stat.label} className="stat-c">
              <div style={{ fontSize: 44, fontWeight: 900, color: stat.color, letterSpacing: '-1px', lineHeight: 1 }}>
                <Counter target={stat.value} />
              </div>
              <div style={{ color: 'rgba(240,246,255,0.45)', fontSize: 12.5, marginTop: 6, fontWeight: 500 }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── FEATURES ─── */}
      <section style={{ padding: '100px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 60 }}>
          <span className="badge badge-teal" style={{ marginBottom: 16 }}>Features</span>
          <h2 style={{ fontSize: 'clamp(28px,4vw,50px)', fontWeight: 800, letterSpacing: '-1px', lineHeight: 1.1, marginBottom: 14 }}>
            Everything You Need for<br /><span style={{ color: '#00C4B4' }}>Modern Examinations</span>
          </h2>
          <p style={{ color: 'rgba(240,246,255,0.5)', fontSize: 17, maxWidth: 500, margin: '0 auto', lineHeight: 1.7 }}>From secure proctoring to instant results — a complete examination ecosystem.</p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 20 }}>
          {features.map(f => (
            <div key={f.title} className="fcard" style={{ '--ac': f.accent }}>
              <div style={{ width: 46, height: 46, borderRadius: 13, background: `${f.accent}18`, border: `1px solid ${f.accent}38`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: f.accent, marginBottom: 18 }}>{f.icon}</div>
              <h3 style={{ fontSize: 16.5, fontWeight: 700, marginBottom: 8, color: '#F0F6FF' }}>{f.title}</h3>
              <p style={{ color: 'rgba(240,246,255,0.5)', fontSize: 14, lineHeight: 1.7 }}>{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── HOW IT WORKS ─── */}
      <section style={{ padding: '100px 24px', background: 'rgba(255,255,255,0.015)' }}>
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 60 }}>
            <span className="badge badge-gold" style={{ marginBottom: 16 }}>How It Works</span>
            <h2 style={{ fontSize: 'clamp(28px,4vw,50px)', fontWeight: 800, letterSpacing: '-1px' }}>
              Launch Your First Exam<br /><span style={{ color: '#FFB800' }}>in Minutes</span>
            </h2>
          </div>
          <div className="steps-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 18, marginBottom: 36 }}>
            {steps.map((step, i) => (
              <div key={step.number} onClick={() => setActiveStep(i)} style={{ background: activeStep === i ? `${step.color}14` : 'rgba(255,255,255,0.03)', border: `1px solid ${activeStep === i ? step.color + '48' : 'rgba(255,255,255,0.07)'}`, borderRadius: 20, padding: '24px 18px', cursor: 'pointer', transition: 'all 0.3s', transform: activeStep === i ? 'translateY(-5px)' : 'none', boxShadow: activeStep === i ? `0 12px 40px ${step.color}22` : 'none' }}>
                <div style={{ fontSize: 38, fontWeight: 900, color: activeStep === i ? step.color : 'rgba(255,255,255,0.09)', marginBottom: 10, lineHeight: 1 }}>{step.number}</div>
                <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 7, color: '#F0F6FF' }}>{step.title}</h3>
                <p style={{ color: 'rgba(240,246,255,0.45)', fontSize: 12.5, lineHeight: 1.65 }}>{step.description}</p>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
            {steps.map((step, i) => (
              <button key={i} onClick={() => setActiveStep(i)} style={{ border: 'none', cursor: 'pointer', height: 8, borderRadius: 4, transition: 'all 0.3s', width: activeStep === i ? 28 : 8, background: activeStep === i ? step.color : 'rgba(255,255,255,0.18)' }} />
            ))}
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── TESTIMONIALS ─── */}
      <section style={{ padding: '100px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 56 }}>
          <span className="badge badge-coral" style={{ marginBottom: 16 }}>Testimonials</span>
          <h2 style={{ fontSize: 'clamp(28px,4vw,50px)', fontWeight: 800, letterSpacing: '-1px' }}>
            Trusted by Educators<br /><span style={{ color: '#FF5733' }}>Across India</span>
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 20 }}>
          {testimonials.map(t => (
            <div key={t.name} className="tcard">
              <div style={{ display: 'flex', gap: 3, marginBottom: 16 }}>
                {[...Array(5)].map((_, i) => (
                  <svg key={i} width="15" height="15" fill="#FFB800" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                ))}
              </div>
              <p style={{ color: 'rgba(240,246,255,0.68)', fontSize: 14.5, lineHeight: 1.78, marginBottom: 24, fontStyle: 'italic' }}>"{t.content}"</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 42, height: 42, borderRadius: 12, background: `linear-gradient(135deg,${t.color},${t.color}80)`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#081120', fontWeight: 800, fontSize: 13 }}>{t.avatar}</div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, color: '#F0F6FF' }}>{t.name}</div>
                  <div style={{ color: 'rgba(240,246,255,0.38)', fontSize: 12, marginTop: 2 }}>{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── CTA ─── */}
      <section style={{ padding: '100px 24px', position: 'relative', overflow: 'hidden' }}>
        <div className="orb" style={{ width: 600, height: 400, top: '50%', left: '50%', transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle,rgba(0,196,180,0.1) 0%,transparent 70%)' }} />
        <div style={{ maxWidth: 720, margin: '0 auto', textAlign: 'center', position: 'relative' }}>
          <span className="badge badge-cyan" style={{ marginBottom: 20 }}>Get Started Today</span>
          <h2 style={{ fontSize: 'clamp(30px,5vw,58px)', fontWeight: 900, letterSpacing: '-1.5px', lineHeight: 1.08, marginBottom: 20 }}>
            Ready to Transform<br /><span className="shimmer-text">Your Examinations?</span>
          </h2>
          <p style={{ color: 'rgba(240,246,255,0.55)', fontSize: 17, lineHeight: 1.7, maxWidth: 460, margin: '0 auto 40px' }}>Join 500+ educational institutions that trust ExamSaaS. Start free — no credit card required.</p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 44 }}>
            <a href="/register" className="btn-p" style={{ padding: '15px 36px', borderRadius: 14, fontSize: 16 }}>
              Get Started Free
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            </a>
            <a href="/about" className="btn-o" style={{ padding: '15px 36px', borderRadius: 14, fontSize: 16 }}>Learn More</a>
          </div>
          <div style={{ display: 'flex', gap: 28, justifyContent: 'center', flexWrap: 'wrap' }}>
            {['No credit card', '14-day free trial', '99.9% uptime', '24/7 support'].map(item => (
              <div key={item} style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'rgba(240,246,255,0.38)', fontSize: 12.5 }}>
                <svg width="13" height="13" fill="none" stroke="#00C4B4" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}