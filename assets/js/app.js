import { services } from './data.js';

// Configuration
let config = {};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
  // Load configuration
  await loadConfig();
  
  // Initialize components
  initSmoothScroll();
  initScrollSpy();
  initMobileMenu();
  initAnimations();
  initForm();
  populateServices();
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

  return lenis;
}

// Initialize scroll spy for navigation
function initScrollSpy() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');
  
  // Smooth scroll for navigation links
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const targetSection = document.getElementById(targetId);
      
      if (targetSection) {
        const headerHeight = 80; // Account for sticky header
        const targetPosition = targetSection.offsetTop - headerHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
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
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenu.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
        mobileMenu.classList.add('hidden');
      }
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

  // Register ScrollTrigger
  gsap.registerPlugin(ScrollTrigger);

  // Hero section animation
  gsap.timeline()
    .from('.hero h1', {
      opacity: 0,
      y: 50,
      duration: 1,
      ease: 'power2.out'
    })
    .from('.hero p', {
      opacity: 0,
      y: 30,
      duration: 0.8,
      ease: 'power2.out'
    }, '-=0.5')
    .from('.hero .grid', {
      opacity: 0,
      y: 20,
      duration: 0.6,
      ease: 'power2.out'
    }, '-=0.3');

  // Section reveal animations
  gsap.utils.toArray('.focus-card, .service-card, .package-card, .logo-item').forEach((element, index) => {
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

  // Staggered logo animation
  gsap.from('.logo-item', {
    opacity: 0,
    y: 20,
    duration: 0.4,
    ease: 'power2.out',
    stagger: 0.1,
    scrollTrigger: {
      trigger: '.logo-wall',
      start: 'top 80%',
      toggleActions: 'play none none reverse'
    }
  });

  // Parallax effect for hero background
  gsap.to('.hero::before', {
    y: -50,
    ease: 'none',
    scrollTrigger: {
      trigger: '.hero',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  });
}

// Initialize intersection observer for navigation active state
function initIntersectionObserver() {
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');
  
  const observerOptions = {
    rootMargin: '-20% 0px -60% 0px',
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
  
  const serviceIcons = [
    'M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h3a1 1 0 011 1v14a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1h3zM9 4h6V3H9v1z',
    'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
    'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z',
    'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
    'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z',
    'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z'
  ];
  
  servicesGrid.innerHTML = services.map((service, index) => `
    <div class="service-card">
      <div class="service-icon">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${serviceIcons[index] || serviceIcons[0]}"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold text-ink mb-3">${service.title}</h3>
      <p class="text-neutral-600 mb-4">${service.description}</p>
      <div class="text-sm text-primary font-medium">${service.outcome}</div>
    </div>
  `).join('');
}

// Initialize contact form
function initForm() {
  const form = document.getElementById('contact-form');
  const successMessage = document.getElementById('form-success');
  
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
        // Show success message with animation
        form.style.display = 'none';
        successMessage.classList.remove('hidden');
        
        // Animate success message
        gsap.from(successMessage, {
          opacity: 0,
          y: 20,
          duration: 0.6,
          ease: 'power2.out'
        });
        
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
  initScrollSpy,
  initMobileMenu,
  initAnimations,
  initForm,
  populateServices
};