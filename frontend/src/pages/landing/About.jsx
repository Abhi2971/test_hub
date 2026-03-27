import Header from './Header';
import Footer from './Footer';

// ─── Asian Paints T20 World Cup Pre-Match Palette ─────────────────────────────
// Deep Navy #081120 · Vivid Teal #00C4B4 · Electric Cyan #00E5FF
// Coral Burst #FF5733 · Amber Gold #FFB800 · Soft White #F0F6FF
// ─────────────────────────────────────────────────────────────────────────────

const team = [
  { name: 'Vikram Singh', role: 'Founder & CEO', avatar: 'VS', bio: 'Former IIT professor with 15 years in educational technology.', color: '#00C4B4' },
  { name: 'Neha Gupta', role: 'CTO', avatar: 'NG', bio: 'Built exam systems serving 5M+ students at previous venture.', color: '#FFB800' },
  { name: 'Arjun Mehta', role: 'Head of Product', avatar: 'AM', bio: 'Product leader with deep expertise in edtech and user experience.', color: '#FF5733' },
  { name: 'Sneha Reddy', role: 'Head of Engineering', avatar: 'SR', bio: 'Distributed systems expert passionate about scalable architecture.', color: '#00E5FF' },
];

const values = [
  { title: 'Integrity First', description: 'We build technology that maintains the highest standards of examination integrity. Our AI proctoring is fair, accurate, and transparent.', color: '#00C4B4', icon: '🛡️' },
  { title: 'Accessible Everywhere', description: 'Education should have no barriers. Our platform works on any device, in any location, regardless of technical constraints.', color: '#FFB800', icon: '🌏' },
  { title: 'Speed & Reliability', description: '99.9% uptime and sub-second response times. Your exams never face technical delays when it matters most.', color: '#FF5733', icon: '⚡' },
  { title: 'Privacy & Security', description: 'Student data privacy is paramount. GDPR compliant, end-to-end encryption, never compromising on data protection.', color: '#00E5FF', icon: '🔒' },
];

const milestones = [
  { year: '2022', label: 'Founded', detail: 'Dr. Vikram Singh builds the first version in 3 months', color: '#00C4B4' },
  { year: '2022', label: 'First 12 Institutions', detail: '50,000+ examinations across Delhi in year one', color: '#FFB800' },
  { year: '2023', label: '100+ Institutions', detail: 'Expanded to colleges and universities nationwide', color: '#FF5733' },
  { year: '2024', label: '500+ Institutions', detail: 'Processing millions of examinations annually', color: '#00E5FF' },
];

