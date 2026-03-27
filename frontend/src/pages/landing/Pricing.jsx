import { useState } from 'react';
import Header from './Header';
import Footer from './Footer';

// ─── Asian Paints T20 World Cup Pre-Match Palette ─────────────────────────────
// Deep Navy #081120 · Vivid Teal #00C4B4 · Electric Cyan #00E5FF
// Coral Burst #FF5733 · Amber Gold #FFB800 · Soft White #F0F6FF
// ─────────────────────────────────────────────────────────────────────────────

const plans = [
  {
    name: 'Starter',
    price: 'Free',
    period: 'forever',
    description: 'Perfect for individual teachers and small classes.',
    features: ['Up to 50 students', '10 exams per month', 'Basic question bank', 'Email support', 'Standard reports'],
    cta: 'Get Started',
    href: '/register',
    accent: '#00C4B4',
    popular: false,
  },
  {
    name: 'Professional',
    price: '₹999',
    period: 'per month',
    description: 'For growing institutions and dedicated departments.',
    features: ['Up to 2,000 students', 'Unlimited exams', 'AI question generation', 'AI proctoring', 'Advanced analytics', 'Priority support', 'Custom certificates', 'Payment integration'],
    cta: 'Start Free Trial',
    href: '/register',
    accent: '#FFB800',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    description: 'For universities and large organizations.',
    features: ['Unlimited everything', 'SSO & SAML', 'Custom integrations', 'Dedicated account manager', 'SLA guarantee', 'On-premise option', 'Custom development', 'Training & onboarding'],
    cta: 'Contact Sales',
    href: 'mailto:hello@examsaas.com',
    accent: '#FF5733',
    popular: false,
  },
];

const faqs = [
  { q: 'Is there a free trial for paid plans?', a: 'Yes, the Professional plan includes a 14-day free trial with full access to all features. No credit card required to start.' },
  { q: 'Can I switch plans at any time?', a: 'Absolutely. Upgrades take effect immediately, and downgrades apply at the next billing cycle with no data loss.' },
  { q: 'How does the student limit work?', a: 'Your student limit is the total number of unique students enrolled across all exams. Inactive students can be removed to free up slots.' },
  { q: 'What payment methods do you accept?', a: 'We accept all major credit/debit cards, UPI, net banking, and bank transfers. All payments are processed securely via Razorpay.' },
  { q: 'Is my data secure?', a: 'Yes. All data is encrypted in transit and at rest. We use MongoDB Atlas with enterprise-grade security and are GDPR compliant.' },
  { q: 'Do you offer annual billing discounts?', a: 'Annual billing saves you up to 20% vs monthly. Contact us for institutional volume discounts on Professional and Enterprise plans.' },
];

const comparison = [
  { feature: 'Students', starter: '50', pro: '2,000', enterprise: 'Unlimited' },
  { feature: 'Monthly Exams', starter: '10', pro: 'Unlimited', enterprise: 'Unlimited' },
  { feature: 'AI Question Generation', starter: false, pro: true, enterprise: true },
  { feature: 'AI Proctoring', starter: false, pro: true, enterprise: true },
  { feature: 'Advanced Analytics', starter: false, pro: true, enterprise: true },
  { feature: 'Custom Certificates', starter: false, pro: true, enterprise: true },
  { feature: 'SSO / SAML', starter: false, pro: false, enterprise: true },
  { feature: 'Dedicated Manager', starter: false, pro: false, enterprise: true },
  { feature: 'SLA Guarantee', starter: false, pro: false, enterprise: true },
  { feature: 'Support', starter: 'Email', pro: 'Priority', enterprise: '24/7 Dedicated' },
];

