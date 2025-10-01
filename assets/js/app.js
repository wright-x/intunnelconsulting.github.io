import { caseStudies, services } from './data.js';

// Configuration
let config = {};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
  // Load configuration
  await loadConfig();
  
  // Initialize components
  initSmoothScroll();
  initNavigation();
  initMobileMenu();
  initAnimations();
  initForm();
  populateServices();
  populateCaseStudies();
  initIntersectionObserver();
});

// Load configuration from config.json
async function loadConfig() {
  try {
    const response = await fetch('./config.json');
    config = await response.json();
  } catch (error) {
    console.error('Failed to load config:', error);
    // Fallback configuration
    config = {
      formEndpoint: 'https://formspree.io/f/YOUR_FORM_ID',
      calendly: 'https://calendly.com/your-link'
    };
  }
}

// Initialize smooth scrolling with Lenis
function initSmoothScroll() {
  const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    direction: 'vertical',
    gestureDirection: 'vertical',
    smooth: true,
    mouseMultiplier: 1,
    smoothTouch: false,
    touchMultiplier: 2,
    infinite: false,
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }

  requestAnimationFrame(raf);

  // Update header opacity on scroll
  lenis.on('scroll', ({ scroll }) => {
    const header = document.getElementById('header');
    if (scroll > 24) {
      header.style.opacity = '0.95';
    } else {
      header.style.opacity = '1';
    }
  });
}

// Initialize navigation with active state tracking
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');
  
  // Smooth scroll for navigation links
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      
      if (targetSection) {
        targetSection.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

// Initialize mobile menu
function initMobileMenu() {
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
    
    // Close mobile menu when clicking on a link
    const mobileLinks = mobileMenu.querySelectorAll('.nav-link');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });
  }
}

// Initialize GSAP animations
function initAnimations() {
  // Respect reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  if (prefersReducedMotion) {
    return;
  }

  // Hero section animation
  gsap.from('.hero h1', {
    opacity: 0,
    y: 50,
    duration: 1,
    ease: 'power2.out',
    delay: 0.2
  });

  gsap.from('.hero p', {
    opacity: 0,
    y: 30,
    duration: 0.8,
    ease: 'power2.out',
    delay: 0.4
  });

  gsap.from('.proof-chips', {
    opacity: 0,
    y: 20,
    duration: 0.8,
    ease: 'power2.out',
    delay: 0.6
  });

  // Section reveal animations
  gsap.registerPlugin(ScrollTrigger);
  
  gsap.utils.toArray('.value-card, .service-card, .process-step, .case-study-card, .pricing-card').forEach((element, index) => {
    gsap.from(element, {
      opacity: 0,
      y: 30,
      duration: 0.6,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: element,
        start: 'top 80%',
        toggleActions: 'play none none reverse'
      },
      delay: index * 0.1
    });
  });
}

// Initialize intersection observer for navigation active state
function initIntersectionObserver() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');
  
  const observerOptions = {
    rootMargin: '-50% 0px -50% 0px',
    threshold: 0
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const sectionId = entry.target.id;
        
        // Update active nav link
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }, observerOptions);
  
  sections.forEach(section => {
    observer.observe(section);
  });
}

// Populate services section
function populateServices() {
  const servicesGrid = document.getElementById('services-grid');
  if (!servicesGrid) return;
  
  servicesGrid.innerHTML = services.map(service => `
    <div class="service-card">
      <h3 class="text-lg font-semibold text-ink mb-3">${service.title}</h3>
      <p class="text-neutral-600 mb-4">${service.description}</p>
      <div class="text-sm text-primary font-medium">${service.outcome}</div>
    </div>
  `).join('');
}