export default function About() {
  return (
    <div style={{ fontFamily: "'Sora','DM Sans',sans-serif", background: '#081120', minHeight: '100vh', color: '#F0F6FF' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        @keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
        .shimmer-text{background:linear-gradient(90deg,#00C4B4,#00E5FF,#FFB800,#FF5733,#00C4B4);background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 5s linear infinite;}
        .orb{position:absolute;border-radius:50%;filter:blur(90px);pointer-events:none;}
        .sdivider{height:1px;background:linear-gradient(90deg,transparent,rgba(0,196,180,0.22),rgba(255,184,0,0.18),transparent);}
        .vcard{background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:28px;transition:all 0.3s;}
        .vcard:hover{background:rgba(255,255,255,0.06);transform:translateY(-5px);}
        .tcard{background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:26px 20px;text-align:center;transition:all 0.3s;}
        .tcard:hover{background:rgba(255,255,255,0.06);transform:translateY(-5px);}
        .badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
        .badge-teal{background:rgba(0,196,180,0.12);color:#00C4B4;border:1px solid rgba(0,196,180,0.25);}
        .badge-gold{background:rgba(255,184,0,0.12);color:#FFB800;border:1px solid rgba(255,184,0,0.25);}
        .badge-coral{background:rgba(255,87,51,0.12);color:#FF5733;border:1px solid rgba(255,87,51,0.25);}
        .badge-cyan{background:rgba(0,229,255,0.12);color:#00E5FF;border:1px solid rgba(0,229,255,0.25);}
        .btn-p{background:linear-gradient(135deg,#00C4B4,#00E5FF);color:#081120;font-weight:700;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
        .btn-p:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(0,196,180,0.45);}
        .btn-o{background:transparent;color:#F0F6FF;font-weight:600;border:1.5px solid rgba(255,255,255,0.2);cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
        .btn-o:hover{border-color:#00C4B4;background:rgba(0,196,180,0.09);color:#00C4B4;}
        .grid-bg{position:absolute;inset:0;opacity:0.03;background-image:linear-gradient(rgba(0,196,180,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,196,180,1) 1px,transparent 1px);background-size:56px 56px;mask-image:radial-gradient(ellipse at center,black 20%,transparent 75%);}
        .milestone{display:flex;gap:20px;align-items:flex-start;padding:22px 0;border-bottom:1px solid rgba(255,255,255,0.06);}
        .milestone:last-child{border-bottom:none;}
      `}</style>

      <Header />

      {/* ─── HERO ─── */}
      <section style={{ position: 'relative', overflow: 'hidden', padding: '140px 24px 100px', textAlign: 'center' }}>
        <div className="orb" style={{ width: 700, height: 500, top: -200, right: -100, background: 'radial-gradient(circle,rgba(0,196,180,0.15) 0%,transparent 70%)' }} />
        <div className="orb" style={{ width: 550, height: 450, bottom: -120, left: -100, background: 'radial-gradient(circle,rgba(255,87,51,0.11) 0%,transparent 70%)' }} />
        <div className="grid-bg" />
        <div style={{ maxWidth: 720, margin: '0 auto', position: 'relative' }}>
          <span className="badge badge-teal" style={{ marginBottom: 20 }}>About Us</span>
          <h1 style={{ fontSize: 'clamp(36px,6.5vw,70px)', fontWeight: 900, letterSpacing: '-2px', lineHeight: 1.07, marginBottom: 22 }}>
            Building the <span className="shimmer-text">Future</span><br />of Education
          </h1>
          <p style={{ color: 'rgba(240,246,255,0.55)', fontSize: 18, lineHeight: 1.75, maxWidth: 540, margin: '0 auto' }}>
            Founded with a simple mission: make high-quality online examinations accessible to every educational institution in India.
          </p>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── OUR STORY ─── */}
      <section style={{ padding: '88px 24px' }}>
        <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))', gap: 56, alignItems: 'start' }}>
          <div>
            <span className="badge badge-teal" style={{ marginBottom: 20 }}>Our Story</span>
            <h2 style={{ fontSize: 'clamp(28px,4vw,44px)', fontWeight: 800, letterSpacing: '-1px', marginBottom: 28, lineHeight: 1.15 }}>
              From IIT Classroom<br />to 500+ Institutions
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                'In 2022, Dr. Vikram Singh was teaching at IIT when the pandemic forced universities online. Existing solutions were too expensive, too complex, or lacked security features for high-stakes assessments.',
                'With support from colleagues and students, Vikram built the first version of ExamSaaS in just three months — immediately adopted by 12 institutions across Delhi, handling 50,000+ examinations.',
                'Today, ExamSaaS serves 500+ institutions — from small schools to major universities — processing millions of examinations annually across every state in India.',
              ].map((text, i) => (
                <p key={i} style={{ color: 'rgba(240,246,255,0.55)', fontSize: 15, lineHeight: 1.8 }}>{text}</p>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {/* Quote */}
            <div style={{ background: 'linear-gradient(145deg,rgba(0,196,180,0.1),rgba(0,196,180,0.04))', border: '1px solid rgba(0,196,180,0.22)', borderRadius: 24, padding: 34, position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', top: -18, right: -10, fontSize: 100, color: 'rgba(0,196,180,0.07)', fontFamily: 'Georgia,serif', fontWeight: 900, lineHeight: 1, pointerEvents: 'none' }}>"</div>
              <blockquote style={{ fontSize: 18, lineHeight: 1.75, color: 'rgba(240,246,255,0.82)', fontStyle: 'italic', marginBottom: 22, position: 'relative' }}>
                The examination is not just a test of knowledge — it is a pillar of educational integrity. We take that responsibility seriously.
              </blockquote>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 46, height: 46, borderRadius: 13, background: 'linear-gradient(135deg,#00C4B4,#00E5FF)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#081120', fontWeight: 800, fontSize: 14 }}>VS</div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, color: '#F0F6FF' }}>Dr. Vikram Singh</div>
                  <div style={{ color: 'rgba(240,246,255,0.4)', fontSize: 12.5, marginTop: 2 }}>Founder & CEO, ExamSaaS</div>
                </div>
              </div>
            </div>

            {/* Milestones */}
            <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: '8px 24px' }}>
              {milestones.map((m, i) => (
                <div key={i} className="milestone">
                  <div style={{ minWidth: 56, padding: '3px 10px', borderRadius: 8, background: `${m.color}18`, border: `1px solid ${m.color}30`, textAlign: 'center' }}>
                    <span style={{ color: m.color, fontSize: 12, fontWeight: 800 }}>{m.year}</span>
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 14, color: '#F0F6FF', marginBottom: 3 }}>{m.label}</div>
                    <div style={{ color: 'rgba(240,246,255,0.45)', fontSize: 12.5, lineHeight: 1.6 }}>{m.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── VALUES ─── */}
      <section style={{ padding: '88px 24px', background: 'rgba(255,255,255,0.018)' }}>
        <div style={{ maxWidth: 1160, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <span className="badge badge-gold" style={{ marginBottom: 16 }}>Our Values</span>
            <h2 style={{ fontSize: 'clamp(28px,4vw,48px)', fontWeight: 800, letterSpacing: '-1px', lineHeight: 1.1 }}>
              What <span style={{ color: '#FFB800' }}>Drives</span> Us Every Day
            </h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 20 }}>
            {values.map(v => (
              <div key={v.title} className="vcard" style={{ borderTop: `2px solid ${v.color}38` }}>
                <div style={{ fontSize: 28, marginBottom: 16 }}>{v.icon}</div>
                <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 10, color: '#F0F6FF' }}>{v.title}</h3>
                <p style={{ color: 'rgba(240,246,255,0.5)', fontSize: 14, lineHeight: 1.75 }}>{v.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── TEAM ─── */}
      <section style={{ padding: '88px 24px' }}>
        <div style={{ maxWidth: 1160, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 52 }}>
            <span className="badge badge-coral" style={{ marginBottom: 16 }}>Our Team</span>
            <h2 style={{ fontSize: 'clamp(28px,4vw,48px)', fontWeight: 800, letterSpacing: '-1px', lineHeight: 1.1 }}>
              Meet the People Behind <span style={{ color: '#FF5733' }}>ExamSaaS</span>
            </h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 20 }}>
            {team.map(member => (
              <div key={member.name} className="tcard">
                <div style={{ width: 66, height: 66, borderRadius: 18, margin: '0 auto 18px', background: `linear-gradient(135deg,${member.color},${member.color}70)`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#081120', fontWeight: 800, fontSize: 19, boxShadow: `0 8px 32px ${member.color}28` }}>
                  {member.avatar}
                </div>
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4, color: '#F0F6FF' }}>{member.name}</h3>
                <div style={{ color: member.color, fontSize: 13, fontWeight: 600, marginBottom: 10 }}>{member.role}</div>
                <p style={{ color: 'rgba(240,246,255,0.45)', fontSize: 13, lineHeight: 1.65 }}>{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── STATS ─── */}
      <section style={{ padding: '64px 24px', background: 'rgba(255,255,255,0.018)' }}>
        <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 16 }}>
          {[
            { value: '2022', label: 'Founded', color: '#00C4B4' },
            { value: '40+', label: 'Team Members', color: '#FFB800' },
            { value: 'Delhi NCR', label: 'Headquarters', color: '#FF5733' },
            { value: '24/7', label: 'Support', color: '#00E5FF' },
          ].map(stat => (
            <div key={stat.label} style={{ background: `${stat.color}0C`, border: `1px solid ${stat.color}22`, borderRadius: 16, padding: '26px 16px', textAlign: 'center' }}>
              <div style={{ fontSize: 30, fontWeight: 900, color: stat.color, letterSpacing: '-0.5px' }}>{stat.value}</div>
              <div style={{ color: 'rgba(240,246,255,0.42)', fontSize: 12.5, marginTop: 5 }}>{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section style={{ padding: '88px 24px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div className="orb" style={{ width: 600, height: 350, top: '50%', left: '50%', transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle,rgba(0,196,180,0.1) 0%,transparent 70%)' }} />
        <div style={{ position: 'relative', maxWidth: 560, margin: '0 auto' }}>
          <h2 style={{ fontSize: 'clamp(28px,4vw,48px)', fontWeight: 900, letterSpacing: '-1px', marginBottom: 14 }}>Want to Partner With Us?</h2>
          <p style={{ color: 'rgba(240,246,255,0.55)', marginBottom: 34, fontSize: 16, lineHeight: 1.75 }}>Institution, integration partner, or investor — we would love to hear from you.</p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="/register" className="btn-p" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>Get Started</a>
            <a href="mailto:hello@examsaas.com" className="btn-o" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>Contact Us</a>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}