function Check({ color }) {
  return (
    <svg width="16" height="16" fill="none" stroke={color || '#00C4B4'} strokeWidth="2.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  );
}
function Cross() {
  return (
    <svg width="14" height="14" fill="none" stroke="rgba(240,246,255,0.2)" strokeWidth="2" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

export default function Pricing() {
  const [openFaq, setOpenFaq] = useState(null);
  const [billing, setBilling] = useState('monthly');

  return (
    <div style={{ fontFamily: "'Sora','DM Sans',sans-serif", background: '#081120', minHeight: '100vh', color: '#F0F6FF' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        @keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
        .shimmer-text{background:linear-gradient(90deg,#00C4B4,#00E5FF,#FFB800,#FF5733,#00C4B4);background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shimmer 5s linear infinite;}
        .orb{position:absolute;border-radius:50%;filter:blur(90px);pointer-events:none;}
        .sdivider{height:1px;background:linear-gradient(90deg,transparent,rgba(0,196,180,0.22),rgba(255,184,0,0.18),transparent);}
        .badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
        .badge-teal{background:rgba(0,196,180,0.12);color:#00C4B4;border:1px solid rgba(0,196,180,0.25);}
        .badge-gold{background:rgba(255,184,0,0.12);color:#FFB800;border:1px solid rgba(255,184,0,0.25);}
        .badge-coral{background:rgba(255,87,51,0.12);color:#FF5733;border:1px solid rgba(255,87,51,0.25);}
        .badge-cyan{background:rgba(0,229,255,0.12);color:#00E5FF;border:1px solid rgba(0,229,255,0.25);}
        .btn-p{background:linear-gradient(135deg,#00C4B4,#00E5FF);color:#081120;font-weight:700;border:none;cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
        .btn-p:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(0,196,180,0.45);}
        .btn-o{background:transparent;color:#F0F6FF;font-weight:600;border:1.5px solid rgba(255,255,255,0.2);cursor:pointer;transition:all 0.3s;text-decoration:none;display:inline-flex;align-items:center;gap:8px;font-family:inherit;}
        .btn-o:hover{border-color:#00C4B4;background:rgba(0,196,180,0.09);color:#00C4B4;}
        .plan-card{border-radius:24px;padding:32px;transition:all 0.3s;}
        .plan-card:hover{transform:translateY(-4px);}
        .faq-btn{width:100%;display:flex;justify-content:space-between;align-items:center;padding:18px 22px;background:transparent;border:none;cursor:pointer;color:#F0F6FF;font-family:inherit;text-align:left;transition:background 0.2s;}
        .faq-btn:hover{background:rgba(255,255,255,0.03);}
        .comp-table{width:100%;border-collapse:collapse;}
        .comp-table th,.comp-table td{padding:13px 18px;text-align:center;font-size:13.5px;border-bottom:1px solid rgba(255,255,255,0.05);}
        .comp-table th{font-weight:700;font-size:13px;letter-spacing:0.3px;}
        .comp-table td:first-child,.comp-table th:first-child{text-align:left;color:rgba(240,246,255,0.55);}
        .comp-table tr:last-child td{border-bottom:none;}
        .billing-toggle{display:inline-flex;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:4px;gap:4px;}
        .billing-btn{padding:7px 20px;border-radius:9px;border:none;cursor:pointer;font-family:inherit;font-weight:600;font-size:13px;transition:all 0.25s;}
        .billing-btn.active{background:rgba(0,196,180,0.18);color:#00C4B4;border:1px solid rgba(0,196,180,0.3);}
        .billing-btn.inactive{background:transparent;color:rgba(240,246,255,0.45);}
        .grid-bg{position:absolute;inset:0;opacity:0.028;background-image:linear-gradient(rgba(0,196,180,1) 1px,transparent 1px),linear-gradient(90deg,rgba(0,196,180,1) 1px,transparent 1px);background-size:56px 56px;mask-image:radial-gradient(ellipse at center,black 20%,transparent 75%);}
      `}</style>

      <Header />

      {/* ─── HERO ─── */}
      <section style={{ position: 'relative', overflow: 'hidden', padding: '140px 24px 80px', textAlign: 'center' }}>
        <div className="orb" style={{ width: 700, height: 450, top: -150, left: '50%', transform: 'translateX(-50%)', background: 'radial-gradient(circle,rgba(255,184,0,0.1) 0%,transparent 70%)' }} />
        <div className="orb" style={{ width: 400, height: 400, bottom: -80, right: -60, background: 'radial-gradient(circle,rgba(0,196,180,0.08) 0%,transparent 70%)' }} />
        <div className="grid-bg" />
        <div style={{ maxWidth: 680, margin: '0 auto', position: 'relative' }}>
          <span className="badge badge-gold" style={{ marginBottom: 20 }}>Pricing</span>
          <h1 style={{ fontSize: 'clamp(36px,6.5vw,70px)', fontWeight: 900, letterSpacing: '-2px', lineHeight: 1.07, marginBottom: 22 }}>
            Simple, <span className="shimmer-text">Transparent</span><br />Pricing
          </h1>
          <p style={{ color: 'rgba(240,246,255,0.55)', fontSize: 17, lineHeight: 1.75, maxWidth: 460, margin: '0 auto 32px' }}>
            Start free, scale as you grow. No hidden fees, no surprises. Choose the plan that fits your institution.
          </p>

          {/* Billing toggle */}
          <div className="billing-toggle">
            <button className={`billing-btn ${billing === 'monthly' ? 'active' : 'inactive'}`} onClick={() => setBilling('monthly')}>Monthly</button>
            <button className={`billing-btn ${billing === 'annual' ? 'active' : 'inactive'}`} onClick={() => setBilling('annual')}>
              Annual
              <span style={{ marginLeft: 6, fontSize: 10, background: 'rgba(0,196,180,0.2)', color: '#00C4B4', padding: '2px 6px', borderRadius: 6, fontWeight: 700 }}>-20%</span>
            </button>
          </div>
        </div>
      </section>

      {/* ─── PLANS ─── */}
      <section style={{ padding: '20px 24px 80px' }}>
        <div style={{ maxWidth: 1160, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 20 }}>
          {plans.map(plan => {
            const annualPrice = plan.price === '₹999' ? '₹799' : plan.price;
            const displayPrice = billing === 'annual' ? annualPrice : plan.price;
            return (
              <div key={plan.name} className="plan-card" style={{ position: 'relative', background: plan.popular ? `linear-gradient(145deg,${plan.accent}16,${plan.accent}06)` : 'rgba(255,255,255,0.035)', border: `1px solid ${plan.popular ? plan.accent + '45' : 'rgba(255,255,255,0.08)'}`, boxShadow: plan.popular ? `0 24px 64px ${plan.accent}18` : 'none', transform: plan.popular ? 'scale(1.025)' : undefined }}>
                {plan.popular && (
                  <div style={{ position: 'absolute', top: -14, left: '50%', transform: 'translateX(-50%)', background: plan.accent, color: '#081120', fontSize: 10.5, fontWeight: 800, padding: '4px 16px', borderRadius: 20, letterSpacing: '0.6px', whiteSpace: 'nowrap' }}>
                    MOST POPULAR
                  </div>
                )}

                <div style={{ marginBottom: 28 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 12, background: `${plan.accent}20`, border: `1px solid ${plan.accent}30`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16 }}>
                    <div style={{ width: 12, height: 12, borderRadius: '50%', background: plan.accent, boxShadow: `0 0 12px ${plan.accent}80` }} />
                  </div>
                  <h3 style={{ fontSize: 20, fontWeight: 800, marginBottom: 8, color: '#F0F6FF' }}>{plan.name}</h3>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 8 }}>
                    <span style={{ fontSize: 44, fontWeight: 900, color: plan.accent, letterSpacing: '-2px', lineHeight: 1 }}>{displayPrice}</span>
                    <span style={{ color: 'rgba(240,246,255,0.38)', fontSize: 13.5 }}>/ {plan.period}</span>
                  </div>
                  {billing === 'annual' && plan.price === '₹999' && (
                    <div style={{ fontSize: 12, color: 'rgba(240,246,255,0.4)', marginBottom: 4 }}>
                      <span style={{ textDecoration: 'line-through', marginRight: 6 }}>₹999/mo</span>
                      <span style={{ color: '#00C4B4' }}>Save ₹2,400/year</span>
                    </div>
                  )}
                  <p style={{ color: 'rgba(240,246,255,0.48)', fontSize: 13.5 }}>{plan.description}</p>
                </div>

                <ul style={{ listStyle: 'none', marginBottom: 32, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {plan.features.map(feature => (
                    <li key={feature} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 20, height: 20, borderRadius: '50%', flexShrink: 0, background: `${plan.accent}18`, border: `1px solid ${plan.accent}35`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Check color={plan.accent} />
                      </div>
                      <span style={{ color: 'rgba(240,246,255,0.68)', fontSize: 13.5 }}>{feature}</span>
                    </li>
                  ))}
                </ul>

                <a href={plan.href} style={{ display: 'block', textAlign: 'center', padding: '14px', borderRadius: 14, fontWeight: 700, fontSize: 15, fontFamily: 'inherit', textDecoration: 'none', transition: 'all 0.3s', background: plan.popular ? `linear-gradient(135deg,${plan.accent},${plan.accent}cc)` : 'rgba(255,255,255,0.06)', color: plan.popular ? '#081120' : '#F0F6FF', border: plan.popular ? 'none' : `1px solid rgba(255,255,255,0.12)` }}>
                  {plan.cta}
                </a>
              </div>
            );
          })}
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── COMPARISON TABLE ─── */}
      <section style={{ padding: '80px 24px' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 44 }}>
            <span className="badge badge-cyan" style={{ marginBottom: 16 }}>Compare Plans</span>
            <h2 style={{ fontSize: 'clamp(24px,3.5vw,40px)', fontWeight: 800, letterSpacing: '-0.5px' }}>Feature Comparison</h2>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, overflow: 'hidden' }}>
            <table className="comp-table">
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.04)' }}>
                  <th style={{ color: 'rgba(240,246,255,0.55)', paddingTop: 20, paddingBottom: 20 }}>Feature</th>
                  <th style={{ color: '#00C4B4' }}>Starter</th>
                  <th style={{ color: '#FFB800' }}>Professional</th>
                  <th style={{ color: '#FF5733' }}>Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row, i) => (
                  <tr key={i} style={{ background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.015)' }}>
                    <td style={{ fontWeight: 500 }}>{row.feature}</td>
                    {['starter', 'pro', 'enterprise'].map(tier => (
                      <td key={tier} style={{ textAlign: 'center' }}>
                        {typeof row[tier] === 'boolean'
                          ? (row[tier] ? <div style={{ display: 'flex', justifyContent: 'center' }}><Check color={tier === 'starter' ? '#00C4B4' : tier === 'pro' ? '#FFB800' : '#FF5733'} /></div> : <div style={{ display: 'flex', justifyContent: 'center' }}><Cross /></div>)
                          : <span style={{ color: tier === 'starter' ? '#00C4B4' : tier === 'pro' ? '#FFB800' : '#FF5733', fontWeight: 600, fontSize: 13 }}>{row[tier]}</span>
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div className="sdivider" />

      {/* ─── FAQ ─── */}
      <section style={{ padding: '80px 24px', background: 'rgba(255,255,255,0.018)' }}>
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <span className="badge badge-coral" style={{ marginBottom: 16 }}>FAQ</span>
            <h2 style={{ fontSize: 'clamp(24px,3.5vw,40px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 10 }}>Frequently Asked Questions</h2>
            <p style={{ color: 'rgba(240,246,255,0.45)', fontSize: 16 }}>Everything you need to know about our pricing.</p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {faqs.map((faq, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.035)', border: `1px solid ${openFaq === i ? 'rgba(0,196,180,0.28)' : 'rgba(255,255,255,0.07)'}`, borderRadius: 16, overflow: 'hidden', transition: 'border-color 0.3s' }}>
                <button className="faq-btn" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                  <span style={{ fontWeight: 600, fontSize: 14.5, color: '#F0F6FF' }}>{faq.q}</span>
                  <svg style={{ flexShrink: 0, transition: 'transform 0.3s', transform: openFaq === i ? 'rotate(180deg)' : 'rotate(0)' }} width="18" height="18" fill="none" stroke="rgba(240,246,255,0.4)" strokeWidth="2" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {openFaq === i && (
                  <div style={{ padding: '0 22px 18px' }}>
                    <p style={{ color: 'rgba(240,246,255,0.55)', fontSize: 14, lineHeight: 1.75 }}>{faq.a}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CTA ─── */}
      <section style={{ padding: '88px 24px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div className="orb" style={{ width: 600, height: 350, top: '50%', left: '50%', transform: 'translate(-50%,-50%)', background: 'radial-gradient(circle,rgba(0,196,180,0.1) 0%,transparent 70%)' }} />
        <div style={{ position: 'relative' }}>
          <h2 style={{ fontSize: 'clamp(28px,4vw,48px)', fontWeight: 900, letterSpacing: '-1px', marginBottom: 14 }}>Still Have Questions?</h2>
          <p style={{ color: 'rgba(240,246,255,0.55)', marginBottom: 34, fontSize: 17, lineHeight: 1.7 }}>Our team is here to help. We'll get back to you within 24 hours.</p>
          <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="/register" className="btn-p" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>Start Free Trial</a>
            <a href="mailto:hello@examsaas.com" className="btn-o" style={{ padding: '14px 32px', borderRadius: 14, fontSize: 16 }}>Talk to Sales</a>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}