document.addEventListener('DOMContentLoaded', () => {
    const reveals = document.querySelectorAll('.reveal');
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.15
    };
  
    const revealOnScroll = (entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
        }
      });
    };
  
    const observer = new IntersectionObserver(revealOnScroll, observerOptions);
    reveals.forEach(el => observer.observe(el));
  });
  