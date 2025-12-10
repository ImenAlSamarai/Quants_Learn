import { useNavigate } from 'react-router-dom';

const LandingPageNew = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: '100vh',
      background: '#FAF9F6',
      padding: '3rem 2rem'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        width: '100%'
      }}>

        {/* Hero Section */}
        <div style={{
          textAlign: 'center',
          marginBottom: '4rem'
        }}>
          <h1 style={{
            fontSize: '3rem',
            fontWeight: '800',
            color: '#1A1A1A',
            marginBottom: '1.5rem',
            lineHeight: '1.2'
          }}>
            The Ethical Hiring Platform
          </h1>

          <p style={{
            fontSize: '1.2rem',
            color: '#6B6B6B',
            maxWidth: '900px',
            margin: '0 auto 3rem',
            lineHeight: '1.8'
          }}>
            Finding signal in the noise of AI-assisted hiring is our mission. We empower candidates to
            target their dream roles and prepare effectively using expert knowledge delivered in bite-sized
            lessons, ensuring they're truly ready for technical interviews. For recruiters, we provide a
            window into genuine technical capabilities beyond AI-polished CVs—helping you identify and hire
            candidates whose verified learning progress demonstrates real interview readiness and mastery
            of the skills your role demands.
          </p>

          {/* Value Props */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2rem',
            marginBottom: '3rem'
          }}>
            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid #E5E5E0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
              textAlign: 'left'
            }}>
              <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '1rem' }}>🎯</span>
              <h3 style={{ fontSize: '1.5rem', color: '#1A1A1A', marginBottom: '0.75rem', fontWeight: '700' }}>
                For Candidates
              </h3>
              <p style={{ color: '#6B6B6B', lineHeight: '1.7', fontSize: '1rem' }}>
                Target your dream role with precision. Master the exact skills employers need through
                expert-curated lessons. Build genuine expertise that shines in technical interviews,
                not just on paper.
              </p>
            </div>

            <div style={{
              background: 'white',
              padding: '2rem',
              borderRadius: '12px',
              border: '1px solid #E5E5E0',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
              textAlign: 'left'
            }}>
              <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '1rem' }}>✓</span>
              <h3 style={{ fontSize: '1.5rem', color: '#1A1A1A', marginBottom: '0.75rem', fontWeight: '700' }}>
                For Recruiters
              </h3>
              <p style={{ color: '#6B6B6B', lineHeight: '1.7', fontSize: '1rem' }}>
                Look beyond AI-polished CVs. Assess real technical readiness through verified learning
                progress. Identify candidates who've invested in mastering the skills your role demands.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div style={{
          background: 'white',
          padding: '3rem',
          borderRadius: '16px',
          border: '1px solid #E5E5E0',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
          textAlign: 'center',
          marginBottom: '3rem'
        }}>
          <h2 style={{
            fontSize: '2rem',
            color: '#1A1A1A',
            marginBottom: '0.5rem',
            fontWeight: '700'
          }}>
            Get Started
          </h2>
          <p style={{
            color: '#6B6B6B',
            fontSize: '1.1rem',
            marginBottom: '2.5rem'
          }}>
            Choose your path to authentic hiring
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '2rem',
            marginBottom: '2rem'
          }}>
            <button
              onClick={() => navigate('/register?role=candidate')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
                padding: '2rem',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                textAlign: 'left',
                background: '#C9A96E',
                color: 'white',
                transition: 'all 0.3s ease'
              }}
            >
              <span style={{ fontSize: '3rem', flexShrink: '0' }}>🎓</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: '1' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: '700', display: 'block' }}>
                  I am a Candidate
                </span>
                <span style={{ fontSize: '0.95rem', opacity: '0.9', display: 'block' }}>
                  Prepare for your dream role
                </span>
              </div>
            </button>

            <button
              onClick={() => navigate('/register?role=recruiter')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1.5rem',
                padding: '2rem',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                fontFamily: 'inherit',
                textAlign: 'left',
                background: '#7BA591',
                color: 'white',
                transition: 'all 0.3s ease'
              }}
            >
              <span style={{ fontSize: '3rem', flexShrink: '0' }}>💼</span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: '1' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: '700', display: 'block' }}>
                  I am a Recruiter
                </span>
                <span style={{ fontSize: '0.95rem', opacity: '0.9', display: 'block' }}>
                  Find verified talent
                </span>
              </div>
            </button>
          </div>

          <div style={{
            marginTop: '2rem',
            paddingTop: '2rem',
            borderTop: '1px solid #E5E5E0'
          }}>
            <p style={{ color: '#6B6B6B', fontSize: '1rem' }}>
              Already registered?{' '}
              <button
                onClick={() => navigate('/login')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#C9A96E',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  fontFamily: 'inherit',
                  fontSize: 'inherit',
                  padding: '0'
                }}
              >
                Sign in here
              </button>
            </p>
          </div>
        </div>

        {/* Trust Indicators */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '3rem',
          flexWrap: 'wrap'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#6B6B6B',
            fontSize: '1rem'
          }}>
            <span style={{ fontSize: '1.5rem' }}>🔒</span>
            <span style={{ fontWeight: '500' }}>Privacy-first design</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#6B6B6B',
            fontSize: '1rem'
          }}>
            <span style={{ fontSize: '1.5rem' }}>📚</span>
            <span style={{ fontWeight: '500' }}>Expert-curated content</span>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            color: '#6B6B6B',
            fontSize: '1rem'
          }}>
            <span style={{ fontSize: '1.5rem' }}>⚡</span>
            <span style={{ fontWeight: '500' }}>Job-specific learning paths</span>
          </div>
        </div>

      </div>
    </div>
  );
};

export default LandingPageNew;