// Populate case studies section
function populateCaseStudies() {
  const caseStudiesGrid = document.getElementById('case-studies-grid');
  if (!caseStudiesGrid) return;
  
  caseStudiesGrid.innerHTML = caseStudies.map(study => `
    <div class="case-study-card">
      <details>
        <summary class="case-study-header">
          <div>
            <h3 class="text-lg font-semibold text-ink mb-2">${study.title}</h3>
            <div class="case-study-badges">
              ${study.badges.map(badge => `<span class="case-study-badge">${badge}</span>`).join('')}
            </div>
          </div>
        </summary>
        <div class="case-study-content">
          <div class="mb-4">
            <h4 class="font-semibold text-ink mb-2">Challenge:</h4>
            <p class="text-neutral-600">${study.challenge}</p>
          </div>
          
          <div class="mb-4">
            <h4 class="font-semibold text-ink mb-2">Solution:</h4>
            <ul class="text-neutral-600 space-y-1">
              ${study.solution.map(item => `<li>• ${item}</li>`).join('')}
            </ul>
          </div>
          
          <div>
            <h4 class="font-semibold text-ink mb-2">Results:</h4>
            <ul class="text-neutral-600 space-y-1">
              ${study.results.map(result => `<li>• ${result}</li>`).join('')}
            </ul>
          </div>
        </div>
      </details>
    </div>
  `).join('');
  
  // Add animation to case study details
  const detailsElements = document.querySelectorAll('.case-study-card details');
  detailsElements.forEach(details => {
    details.addEventListener('toggle', () => {
      if (details.open) {
        const content = details.querySelector('.case-study-content');
        gsap.from(content, {
          opacity: 0,
          y: 20,
          duration: 0.3,
          ease: 'power2.out'
        });
      }
    });
  });
}

// Initialize contact form
function initForm() {
  const form = document.getElementById('contact-form');
  const successMessage = document.getElementById('form-success');
  const calendlyLink = document.getElementById('calendly-link');
  
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitButton = form.querySelector('button[type="submit"]');
    const submitText = submitButton.querySelector('.submit-text');
    const submitLoading = submitButton.querySelector('.submit-loading');
    
    // Show loading state
    form.classList.add('form-submitting');
    submitButton.disabled = true;
    
    try {
      const formData = new FormData(form);
      
      // Add honeypot field for spam protection
      formData.append('_subject', 'New contact form submission from Intunnel Consulting');
      formData.append('_replyto', formData.get('email'));
      
      const response = await fetch(config.formEndpoint, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });
      
      if (response.ok) {
        // Show success message
        form.style.display = 'none';
        successMessage.classList.remove('hidden');
        
        // Set Calendly link
        if (calendlyLink && config.calendly) {
          calendlyLink.href = config.calendly;
        }
        
        // Track conversion (if analytics is available)
        if (typeof gtag !== 'undefined') {
          gtag('event', 'form_submit', {
            event_category: 'engagement',
            event_label: 'contact_form'
          });
        }
      } else {
        throw new Error('Form submission failed');
      }
    } catch (error) {
      console.error('Form submission error:', error);
      alert('There was an error submitting your form. Please try again or contact us directly.');
    } finally {
      // Reset form state
      form.classList.remove('form-submitting');
      submitButton.disabled = false;
    }
  });
}

// Utility function to debounce function calls
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Handle window resize
window.addEventListener('resize', debounce(() => {
  // Refresh any animations that depend on viewport size
  if (typeof ScrollTrigger !== 'undefined') {
    ScrollTrigger.refresh();
  }
}, 250));

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // Resume animations when page becomes visible
    if (typeof gsap !== 'undefined') {
      gsap.globalTimeline.play();
    }
  } else {
    // Pause animations when page becomes hidden
    if (typeof gsap !== 'undefined') {
      gsap.globalTimeline.pause();
    }
  }
});

// Error handling for missing dependencies
window.addEventListener('error', (event) => {
  if (event.message.includes('Lenis') || event.message.includes('gsap')) {
    console.warn('Some animations may not work due to missing dependencies. The site will still function normally.');
  }
});

// Export functions for potential external use
window.IntunnelConsulting = {
  initSmoothScroll,
  initNavigation,
  initMobileMenu,
  initAnimations,
  initForm,
  populateServices,
  populateCaseStudies
};
